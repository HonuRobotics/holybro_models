# Contributing

Thanks for improving the Holybro vehicle models. This page covers the
developer workflow; using the models is documented in the [README](README.md)
and each package README, and releases in [RELEASING.md](RELEASING.md).

## Build and test

The project standard is the merged install layout, the same command CI runs:

```bash
colcon build --merge-install
colcon test --merge-install
colcon test-result --verbose
```

The gz integration suite runs a headless server; it needs the `gz` CLI and
fails (never skips) when the environment is broken. Test logs, including the
sim output tails, land in `log/` and are uploaded as a CI artifact on every
run. The CI workflow in `.github/workflows/ci.yml` is the source of truth for
the supported build.

## Pre-commit hooks

Optional but recommended: install the pre-commit hooks; they mirror the ament
linters that CI runs.

```bash
pip install pre-commit
pre-commit install              # from the repo root; runs on every git commit
pre-commit run --all-files      # manual check
```

The `ament_*` hooks need a sourced ROS environment.

## Conventions

- One-line commit subjects, signed off (`git commit -s`).
- Vehicle configuration lives in `x500_description/config/x500.yaml`; the
  URDF, the composed Gazebo model and the ros_gz bridge config are all
  GENERATED from it at build time. Never hand-edit the generated files.
- Every accessory type is a same-named xacro macro; the tests enforce that the
  config catalog and the macros stay in sync.
