# Project

## Contributing

Pull requests target the `lyrical` branch and need the CI checks green; the
developer workflow (build, test, lint) is in the repository's
[CONTRIBUTING.md](https://github.com/HonuRobotics/holybro_models/blob/lyrical/CONTRIBUTING.md).
The documentation is built with [honu-docs](https://github.com/HonuRobotics/honu-docs)
(Sphinx + MyST); every pull request gets a strict build, pushes to a distro
branch deploy that branch:

```bash
pip install -r docs/requirements.txt
sphinx-build -W docs _build/html && python3 -m http.server -d _build/html
```

## Releases

The packages follow the standard ROS release flow (CHANGELOG.rst per
package, bloom into rosdistro) once the interfaces settle.
