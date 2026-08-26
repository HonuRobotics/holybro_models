# Reference

## Config schema

The vehicle config is one YAML document:

| Key | Required | Meaning |
|---|---|---|
| `topic_namespace` | no (`x500`) | prefix of every part topic: `/<ns>/<name>/...` |
| `base` | yes | the root part: `{type, name (default base_link), collision (default true)}` |
| `parts` | no (`[]`) | slot entries and free placements |
| `slots` | no | ad hoc slots: `{of (instance, default base_link), name, xyz, rpy, accepts, default, joint}` |
| `extra_bridge_topics` | no | list appended verbatim to the generated bridge config |

A slot entry: `slot`, `of` (instance carrying the slot; not `on`, which YAML
reads as `true`), `type` (accepted type or `none`), `name` (default: the
slot name; must be unique), `xyz`/`rpy`, `joint`, `axis`, `collision`, and
for parts with topics `topic`/`gz_topic`/`ros_topic`/`bridge`. A free
placement: `type`, `name`, `xyz` (required), `rpy`, `parent` and the same
optional keys. A key outside the schema is reported as a typo; errors name
the problem and fail the build or the launch.

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

See [X500: Sensors and Driving](../vehicles/x500.md). `/clock` and
`/joint_states` are always bridged; every part topic follows
`/<namespace>/<instance>/<suffix>` on both sides.

## Packages

| Package | Purpose |
|---|---|
| `holybro_parts` | the part library, the assembly dispatcher and the config check |
| `x500_description` | the X500 assembled from the parts; RViz view |
| `x500_gazebo` | composed Gazebo model, worlds, sim launch, generated bridge |
