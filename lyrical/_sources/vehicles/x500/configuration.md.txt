# Configuration

The X500 needs no configuration: every slot the parts declare fills
itself with its default. The loadout config
(`x500_description/config/x500.yaml`, or any file passed as
`config_file:=`) states differences only.

## Payload

Sensors and actuators are fitted into slots, one config entry each. The
fitted options and their topics live in [Sensors](sensors.md) and
[Actuators](actuators.md); the slots are:

| Slot | Accepts | Default |
|---|---|---|
| `rotor_0` .. `rotor_3` | the matching 1345 propeller | fitted |
| `battery` | `battery_4s` | fitted |
| `gps` | `gps_mast` | fitted |
| `companion` | `companion_computer` | empty |
| `gimbal` | `gimbal_camera` | empty |

Keep the rotor instances named `rotor_0` .. `rotor_3`: the motor command
bus indexes actuators by that number, and the expansion fails loudly on a
rotor whose name does not end in its actuator number. Slot entries, free
placements, ad hoc slots and topic overrides follow the schema in
[Reference](../../reference/index.md); the instance key is `of:`, not
`on:`. Mistakes fail the build or the launch with a message naming the
problem.
