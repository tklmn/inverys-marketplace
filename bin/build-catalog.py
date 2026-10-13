#!/usr/bin/env python3
"""Build marketplace.json from the latest releases of the repositories in packages.json.

For every repository: the latest release, its attached <slug>-<version>.zip
(built by the package's release workflow), the SHA-256 checksum of exactly
that file and the manifest (theme.json / plugin.json) inside it. Only the
Python standard library is used; GITHUB_TOKEN raises the GitHub API limit.

    python3 bin/build-catalog.py            write marketplace.json
    python3 bin/build-catalog.py --check    fail if marketplace.json is out of date
"""

import hashlib
import io
import json
import os
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / 'marketplace.json'
PACKAGES = ROOT / 'packages.json'
MANIFESTS = {'theme.json': 'theme', 'plugin.json': 'plugin'}
SLUG = re.compile(r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$')
PATH = re.compile(r'^[A-Za-z0-9_][A-Za-z0-9._-]*(/[A-Za-z0-9_][A-Za-z0-9._-]*)*$')


def fetch(url: str, accept: str = 'application/vnd.github+json') -> bytes:
    headers = {'Accept': accept, 'User-Agent': 'inverys-marketplace'}
    token = os.environ.get('GITHUB_TOKEN', '')
    if token and url.startswith('https://api.github.com/'):
        headers['Authorization'] = 'Bearer ' + token
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=60) as response:
        return response.read()


def fail(message: str) -> None:
    sys.exit('error: ' + message)


def package(repository: str) -> dict:
    release = json.loads(fetch(f'https://api.github.com/repos/{repository}/releases/latest'))
    tag = release['tag_name']
    version = tag.lstrip('vV')

    assets = [a for a in release.get('assets', []) if a['name'].endswith('.zip')]
    if not assets:
        fail(f'{repository} {tag}: no .zip attached to the release (run its release workflow)')
    asset = assets[0]
    data = fetch(asset['browser_download_url'], 'application/octet-stream')

    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        found = [n for n in archive.namelist() if n.split('/')[-1] in MANIFESTS and n.count('/') <= 1]
        if len(found) != 1:
            fail(f'{repository}: expected one theme.json or plugin.json in {asset["name"]}, found {found}')
        manifest = json.loads(archive.read(found[0]))
        package_type = MANIFESTS[found[0].split('/')[-1]]
        composer = found[0].rsplit('/', 1)[0] + '/composer.json' if '/' in found[0] else 'composer.json'
        license_name = manifest.get('license') or (json.loads(archive.read(composer)).get('license', '') if composer in archive.namelist() else '')

    slug = manifest.get('slug', '')
    if not SLUG.match(slug):
        fail(f'{repository}: invalid slug {slug!r}')
    if manifest.get('version') != version:
        fail(f'{repository}: manifest version {manifest.get("version")} differs from the tag {tag}')

    entry = {
        'type': package_type,
        'slug': slug,
        'name': manifest.get('name', slug),
        'description': manifest.get('description', ''),
        'author': manifest.get('author', ''),
        'version': version,
    }
    if manifest.get('requires'):
        entry['requires'] = manifest['requires']
    if license_name:
        entry['license'] = license_name
    entry['download'] = asset['browser_download_url']
    entry['sha256'] = hashlib.sha256(data).hexdigest()
    screenshot = manifest.get('screenshot')
    if isinstance(screenshot, str) and PATH.match(screenshot) and '..' not in screenshot:
        entry['screenshot'] = f'https://raw.githubusercontent.com/{repository}/{tag}/{screenshot}'
    entry['homepage'] = f'https://github.com/{repository}'

    return entry


def build() -> str:
    config = json.loads(PACKAGES.read_text(encoding='utf-8'))
    entries = [package(repository) for repository in config['repositories']]
    entries.sort(key=lambda e: (e['type'], e['slug']))

    slugs = [(e['type'], e['slug']) for e in entries]
    if len(slugs) != len(set(slugs)):
        fail('the same slug appears twice')

    catalog = {'schema': 1, 'name': config.get('name', 'Inverys Marketplace'), 'packages': entries}
    return json.dumps(catalog, indent=4, ensure_ascii=False) + '\n'


def main() -> None:
    text = build()
    if '--check' in sys.argv[1:]:
        current = CATALOG.read_text(encoding='utf-8') if CATALOG.exists() else ''
        if current != text:
            fail('marketplace.json is out of date — run python3 bin/build-catalog.py')
        print('marketplace.json is up to date')
        return
    CATALOG.write_text(text, encoding='utf-8', newline='\n')
    print(f'wrote {CATALOG.name}: {text.count(chr(34) + "slug" + chr(34))} packages')


if __name__ == '__main__':
    main()
