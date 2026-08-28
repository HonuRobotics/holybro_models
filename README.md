# Holybro models

ROS 2 / Gazebo Sim model packages for Holybro vehicles: currently the X500
V2 quadcopter development kit, built from a configurable part library.
Targets **ROS 2 Lyrical + Gazebo Jetty** (the default pairing on Ubuntu
26.04), via `ros_gz`.

**Documentation: <https://honurobotics.github.io/holybro_models/>**

The site covers installation, running and configuring the X500, the ROS
interfaces and the design of the parts pipeline.

## Quick start

```bash
mkdir -p ~/ws/src
cd ~/ws/src && git clone https://github.com/HonuRobotics/holybro_models.git
cd ~/ws
rosdep update
rosdep install --from-paths src --ignore-packages-from-source --default-yes
colcon build --merge-install
source install/setup.bash
ros2 launch x500_gazebo sim.launch.xml
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Licensed Apache 2.0 (see
[LICENSE](LICENSE)); the placeholder meshes are BSD 3 Clause from PX4 (see
[NOTICE](NOTICE) and `holybro_parts/models/LICENSE`).
