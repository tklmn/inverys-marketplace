# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-10-13

### Added
- Catalog `marketplace.json` (schema 1) for Inverys CMS with the Ember theme and the Announcement Bar plugin: version, download of the release package and its SHA-256 checksum, preview image and project page per package.
- `bin/build-catalog.py` builds the catalog from the latest releases of the repositories in `packages.json` (standard library only, `--check` for an up-to-date test).
