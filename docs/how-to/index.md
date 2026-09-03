# How to guides

## Change the loadout

The vehicle is described by one YAML config, so changing what is fitted
never means rebuilding. Start from the default config:

```bash
mkdir -p $HOME/my_x500
cp "$(ros2 pkg prefix --share x500_description)"/config/x500.yaml $HOME/my_x500/my_loadout.yaml
```

Edit your copy, then hand it to either launch with `config_file:=`:

```bash
ros2 launch x500_gazebo sim.launch.xml config_file:=$HOME/my_x500/my_loadout.yaml
ros2 launch x500_description display.launch.xml config_file:=$HOME/my_x500/my_loadout.yaml
```

Inside the config there are three ways to place a part:

- A **slot entry** fills one of the slots the parts declare. Name the slot
  and the type that goes in it, or `none` to leave it empty:

  ```yaml
  parts:
    - {slot: gimbal, type: gimbal_camera}
    - {slot: gps, type: none}
  ```

- A **free placement** is an entry with no `slot:`. It bolts a part
  straight onto its parent at a pose you give:

  ```yaml
  parts:
    - {type: battery_4s, name: battery_aft, xyz: "-0.09 0 -0.045"}
  ```

- An **ad hoc slot** under `slots:` adds a mount point the parts did not
  declare.

```{tip}
To fill a slot on a part other than the base, the instance key is `of:`,
never `on:`. YAML reads a bare `on` as the boolean `true`.
```

## Generate the artifacts yourself

The launches generate everything they need, but you can write the same
artifacts to a directory of your own:

```bash
ros2 run x500_gazebo configure_vehicle.py --config $HOME/my_x500/my_loadout.yaml --out-dir $HOME/my_x500
```

That writes `x500.urdf`, `model.sdf`, `model.config`,
`ros_gz_bridge.yaml` and `robot_description.yaml`. Because the directory
holds a `model.sdf` next to a `model.config`, it works as a `model://`
root on `GZ_SIM_RESOURCE_PATH`.

To confirm a config and an assembled URDF still agree:

```bash
ros2 run holybro_parts check_assembly.py $HOME/my_x500/my_loadout.yaml $HOME/my_x500/x500.urdf
```

## Add a part

A part is one hand written URDF xacro macro in `holybro_parts/urdf/`. The
contract it has to follow is documented at the top of
`holybro_parts/urdf/parts.xacro`; in short, the file holds two macros:

- `<part>_info`, exporting the part's metadata: where it attaches, its
  slots, its frames and, for propellers, a drive table.
- the part macro itself, emitting the link, its mounting joint, and its
  slot and frame links.

Then add the include to `parts.xacro`. A sensor part needs two more
edits, so that its topics reach Gazebo and the bridge:

- the emitter in `x500_gazebo`'s `model.sdf.xacro`,
- `PART_TOPICS` in `generate_bridge_config.py`.

The GPS mast is the worked example to copy from for both.
