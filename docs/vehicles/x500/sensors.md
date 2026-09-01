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

These topic names are not fixed strings. Every part topic is built as
`/<namespace>/<instance>/<suffix>`, so the fix above is the `gps`
instance publishing `fix` under the `x500` namespace. Change the vehicle
and the topics change with it:

- Empty the GPS slot and `/x500/gps/fix` goes away with the part.
- Rename the instance and the topic follows the new name.
- Set `topic`, `gz_topic` or `ros_topic` on the part in the config to
  rename the base yourself.
