<p align="center">
  <img src="https://img.shields.io/badge/Inverys_CMS-Marketplace-6366f1?style=for-the-badge" alt="Inverys CMS Marketplace">
  <img src="https://img.shields.io/badge/Catalog-schema_1-22c55e?style=for-the-badge" alt="Catalog schema 1">
</p>

# :convenience_store: Inverys Marketplace

The default marketplace of [Inverys CMS](https://github.com/tklmn/inverys-cms): one catalog file, [`marketplace.json`](marketplace.json), that lists themes and plugins with their version, download and SHA-256 checksum. Every Inverys installation shows its packages under **Extensions > Themes / Plugins > Marketplace**.

```
https://raw.githubusercontent.com/tklmn/inverys-marketplace/master/marketplace.json
```

That address is the default of `CMS_MARKETPLACE_SOURCES`. Further catalogs — your own, a company's — are added in the backend under **Marketplace > Sources**.

## :package: Packages

| Package | Type | Repository |
|---|---|---|
| **Ember** — a dark theme with warm amber accents | theme | [tklmn/inverys-cms-theme-ember](https://github.com/tklmn/inverys-cms-theme-ember) |
| **Announcement Bar** — a configurable bar on every page | plugin | [tklmn/inverys-cms-plugin-announcement-bar](https://github.com/tklmn/inverys-cms-plugin-announcement-bar) |

## :arrows_counterclockwise: Updating the catalog

The catalog is generated from the latest release of every repository in [`packages.json`](packages.json):

```bash
GITHUB_TOKEN=$(gh auth token) python3 bin/build-catalog.py
```

For each repository the script takes the `<slug>-<version>.zip` attached to the release (built by the package's *Release package* workflow), computes its SHA-256 checksum and reads name, description, version and preview from the manifest inside. To add a package, put its repository into `packages.json` and run the script again. `--check` only reports whether `marketplace.json` is up to date.

## :hammer_and_wrench: Your own marketplace

Any https address that serves a catalog in this format works — see [MARKETPLACE.md](https://github.com/tklmn/inverys-cms/blob/master/docs/MARKETPLACE.md) in the CMS for the format, the rules for package ZIPs, permissions and security.

## :scroll: License

MIT
