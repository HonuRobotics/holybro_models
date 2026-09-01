# How to guides

## Change the loadout

Copy `x500_description/config/x500.yaml`.

```bash
cp "$(ros2 pkg prefix --share x500_description)"/config/x500.yaml $HOME/ws/my_loadout.yaml
```


Edit it and pass it to the
launches; nothing rebuilds:

```bash
ros2 launch x500_gazebo sim.launch.xml config_file:=$HOME/ws/my_loadout.yaml
ros2 launch x500_description display.launch.xml config_file:=$HOME/ws/my_loadout.yaml
```

A slot entry picks what goes in a slot (`{slot: gimbal, type: gimbal_camera}`,
`{slot: gps, type: none}`); an entry without `slot:` is a free placement
(`{type: battery_4s, name: battery_aft, xyz: "-0.09 0 -0.045"}`); ad hoc
slots go under `slots:`. The instance key for a slot of a non base part is
`of:`, not `on:` (YAML reads a bare `on` as the boolean `true`).

## Generate the artifacts yourself

```bash
ros2 run x500_gazebo configure_vehicle.py --config $HOME/ws/my_loadout.yaml --out-dir ~/my_x500
```

writes the URDF, `model.sdf`, `model.config` and the bridge config; the
directory works as a `model://` root on `GZ_SIM_RESOURCE_PATH`. To check a
config against an assembled URDF:

```bash
ros2 run holybro_parts check_assembly.py $HOME/ws/my_loadout.yaml ~/my_x500/x500.urdf
```

## Add a part

A part is one hand written URDF xacro macro in `holybro_parts/urdf/`,
following the contract documented at the top of
`holybro_parts/urdf/parts.xacro`: a `<part>_info` macro exporting attach,
slots, frames and (for propellers) a drive table, and the part macro
emitting the link, its mounting joint and its slot and frame links. Add the
include to `parts.xacro`, and for a sensor part teach `x500_gazebo`'s
`model.sdf.xacro` emitter and `generate_bridge_config.py`'s `PART_TOPICS`
its topics (the GPS mast is the template).
