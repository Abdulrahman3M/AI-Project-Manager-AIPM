# AIPM v1.5.0 Release Notes

## Task Lifecycle And Existing Work Registration

- **Create New Task** now remains the workflow for a new task record, and was repaired under PowerShell strict mode to prevent evaluating uninitialized work folder arguments.
- **Add Existing Work Folder** registers an existing project folder and stores a reference inventory in the task's `References` category.
- Task management now supports explicit completion and reopening, with an auditable note stored in Core task state.
- Completed tasks can be exported as a portable ZIP with a SHA-256 checksum in `Shared-Project-State-Manager/Archive` while the live record remains available.
- Task management can review Git changes and create a confirmed local commit that excludes AIPM's state directory. It never pushes a remote branch.

## Distribution

Version `1.5.0` is an unpublished repository update. Generated ChatGPT, Claude, and Google Antigravity archives were validated during the build; package readiness does not install them into any host.
