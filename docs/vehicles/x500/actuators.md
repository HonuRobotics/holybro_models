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

The four rotors are driven together over one motor command bus:

| ROS Topic | Description | Message type |
|---|---|---|
| `/<name>/command/motor_speed` | Angular velocity per rotor (rad/s), one entry per rotor number, indexed from 0 | [actuator_msgs/msg/Actuators](https://github.com/rudislabs/actuator_msgs/blob/main/msg/Actuators.msg) |

`<name>` is the instance name, `x500` for the default instance, which the
commands below use, or whatever the quad was spawned as.

The `velocity` array carries one angular velocity per rotor, in rad/s,
where entry `i` drives `rotor_i`. Each motor plugin ramps its rotor to the
commanded speed with the part's time constants and holds it until the next
message, so always send all four; a stopped rotor is a `0`. To spin all
four by hand:

```bash
ros2 topic pub --once /x500/command/motor_speed actuator_msgs/msg/Actuators "{velocity: [700, 700, 700, 700]}"
```

and to stop them:

```bash
ros2 topic pub --once /x500/command/motor_speed actuator_msgs/msg/Actuators "{velocity: [0, 0, 0, 0]}"
```

The bus is a low level interface: it sets rotor speeds and nothing more,
and keeping the quad level and steering it is the job of a controller
above it. Rotor joint
states are bridged to `/<name>/joint_states` so RViz animates the props.

## Gazebo transport API

| gz Topic | Description | Message type |
|---|---|---|
| `/<name>/command/motor_speed` | The same bus on the Gazebo side | `gz.msgs.Actuators` |

The motor plugins build the topic from the instance name, so a quad spawned
as `uav_b` listens on `/uav_b/command/motor_speed`. The bridge maps the ROS
messages above onto it; the same command can be sent from the Gazebo side:

```bash
gz topic -t /x500/command/motor_speed -m gz.msgs.Actuators -p 'velocity: [700, 700, 700, 700]'
```

Keep the rotor instances named `rotor_0` .. `rotor_3`: the bus indexes
actuators by that trailing number.
