# x500_gazebo

Gazebo Sim bring-up for the Holybro X500: the composed simulation model
(rotor actuators + flight sensors), a world, a sim launch file and the
generated ros_gz bridge. Gazebo-specific assets and plugins live here,
keeping [`x500_description`](../x500_description) free of simulator code.

> **Model only, no control layer.** The motors idle until something publishes
> commands, so the quad rests on its landing gear. The model is
> control-agnostic by design; see [Control](#control).

## What it provides

- `model.sdf`: **generated at build time** from `model.sdf.xacro`. It
  `<include merge="true">`s the description URDF and adds four
  `MulticopterMotorModel` plugins (the actuator plant, PX4 constants) and the
  flight sensors (IMU, air pressure, magnetometer, NavSat).
- `worlds/x500_playground.sdf`: ground, the sensor system plugins and a
  geodetic origin so NavSat yields lat/lon. No GPU needed: none of the flight
  sensors are rendered.
- `config/ros_gz_bridge.yaml`: **generated at build time** from the same
  vehicle config, so bridge topics always match the configuration.
- `launch/sim.launch.xml`, `model.config` (`model://x500_gazebo`).

## Build

```bash
colcon build --packages-select x500_description x500_gazebo
source install/setup.bash
```

## See the model in Gazebo

```bash
gz sim $(ros2 pkg prefix --share x500_gazebo)/worlds/x500_playground.sdf
ros2 launch x500_gazebo sim.launch.xml   # gui:=false  use_composition:=false  world:=<path>
```

> A `[kdl_parser] root link ... inertia` warning from robot_state_publisher is
> expected and harmless; see the note in the x500_description README.

## API

Flight-sensor topics live at `/<topic_namespace>/...` (default `x500`, set in
the vehicle config).

### ROS interface (via the generated bridge)

| ROS topic | Type | Direction |
|-----------|------|-----------|
| `/x500/imu` | `sensor_msgs/msg/Imu` | publishes |
| `/x500/air_pressure` | `sensor_msgs/msg/FluidPressure` | publishes |
| `/x500/mag` | `sensor_msgs/msg/MagneticField` | publishes |
| `/x500/gps` | `sensor_msgs/msg/NavSatFix` | publishes |
| `/clock` | `rosgraph_msgs/msg/Clock` | publishes |

`robot_state_publisher` (started by the launch) additionally publishes
`/robot_description` and TF.

### Gazebo transport interface (gz topics)

| gz topic | Type | Direction | Purpose |
|----------|------|-----------|---------|
| `x500/command/motor_speed` | `gz.msgs.Actuators` | subscribes | per-rotor angular velocity commands (the motor bus) |
| `/x500/{imu,air_pressure,mag,gps}` | sensor msgs | publishes | flight sensors |

Never edit the generated `config/ros_gz_bridge.yaml`; edit the vehicle config
and rebuild. Arbitrary extra bridge entries go in the config's
`extra_bridge_topics:` list.

## Control

The model is **control-agnostic**: anything that publishes `gz.msgs.Actuators`
on the motor bus flies it.

- **Custom**: publish directly, e.g.
  `gz topic -t /x500/command/motor_speed -m gz.msgs.Actuators -p 'velocity: [700,700,700,700]'`
  (equal thrust with no stabiliser will tip; expected without a controller).
- **PX4 SITL**: PX4's GZBridge publishes to the same bus; point PX4 at this
  world/model.
- **ArduPilot SITL**: add the ArduPilotPlugin overlay and run ArduPilot.

## Binary (deb) installs

From debs, the composed model and bridge config are baked with the default
loadout. Customize without a rebuild by passing `config_file:=` and
`bridge_config_file:=` to the launch, regenerating the model from the shipped
`model.sdf.xacro` into a directory that shadows `model://x500_gazebo` via
`GZ_SIM_RESOURCE_PATH`, and regenerating the bridge with the shipped
`generate_bridge_config.py`; all from the same config. An overlay workspace
is the recommended path for anything long-lived.

## Integrate the model into an existing Gazebo project

1. Sourcing the workspace puts `x500_gazebo` on `GZ_SIM_RESOURCE_PATH`
   (env hook), so `model://x500_gazebo` resolves.
2. Reference it in your world SDF and copy the sensor system plugins and
   `<spherical_coordinates>` from `worlds/x500_playground.sdf`:

   ```xml
   <include>
     <uri>model://x500_gazebo</uri>
     <name>x500</name>
     <pose>0 0 0.25 0 0 0</pose>
   </include>
   ```
3. Or spawn at runtime:

   ```bash
   ros2 run ros_gz_sim create -world <your_world> -name x500 -z 0.25 \
     -file $(ros2 pkg prefix --share x500_gazebo)/model.sdf
   ```
