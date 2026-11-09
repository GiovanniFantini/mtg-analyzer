"""Validation of optional, independent statistical provider snapshots."""
import math
from datetime import date
from urllib.parse import urlsplit


def validate_external_statistics(statistics, catalog):
    for kind in ('draft','sealed'):
        validate_provider_snapshots(statistics.get(kind) or {},catalog,kind)


def validate_provider_snapshots(statistics, catalog, kind):
    sources = statistics.get('externalSources', {})
    def fail(message):
        raise ValueError('statistics.'+kind+'.externalSources: ' + message)
    if not isinstance(sources, dict):
        fail('deve essere un oggetto')
    by_id = {card['id']: card for card in catalog}
    for key, snapshot in sources.items():
        if not isinstance(snapshot, dict) or snapshot.get('schemaVersion') != 1:
            fail(key + ': versione snapshot non supportata')
        for field in ('provider', 'url', 'retrieved', 'rateUnit', 'filters', 'metrics', 'cards'):
            if field not in snapshot:
                fail(key + ': manca ' + field)
        try:
            date.fromisoformat(snapshot['retrieved'])
        except (ValueError, TypeError):
            fail(key + ': data non valida')
        if not isinstance(snapshot['provider'], str) or not snapshot['provider'].strip():
            fail(key + ': provider non valido')
        if not isinstance(snapshot['url'], str) or urlsplit(snapshot['url']).scheme != 'https':
            fail(key + ': URL non valido')
        if snapshot['rateUnit'] != 'percent' or not isinstance(snapshot['filters'], dict):
            fail(key + ': unità o filtri non validi')
        eligibility = snapshot.get('assessmentEligibility')
        if eligibility is not None and (not isinstance(eligibility, dict)
                or eligibility.get('status') not in ('eligible', 'experimental_only')
                or not isinstance(eligibility.get('reason'), str) or not eligibility['reason'].strip()):
            fail(key + ': idoneità alle valutazioni non valida')
        metrics = snapshot['metrics']
        if not isinstance(metrics, dict) or not metrics:
            fail(key + ': metriche mancanti')
        for metric, definition in metrics.items():
            if not isinstance(definition, dict) or definition.get('status') not in ('public', 'locked', 'suspect') or definition.get('unit') not in ('percent', 'pick', 'games') or not isinstance(definition.get('label'), str):
                fail(key + ': definizione metrica non valida: ' + metric)
        if not isinstance(snapshot['cards'], list):
            fail(key + ': cards non valido')
        seen = set()
        for row in snapshot['cards']:
            if not isinstance(row, dict) or row.get('catalogId') not in by_id:
                fail(key + ': carta sconosciuta')
            identity = row['catalogId']
            if identity in seen:
                fail(key + ': carta duplicata: ' + identity)
            seen.add(identity)
            card = by_id[identity]
            if row.get('name') not in (card['name'], card.get('full')):
                fail(key + ': nome incoerente: ' + identity)
            values = row.get('metrics')
            if not isinstance(values, dict) or set(values) != set(metrics):
                fail(key + ': metriche incomplete: ' + identity)
            for metric, value in values.items():
                definition = metrics[metric]
                if definition['status'] == 'locked' and value is not None:
                    fail(key + ': metrica bloccata valorizzata: ' + metric)
                if value is None:
                    continue
                if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
                    fail(key + ': valore non valido: ' + metric)
                if definition['unit'] == 'percent' and value > 100:
                    fail(key + ': percentuale fuori scala: ' + metric)
                if definition['unit'] == 'games' and type(value) is not int:
                    fail(key + ': numero partite non intero')
            n, wins = values.get('games'), values.get('wins')
            if type(n) is int and type(wins) is int and wins > n:
                fail(key + ': vittorie superiori al campione')
            limit = snapshot.get('games', snapshot.get('derivation', {}).get('games'))
            if type(n) is int and type(limit) is int and n > limit:
                fail(key + ': campione carta superiore alle partite della coorte')
        if not isinstance(snapshot.get('colorContexts', {}), dict):
            fail(key + ': contesti colori non validi')
        for lane, context in snapshot.get('colorContexts', {}).items():
            if (not isinstance(lane, str) or not lane or any(c not in 'WUBRG' for c in lane)
                    or len(set(lane)) != len(lane) or not isinstance(context, dict)
                    or type(context.get('games')) is not int or type(context.get('wins')) is not int
                    or not 0 <= context['wins'] <= context['games'] or not isinstance(context.get('cards'), list)):
                fail(key + ': contesto colori non valido')
            nested = {**snapshot, **context}
            nested.pop('colorContexts', None)
            nested.pop('gameOne', None)
            validate_provider_snapshots({'externalSources': {key + ':' + lane: nested}}, catalog, kind)
        if 'gameOne' in snapshot:
            first = snapshot['gameOne']
            if (not isinstance(first, dict) or type(first.get('games')) is not int or type(first.get('wins')) is not int
                    or not 0 <= first['wins'] <= first['games'] or not isinstance(first.get('cards'), list)):
                fail(key + ': campione prima partita non valido')
            nested = {**snapshot, **first, 'colorContexts': first.get('colorContexts', {})}
            nested.pop('gameOne', None)
            validate_provider_snapshots({'externalSources': {key + ':game-one': nested}}, catalog, kind)
