"""Inventory stored source URLs for registered sets, without network access."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[4]
META = ('id', 'publisher', 'label', 'kind', 'status', 'retrieved', 'checked',
        'published', 'date', 'verified', 'error', 'sha256', 'archiveSha256')


def collect(value, pointer='', context=None):
    if isinstance(value, dict):
        context = {**(context or {}), **{k: value[k] for k in META if k in value}}
        for key, child in value.items():
            escaped = str(key).replace('~', '~0').replace('/', '~1')
            yield from collect(child, pointer + '/' + escaped, context)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from collect(child, pointer + '/' + str(index), context)
    elif isinstance(value, str) and value.startswith(('https://', 'http://')):
        yield value, pointer, context or {}


def research_owner(name, slugs):
    matches=[slug for slug in slugs if re.fullmatch(re.escape(slug)+r'-\d{8}(?:-.+)?',name)]
    return max(matches,key=len,default=None)


def inventory(root):
    sets = []
    entries=json.loads((root / 'expansions.json').read_text(encoding='utf-8'))
    manifests=[(entry,root/entry['manifest'],json.loads((root/entry['manifest']).read_text(encoding='utf-8'))) for entry in entries]
    slugs=[manifest['id'] for _,_,manifest in manifests]
    for entry,manifest_path,manifest in manifests:
        slug = manifest['id']
        source_path = manifest_path.parent / manifest['datasets']['sources']
        files = [source_path]
        directories = sorted(path for path in (root / 'research').glob(slug + '-*') if path.is_dir() and research_owner(path.name,slugs)==slug)
        for directory in directories:
            for name in ('source-audit.json', 'fetch-audit.json'):
                candidate = directory / name
                if candidate.is_file():
                    files.append(candidate)
        urls, documents = {}, []
        for path in files:
            relative = path.relative_to(root).as_posix()
            raw = path.read_bytes()
            document = json.loads(raw.decode('utf-8-sig'))
            documents.append({'path': relative, 'sha256': hashlib.sha256(raw).hexdigest()})
            for url, pointer, metadata in collect(document):
                row = urls.setdefault(url, {'url': url, 'host': urlsplit(url).netloc,
                                            'occurrences': []})
                row['occurrences'].append({'document': relative, 'pointer': pointer,
                                           'recordedMetadata': metadata})
        sources = json.loads(source_path.read_text(encoding='utf-8-sig'))
        local_references = []
        for key, download in sources.get('downloads', {}).items():
            value = download.get('url', '')
            if value and not urlsplit(value).scheme:
                candidates = [manifest_path.parent / value, root / value]
                local_references.append({'key': key, 'reference': value,
                    'existingFiles': [p.relative_to(root).as_posix() for p in candidates if p.is_file()]})
        sets.append({'id': slug, 'manifest': entry['manifest'],
            'sourceDocuments': documents, 'uniqueUrls': len(urls),
            'sources': sorted(urls.values(), key=lambda row: row['url']),
            'localDownloads': local_references,
            'researchFiles': [p.relative_to(root).as_posix() for directory in directories
                              for p in sorted(directory.rglob('*')) if p.is_file()]})
    return {'schemaVersion': 1, 'scope': 'stored_registries_and_source_audits',
        'networkVerified': False,
        'limitations': ['Stored retrieval metadata is historical, not a live availability check.',
            'Raw HTML may exist only in a temporary cache; a URL/hash is not a local archive.',
            'Card URLs embedded only in catalogs or observations are outside this source-register inventory.'],
        'sets': sets}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    result = inventory(args.root.resolve())
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.output:
        # Exclusive creation protects a previous acquisition or unrelated file.
        with args.output.open('x', encoding='utf-8', newline='\n') as stream:
            stream.write(serialized)
        print(json.dumps({'output': str(args.output), 'sets': [
            {'id': item['id'], 'uniqueUrls': item['uniqueUrls'],
             'researchFiles': len(item['researchFiles'])} for item in result['sets']]}))
    else:
        print(serialized, end='')


if __name__ == '__main__':
    main()
