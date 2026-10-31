<h1 align="center">traejiik's Jellyfin plugins</h1>

<p><img src="assets/readme-banner.svg" alt="AniDōki and Task Timeline" width="100%"></p>

One plugin repository for Jellyfin that serves every plugin below from a single manifest.

## Install

1. In Jellyfin, open **Dashboard → Plugins → Repositories**, add a repository:

    Name: `TJK Plugins`  
    Repository URL:
    ```
    https://raw.githubusercontent.com/traejiik/jellyfin-tjk-plugins/main/manifest.json
    ```

2. The plugins then show up in the **Catalog**:

    | Plugin | Source |
    | --- | --- |
    | AniDoki | [traejiik/jellyfin-anidoki](https://github.com/traejiik/jellyfin-anidoki) |
    | Task Timeline | [traejiik/jellyfin-tasktimeline](https://github.com/traejiik/jellyfin-tasktimeline) |

## How it works

`scripts/build_manifest.py` reads each repository in `sources.json`. It takes the plugin's
details from the `manifest.json` on that repository's branch, and its versions from the
`manifest.json` attached to every published release. A plugin with no releases yet is left out.

The **Update plugin manifest** workflow rebuilds `manifest.json` every hour, on manual run,
and on a `plugin-released` repository dispatch, and commits it when something changed.

To add a plugin, add its repository to `sources.json`.

To rebuild locally:

```sh
GH_TOKEN=$(gh auth token) python3 scripts/build_manifest.py
```
