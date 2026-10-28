#!/usr/bin/env python3
"""Merge the installation feeds of several Jellyfin plugin repositories into one manifest.

Each source contributes its plugin metadata from the manifest.json committed on its
branch, and its versions from both that file and the manifest.json asset attached to
each published GitHub release. Versions are de-duplicated and sorted newest first.
"""
import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

API = 'https://api.github.com'


def fetch(url, token=None):
    headers = {'User-Agent': 'jellyfin-tjk-plugins', 'Accept': 'application/vnd.github+json'}
    if token and url.startswith(API):
        headers['Authorization'] = f'Bearer {token}'
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
        return json.load(response)


def releases(repository, token):
    page = 1
    while True:
        batch = fetch(f'{API}/repos/{repository}/releases?per_page=100&page={page}', token)
        yield from batch
        if len(batch) < 100:
            return
        page += 1


def version_key(entry):
    return tuple(int(part) for part in entry['version'].split('.'))


def build_plugin(source, token):
    repository = source['repository']
    branch = source.get('branch', 'main')
    plugins = fetch(f'https://raw.githubusercontent.com/{repository}/{branch}/manifest.json')
    plugin = plugins[0]
    versions = {entry['version']: entry for entry in plugin.get('versions', [])}

    for release in releases(repository, token):
        if release['draft'] or release['prerelease']:
            continue
        asset = next((a for a in release['assets'] if a['name'] == 'manifest.json'), None)
        if asset is None:
            continue
        for released in fetch(asset['browser_download_url']):
            if released.get('guid') != plugin['guid']:
                continue
            for entry in released.get('versions', []):
                versions[entry['version']] = entry

    plugin['versions'] = sorted(versions.values(), key=version_key, reverse=True)
    return plugin


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sources', type=Path, default=Path('sources.json'))
    parser.add_argument('--output', type=Path, default=Path('manifest.json'))
    args = parser.parse_args()

    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    manifest = []
    for source in json.loads(args.sources.read_text()):
        plugin = build_plugin(source, token)
        if not plugin['versions']:
            print(f"Skipping {plugin['name']}: no released versions yet.", file=sys.stderr)
            continue
        print(f"{plugin['name']}: {len(plugin['versions'])} versions", file=sys.stderr)
        manifest.append(plugin)

    args.output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + '\n')


if __name__ == '__main__':
    main()
