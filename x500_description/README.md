# x500_description

URDF/xacro **description** of the Holybro X500 V2 quadcopter: geometry, meshes
and an RViz view. Pure description: **no Gazebo or simulator code** (that
lives in [`x500_gazebo`](../x500_gazebo)).

## What it provides

- A quad-X airframe: `base_link` (carbon frame, motor housings, box colliders)
  and four rotors on `continuous` joints (`rotor_0..3`, PX4 `quad_x` spin:
  front-right/rear-left CCW, front-left/rear-right CW).
- **Config-driven accessory mounts** (battery, GPS mast, gimbal, companion
  computer) from `config/x500.yaml`. The battery and payload accessories make
  up the all-up weight, so mount poses matter for balance.
- The URDF is **generated from xacro at build time** (`urdf/x500.urdf`).

Meshes are BSD-3-Clause assets reused from PX4 (see [`ASSETS.md`](ASSETS.md)).

## Layout

```
urdf/     x500.urdf.xacro (top), accessories.xacro
config/   x500.yaml   (accessory loadout + topic namespace)
meshes/   frame / motor / prop meshes (+ LICENSE)
rviz/     x500.rviz
launch/   display.launch.xml
```

## Build

```bash
colcon build --merge-install --packages-select x500_description
source install/setup.bash
```

## Configure accessories

Edit `config/x500.yaml` and rebuild; it is a list of `{type, name, xyz, rpy}`
entries (pose relative to `base_link`, metres and radians):

| `type` | Mount |
|--------|-------|
| `battery` | 4S LiPo, the largest mass and biggest CG lever |
| `companion_computer` | RPi/Jetson-class box on the payload plate |
| `gimbal` | payload camera, slung below/forward |
| `gps_mast` | GPS/RTK puck on a mast |

The default loadout is the full dev-kit set (all four). The composed Gazebo
model and the ros_gz bridge config regenerate from this file on rebuild.

## API

This package exposes files and frames, no runtime nodes:

| Artifact | Path |
|----------|------|
| Generated URDF | `share/x500_description/urdf/x500.urdf` |
| Vehicle config | `share/x500_description/config/x500.yaml` |
| Xacro sources | `share/x500_description/urdf/*.xacro` |

Frames and joints (published as TF by `robot_state_publisher`):

| Name | Kind | Notes |
|------|------|-------|
| `base_link` | link (root) | airframe |
| `rotor_<N>`, `rotor_<N>_joint` | links, continuous joints | N = 0..3, quad-X |
| `<accessory name>` | link, fixed joint | one frame per configured accessory |

In Gazebo the fixed-joint accessory links are lumped into `base_link`; in
RViz/TF they stay separate frames.

### Known warning (harmless, do not "fix")

`robot_state_publisher` warns that the root link has an inertia KDL ignores.
This is cosmetic (KDL only publishes TF; Gazebo reads inertia via sdformat).
Do not add the suggested dummy root link: Gazebo's URDF conversion lumps
fixed joints, so a dummy root would absorb `base_link` and break every plugin
that references it.

## View in RViz

```bash
ros2 launch x500_description display.launch.xml
```

`display.launch.xml` expands the xacro at launch time, so a custom loadout
needs no rebuild: pass `config_file:=<your.yaml>`.

## Binary (deb) installs

The generated URDF is baked with the default config at packaging time; do not
edit files under `/opt/ros/...`. Customize via the `config_file` launch
argument (no rebuild) or an overlay workspace. See the `x500_gazebo` README
for the full recipe.

## Simulation

Geometry only. For the rotor actuators, flight sensors and a world, use
**[`x500_gazebo`](../x500_gazebo)**.
