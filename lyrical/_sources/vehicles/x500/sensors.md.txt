# Sensors

Sensors are parts fitted into slots, with one exception: the IMU,
barometer and magnetometer belong to the airframe itself, as the
autopilot carries them on the real vehicle. The slots and their accepted
types are in the [configuration page](configuration.md), and new sensor
parts can be added following the [Add a part](../../how-to/index.md)
guide.

## Available sensors

| Sensor | Part | Slot | Fitted by default |
|---|---|---|---|
| IMU, barometer, magnetometer | the airframe | | yes |
| GPS | `gps_mast` | `gps` | yes |

## Sensors ROS API

### Flight sensors

| ROS Topic | Description | Message type |
|---|---|---|
| `/x500/imu` | Body IMU | [sensor_msgs/msg/Imu](https://docs.ros.org/en/rolling/p/sensor_msgs/interfaces/msg/Imu.html) |
| `/x500/air_pressure` | Barometer | [sensor_msgs/msg/FluidPressure](https://docs.ros.org/en/rolling/p/sensor_msgs/interfaces/msg/FluidPressure.html) |
| `/x500/mag` | Magnetometer | [sensor_msgs/msg/MagneticField](https://docs.ros.org/en/rolling/p/sensor_msgs/interfaces/msg/MagneticField.html) |

### GPS

| ROS Topic | Description | Message type |
|---|---|---|
| `/x500/gps/fix` | Position fix | [sensor_msgs/msg/NavSatFix](https://docs.ros.org/en/rolling/p/sensor_msgs/interfaces/msg/NavSatFix.html) |

Topic bases follow `/<namespace>/<instance>/...`: empty the GPS slot and
its topic disappears, rename the instance and it follows, and per part
`topic` / `gz_topic` / `ros_topic` overrides in the config rename the
base.
