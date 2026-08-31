# Actuators

Actuators are parts fitted into slots, exactly like the sensors. The
vehicle's slots and their accepted types are in the
[configuration page](configuration.md), and new parts can be added
following the [Add a part](../../how-to/index.md) guide.

## Available actuators

| Actuator | Part | Slot | Fitted by default |
|---|---|---|---|
| 1345 propellers, counter clockwise | `prop_1345_ccw` | `rotor_0`, `rotor_1` | yes |
| 1345 propellers, clockwise | `prop_1345_cw` | `rotor_2`, `rotor_3` | yes |

## Actuators ROS API

There is none, deliberately. On a multicopter the per rotor outputs only
make sense downstream of an attitude controller, so the autopilot (PX4
SITL, ArduPilot SITL or a custom controller) is the control layer and it
talks to the Gazebo motor bus directly. The marine vehicles (BlueBoat,
BlueROV2) expose a normalized -1..1 `throttle` topic per thruster, the
ArduPilot output convention; the X500's equivalent normalized layer is
the autopilot itself. Rotor joint states are bridged to `/joint_states`
so RViz animates the props.

## Gazebo transport API

| gz Topic | Description | Message type |
|---|---|---|
| `/x500/command/motor_speed` | Angular velocity per rotor (rad/s), indexed by the rotor number | `gz.msgs.Actuators` |

To spin the rotors by hand, with no autopilot:

```bash
gz topic -t /x500/command/motor_speed -m gz.msgs.Actuators -p 'velocity: [700, 700, 700, 700]'
```

Keep the rotor instances named `rotor_0` .. `rotor_3`: the bus indexes
actuators by that trailing number.
