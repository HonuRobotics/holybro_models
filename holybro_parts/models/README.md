# Visual models

One directory per part, each holding `<part>_visual.glb` files built to the
[Honu glTF Asset Profile](https://github.com/HonuRobotics/gltf-robotics): a
single self-contained binary glTF per part, in glTF's own axes (+Y up, +Z
forward), with its origin on the datum named below and its PBR materials
embedded. Each file carries its manifest (`KHR_xmp_json_ld`): role, datum,
source, rights and the cited dimension, written from the commission,
[`../commissions/commission-x500.yaml`](../commissions/commission-x500.yaml).
`docs/vehicles/x500/images/datums.png` shows every part's origin and axes.

| File | Datum (the part frame) | Source |
|---|---|---|
| `x500_airframe/x500_airframe_visual.glb` | center of the 30.5 mm flight controller hole pattern, lower face of the bottom plate (`base_link`) | modeled from the kit's published and measured dimensions, with avionics and wiring |
| `motor_2216/motor_2216_stator_visual.glb` | center of the motor base's mounting face, on the motor axis | modeled from the 2216 size: base, 12 slot wound stator |
| `motor_2216/motor_2216_bell_visual.glb` | center of the bell's top face (the prop seat), on the motor axis | modeled from the 2216 size: vented can, magnets, shaft |
| `prop_1045_ccw/prop_1045_ccw_visual.glb`, `prop_1045_cw/…` | center of the hub's lower face, on the rotation axis | modeled, 10 x 4.5 inch |
| `gps_mast/gps_mast_visual.glb` | center of the base clamp's lower face, on the mast axis | modeled folding mast and M10 puck |
| `battery_4s/battery_4s_visual.glb` | center of the pack's top face | modeled, 145 x 48 x 38 mm |
| `companion_computer/companion_computer_visual.glb` | center of the 58 x 49 mm hole pattern, standoffs' lower faces | modeled Raspberry Pi 5 |
| `gimbal_camera/gimbal_camera_visual.glb` | center of the mounting plate's upper face | modeled SIYI A8 mini |

## Materials as Gazebo renders them

Every finished material carries baked maps, because those are what Gazebo's
loader and renderer use: a base color, a packed metal-rough map (roughness in
green, metalness in blue) and a tangent space normal map, plus emissive color on
the lit LEDs and binary alpha (`MASK`) on printed markings. The bake rounds every
hard edge in the normal map so it catches light, darkens crevices with ambient
occlusion in the base color, polishes or machines edges (diamond cut aluminum,
worn plastic), and adds relief at physical scale: the carbon twill, molding
stipple, EVA foam cells, brushed aluminum, heat shrink, stator laminations.

Metals are partly metallic, 0.25 to 0.65 over a bright base color. Gazebo hands
embedded glTF materials no environment map, so metalness 1 renders black except
for the specular highlight (gltf-robotics issue #1), while partial metalness reads
as satin metal (measured on Jetty 10.5.0 and Rotary 11.0.0~pre2). `gltf-check`
warns about the metallic factors on four parts; this is a deliberate deviation from the
profile.

No glTF occlusion map is used: Ogre adds it as a light map (extra light), so
occlusion is baked into the base color instead. Large base colors are JPEG, every
data map PNG. Textures are kept small so a vehicle stays light on GPU memory:
baked maps are at most 512 px a side and normal maps 256 px, and printed labels
hold at most 512 x 512 pixels of area, so a long thin print stays sharp. All
textures are generated; no third-party image assets are used.

The frame carries a representative avionics install of a typical X500 V2 build,
modeled from published sizes and baked into its visual: flight controller, power
module and battery lead, telemetry radio, RC receiver, four
ESCs, wiring and cable ties. They have no links and no mass of their own; the
frame's lumped inertia already stands for them.

Gazebo Rotary note: gz-common 8 runs assimp's degenerate triangle removal with its
default area check, which drops triangles below 1e-6 square meters (1 mm^2) and
with them the fine detail of small parts. Jetty does not. Setting
`AI_CONFIG_PP_FD_CHECKAREA` false in the loader restores it.

## Licensing

Every model here is Apache-2.0 (Copyright 2026 Honu Robotics), drawn by scripts
from the kit's dimensions. `LICENSE` here is PX4's BSD 3 Clause license, which
still covers the inertias, the propeller collision boxes and the motor
constants in the part macros. The other collisions are boxes and cylinders
fitted to the kit's measured outer shell, the primitives DART and MuJoCo both handle
natively.
