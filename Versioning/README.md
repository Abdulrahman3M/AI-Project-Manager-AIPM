# Product Versioning

`VERSION` and `CHANGELOG.md` in this directory are the single source of truth for the AIPM product release. Do not edit root, TUI, or Plugin compatibility `VERSION` files directly. Update the canonical version and changelog, then run:

```powershell
python Maintenance-Tools/Sync-Product-Version.py
```

The synchronizer updates root, PowerShell TUI, and host Plugin distribution versions and inserts the canonical release entry into component changelogs. Independently versioned Skills keep their own release streams. Release notes and source archives are generated or built from this canonical release record.
