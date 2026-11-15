# Product Versioning

`VERSION` and `CHANGELOG.md` in this directory are the single source of truth for the AIPM product release. Do not edit root or TUI compatibility `VERSION` files directly. Update the canonical version and changelog, then run:

```powershell
python Maintenance-Tools/Sync-Product-Version.py
```

The synchronizer updates root and PowerShell TUI versions and inserts the canonical release entry into their changelogs. Plugins and Skills keep independently governed release streams. Release notes and source archives are generated or built from this canonical release record.
