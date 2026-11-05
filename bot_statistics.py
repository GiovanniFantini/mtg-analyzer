"""Offline empirical Draft quality. Observations stay separate from reviews.

Only licensed public game counts are eligible. Utility is a standardized,
regularized within-event ordering, never a card's probability of winning.
"""
import math
from urllib.parse import urlsplit

METHOD = 'public-gih-editorial-prior-context-v2'
MIN_GAMES = 100
MIN_CARDS = 8


def observation(row):
    values = row.get('metrics', {})
    n, won, rate = (values.get(k) for k in ('games', 'wins', 'inHandWinRate'))
    if type(n) is not int or type(won) is not int or n <= 0 or not 0 <= won <= n:
        return None
    if type(rate) not in (int, float) or not math.isfinite(rate) or abs(rate - 100 * won / n) > 1e-6:
        return None
    return n, won, won / n


def fit(rows):
    samples = [value for row in rows if (value := observation(row)) and value[0] >= MIN_GAMES]
    if len(samples) < MIN_CARDS:
        return None
    weights = [min(n, 4000) for n, _, _ in samples]
    total = sum(weights)
    center = sum(w * p for w, (_, _, p) in zip(weights, samples)) / total
    variance = sum(w * ((p - center) ** 2 - p * (1 - p) / n)
                   for w, (n, _, p) in zip(weights, samples)) / total
    variance = max(.0001, min(.01, variance))
    strength = max(50, min(5000, center * (1 - center) / variance - 1))
    return {'center': center, 'scale': math.sqrt(variance), 'priorGames': strength}


def utility(probability, model):
    return max(0, min(5, 2.5 + (probability - model['center']) / model['scale']))


def payload(statistics, cards, active, event):
    eligible = {c.get('catalogId') or c['id']: c for c in cards if c['id'] in active and not c.get('basic')}
    reference = event.get('botPolicy', {}).get('statisticsReference', {})
    family = {'BO1': 'PickTwoDraft'} if event.get('picksPerTurn') == 2 else {'BO1': 'PremierDraft', 'BO3': 'TradDraft'}
    bound = (event.get('kind') == 'draft' and reference.get('product') == event.get('product')
             and reference.get('purpose') == 'card-quality-prior' and reference.get('population') == 'MTG Arena')
    expected = {value: mode for mode, value in reference.get('events', {}).items() if bound and family.get(mode) == value}
    candidates = {}
    for source_id, snapshot in (statistics.get('draft', {}).get('externalSources') or {}).items():
        derivation = snapshot.get('derivation', {})
        source_event = snapshot.get('filters', {}).get('event')
        if source_event not in expected or snapshot.get('rateUnit') != 'percent':
            continue
        if source_event == 'TradDraft':
            if not snapshot.get('gameOne'):
                continue
            snapshot = {**snapshot, **snapshot['gameOne'], 'colorContexts': snapshot['gameOne'].get('colorContexts', {}), 'cohort': 'game-one'}
        if (derivation.get('license') != 'CC BY 4.0'
                or urlsplit(derivation.get('datasetUrl', '')).netloc != '17lands-public.s3.amazonaws.com'
                or any(snapshot.get('metrics', {}).get(key, {}).get('status') != 'public'
                       for key in ('inHandWinRate', 'games', 'wins'))):
            continue
        rows = [row for row in snapshot.get('cards', []) if row.get('catalogId') in eligible]
        model = fit(rows)
        if model is None:
            continue
        mode = expected[source_event]
        priority = (sum((observation(row) or (0,))[0] for row in rows), source_id)
        if mode not in candidates or priority > candidates[mode][0]:
            candidates[mode] = priority, source_id, snapshot, rows, model
    modes = {}
    for mode, (_, source_id, snapshot, rows, model) in candidates.items():
        # Reviews are an ordinal prior, not extra wins. On sparse observations
        # a known strong card must not collapse to the average card merely
        # because the mode has few games. Large samples override this prior.
        review_rows = [(eligible[row['catalogId']].get('score'), min(sample[0], 4000))
                       for row in rows if (sample := observation(row)) and sample[0] >= MIN_GAMES
                       and type(eligible[row['catalogId']].get('score')) in (int, float)]
        weight = sum(w for _, w in review_rows)
        review_center = sum(score * w for score, w in review_rows) / weight if weight else 2.5
        review_scale = max(.25, math.sqrt(sum(w * (score - review_center) ** 2 for score, w in review_rows) / weight)) if weight else 1
        fallback = {'slope': 1 / review_scale, 'intercept': 2.5 - review_center / review_scale, 'cards': len(review_rows)}
        def prior(card):
            score = card.get('score')
            value = max(0, min(5, fallback['intercept'] + fallback['slope'] * score)) if type(score) in (int, float) else 2.5
            return max(.05, min(.95, model['center'] + (value - 2.5) * model['scale']))
        values = {}
        for row in rows:
            sample = observation(row)
            if not sample or sample[0] < MIN_GAMES:
                continue
            n, wins, raw = sample
            prior_rate = prior(eligible[row['catalogId']])
            posterior = (wins + prior_rate * model['priorGames']) / (n + model['priorGames'])
            values[row['catalogId']] = {'games': n, 'wins': wins, 'rate': 100 * raw,
                                       'estimate': 100 * posterior, 'priorRate': 100 * prior_rate, 'reliability': n / (n + model['priorGames']),
                                       'utility': utility(posterior, model), 'contexts': {}}
        # Global and color observations overlap. This is a bounded descriptive
        # correction, not two independent samples or a causal synergy estimate.
        for lane, context in sorted(snapshot.get('colorContexts', {}).items()):
            context_rows = [row for row in context.get('cards', []) if row.get('catalogId') in eligible]
            context_model = fit(context_rows)
            if context_model is None:
                continue
            for row in context_rows:
                sample, base = observation(row), values.get(row.get('catalogId'))
                if not sample or sample[0] < MIN_GAMES or base is None:
                    continue
                n, wins, raw = sample
                weight = min(.5, n / (n + 4 * model['priorGames']))
                difference = (raw - context_model['center']) - (base['rate'] / 100 - model['center'])
                adjustment = max(-1, min(1, weight * difference / model['scale']))
                base['contexts'][lane] = {'games': n, 'wins': wins, 'rate': 100 * raw, 'weight': weight,
                                          'adjustment': adjustment, 'utility': max(0, min(5, base['utility'] + adjustment))}
        active_cards = [c for c in cards if c['id'] in active and not c.get('basic')]
        covered = sum((c.get('catalogId') or c['id']) in values for c in active_cards)
        modes[mode] = {'event': snapshot['filters']['event'], 'sourceId': source_id,
                       'provider': snapshot['provider'], 'url': snapshot['url'], 'retrieved': snapshot['retrieved'],
                       'asOf': snapshot.get('derivation', {}).get('lastModified'),
                       'datasetUrl': snapshot['derivation']['datasetUrl'], 'datasetSha256': snapshot['derivation'].get('sha256'),
                       'filters': snapshot['filters'], 'cohort': snapshot.get('cohort', 'all-games'), 'model': model,
                       'reviewPriorModel': {'center': review_center, 'scale': review_scale}, 'fallbackModel': fallback, 'cards': values,
                       'coverage': {'activeNonbasicPrintings': len(active_cards), 'withEvidence': covered,
                                    'editorialFallback': len(active_cards) - covered}}
    return {'method': METHOD, 'minGames': MIN_GAMES, 'minComparableCards': MIN_CARDS,
            'reference': reference, 'referenceBound': bound,
            'matching': {c['id']: c.get('catalogId') or c['id'] for c in cards if c['id'] in active and not c.get('basic')},
            'available': bool(modes), 'modes': modes,
            'limitations': ['Utility standardizzata 0–5, distinta dal voto editoriale e dalla probabilità di vittoria.',
                            'GIH osservata: restano selezione dei mazzi, abilità dei giocatori e durata delle partite.',
                            'Contesti di colore regolarizzati e centrati; non misurano sinergie causali fra carte.',
                            'Nessuna trasposizione fra BO1, BO3, Quick, Sealed e Pick-Two.']}


def semantic(empirical):
    """Only functional numbers and matching affect replay compatibility."""
    return {'method': empirical['method'], 'minGames': empirical['minGames'],
            'minComparableCards': empirical['minComparableCards'], 'matching': empirical['matching'],
            'reference': {key: empirical['reference'].get(key) for key in ('product', 'purpose', 'events')},
            'modes': {mode: {key: source[key] for key in ('event', 'cohort', 'model', 'reviewPriorModel', 'fallbackModel', 'cards')}
                      for mode, source in empirical['modes'].items()}}
