# Combined runtime and optional dependency environments

Normal execution uses the combined `.venvs/runtime` environment. Install the
dependencies needed by `osu_megamix` there so imports are fast and direct.
Optional dependency-specific environments can still be created under
`.venvs/dependencies/<name>` for isolated experiments.

Create environments:

```bash
./create_venvs.sh runtime audio network
```

Install a package into one dependency environment:

```bash
./.venvs/dependencies/audio/bin/pip install <package-name>
```

Run the combined runtime:

```bash
./python app.py
```

The older `run_with_deps.sh` launcher remains available for testing separate
dependency environments when needed.
