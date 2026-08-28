# Getting started

## Requirements

- ROS 2 Lyrical on Ubuntu 26.04
- Gazebo Jetty, installed as ROS 2 Lyrical's `ros_gz` dependency (the
  packages talk to Gazebo only through `ros_gz`)

## Installation

Into a colcon workspace:

```bash
mkdir -p ~/ws/src
cd ~/ws/src
git clone https://github.com/HonuRobotics/holybro_models.git
cd ~/ws
rosdep update
rosdep install --from-paths src --ignore-packages-from-source --default-yes
colcon build --merge-install
source install/setup.bash
```

The project standard is `colcon build --merge-install`; the default isolated
layout also works. Binary debs are planned once the packages are released
into the ROS ecosystem; a released vehicle can then be reconfigured without
rebuilding (see [Change the loadout](../how-to/index.md)).

## First simulation

```bash
ros2 launch x500_gazebo sim.launch.xml
```

Gazebo opens with the X500 resting on its landing gear. The model carries
no control layer: the rotors idle until something publishes
`gz.msgs.Actuators` on `/x500/command/motor_speed` (that is the autopilot's
job; PX4 SITL, ArduPilot SITL or a custom controller). The flight sensors
publish right away:

```bash
ros2 topic echo /x500/imu --once
ros2 topic echo /x500/gps/fix --once
```

To see the model in RViz instead:

```bash
ros2 launch x500_description display.launch.xml
```
