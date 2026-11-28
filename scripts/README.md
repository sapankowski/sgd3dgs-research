# Scripts

- `uv.sh`: runs uv in repository-local `venv/`, avoiding the macOS hidden `.pth`
  problem associated with `.venv/` under some synced folders.
- `check_system.sh`: checks lightweight requirements and reports optional GPU
  worker capabilities.
- `fetch_upstreams.sh`: fetches exact Gaussian Grouping and SAGA commits into
  ignored `.external/` paths without overwriting existing checkouts.
- `validate_with_app.sh`: validates a completed scene package using the sibling
  app's authoritative CLI.
- `spatial_cleanup/`: CPU spatial-island candidate reports and three-view comparison.
- `verify_repository.sh`: enforces the repository boundary and rejects tracked
  large/model/scene artifacts.

Scripts orchestrate owned code or pinned external tools. Scientific logic and
silent data conversion must not be hidden in shell scripts.
