# Holybro models

ROS 2 / Gazebo Sim model packages for Holybro vehicles: currently the X500 V2
quadcopter development kit.

| Package | Purpose |
|---------|---------|
| [`x500_description`](x500_description/) | URDF/xacro, meshes, RViz; pure description, no simulator code |
| [`x500_gazebo`](x500_gazebo/) | Composed Gazebo model (rotor actuators + flight sensors), world, launch and ros_gz bridge |

Targets **ROS 2 Lyrical + Gazebo Jetty** (the default pairing on Ubuntu 26.04),
via `ros_gz`. The model is control-agnostic: PX4 SITL, ArduPilot SITL or any
custom controller can drive the motor bus (see the `x500_gazebo` README).

## Quick start

From source (binary `apt install ros-<distro>-x500-*` packages are planned):

```bash
cd ~/ws/src && git clone https://github.com/HonuRobotics/holybro_models.git
cd ~/ws
rosdep update
rosdep install --from-paths src --ignore-packages-from-source --default-yes
colcon build
source install/setup.bash
ros2 launch x500_gazebo sim.launch.xml     # Gazebo
ros2 launch x500_description display.launch.xml   # RViz
```

## Development

Optional but recommended: install the pre-commit hooks; they mirror the ament
linters that CI runs.

```bash
pip install pre-commit
pre-commit install              # from the repo root; runs on every git commit
pre-commit run --all-files      # manual check
```

The `ament_*` hooks need a sourced ROS environment.

## License

Apache-2.0 (see [LICENSE](LICENSE)). Reused BSD-3-Clause PX4 assets are
credited in [NOTICE](NOTICE) and `x500_description/ASSETS.md`.
