# Reference

## Config schema

The vehicle config is one YAML document with these top level keys:

| Key | Required | Meaning |
|---|---|---|
| `base` | yes | the root part everything hangs off |
| `topic_namespace` | no (`x500`) | prefix of every part topic: `/<ns>/<name>/...` |
| `parts` | no (`[]`) | the parts to fit: slot entries and free placements |
| `slots` | no | extra mount points the parts do not declare themselves |
| `extra_bridge_topics` | no | appended verbatim to the generated bridge config |

`base` takes `type` (required), `name` (default `base_link`) and
`collision` (default true).

### Fitting a part

Entries under `parts:` come in two shapes. A **slot entry** drops a part
into a slot some part already declares; a **free placement** has no
`slot:` key and bolts the part to a parent at a pose you give.

| Key | Slot entry | Free placement |
|---|---|---|
| `slot` | the slot to fill | - |
| `of` | instance carrying the slot (default `base_link`) | - |
| `parent` | - | link to attach to (default the base) |
| `type` | an accepted type, or `none` to leave empty | required |
| `name` | default: the slot name | required |
| `xyz`, `rpy` | offset from the slot pose | `xyz` required, `rpy` optional |
| `joint`, `axis`, `collision` | optional | optional |
| `topic`, `gz_topic`, `ros_topic`, `bridge` | parts with topics only | parts with topics only |

Instance names must be unique across the vehicle.

```{warning}
The instance key is `of:`, not `on:`. YAML reads a bare `on` as the
boolean `true`, so the entry silently means something else.
```

### Ad hoc slots

Entries under `slots:` add a mount point that no part declares, then fill
it like any other: `of` (instance, default `base_link`), `name`, `xyz`,
`rpy`, `accepts`, `default`, `joint`, `collision`.

### Errors

A key outside the schema is reported as a typo rather than ignored, and
the message names the offending key alongside the ones that were
expected. Any error fails the build or the launch instead of producing a
half assembled vehicle.

## Parts catalog

| Type | What | Notes |
|---|---|---|
| `x500_airframe` | X500 V2 frame kit as one body | the assembly root; declares every slot |
| `prop_1345_ccw`, `prop_1345_cw` | 1345 propellers with motor bell | carry the drive table; continuous joints |
| `battery_4s` | 4S LiPo pack | box placeholder |
| `companion_computer` | RPi 4 / Jetson class computer | box placeholder |
| `gps_mast` | GPS module on a mast | `antenna` frame carries the NavSat |
| `gimbal_camera` | A8 mini class gimbal camera | box placeholder |

## Topics

See the X500 [Sensors](../vehicles/x500/sensors.md) and
[Actuators](../vehicles/x500/actuators.md) pages. `/clock` and
`/joint_states` are always bridged; every part topic follows
`/<namespace>/<instance>/<suffix>` on both sides.

## Packages

| Package | Purpose |
|---|---|
| `holybro_parts` | the part library, the assembly dispatcher and the config check |
| `x500_description` | the X500 assembled from the parts; RViz view |
| `x500_gazebo` | composed Gazebo model, worlds, sim launch, generated bridge |
