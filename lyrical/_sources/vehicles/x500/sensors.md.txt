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
| `/<name>/imu` | Body IMU | [sensor_msgs/msg/Imu](https://docs.ros.org/en/rolling/p/sensor_msgs/interfaces/msg/Imu.html) |
| `/<name>/air_pressure` | Barometer | [sensor_msgs/msg/FluidPressure](https://docs.ros.org/en/rolling/p/sensor_msgs/interfaces/msg/FluidPressure.html) |
| `/<name>/mag` | Magnetometer | [sensor_msgs/msg/MagneticField](https://docs.ros.org/en/rolling/p/sensor_msgs/interfaces/msg/MagneticField.html) |

### GPS

| ROS Topic | Description | Message type |
|---|---|---|
| `/<name>/gps/fix` | Position fix | [sensor_msgs/msg/NavSatFix](https://docs.ros.org/en/rolling/p/sensor_msgs/interfaces/msg/NavSatFix.html) |

`<name>` is the instance name, `x500` for the default instance, or
whatever the quad was spawned as ([Several vehicles](../../how-to/index.md#several-vehicles)).
A part topic follows the part's own name (`gps` above), so a part renamed
or removed in the config moves or drops its topics
([Configuration](configuration.md)).

Sensor messages carry the sensor's frame under the instance name
(`<name>/base_link` for the flight sensors, `<name>/gps_antenna` for the
GPS), which is the frame `robot_state_publisher` publishes for the
instance.
