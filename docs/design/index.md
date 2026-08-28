# Design

The X500 is built from a **part library** (`holybro_parts`): each part is a
hand maintained URDF xacro macro stating its own inertia, visuals,
collisions, **slots** (where other parts fit, with accepted options and a
default), **frames** (a sensor's antenna) and, for propellers, a **drive**
table (what a simulator needs to spin it). The assembly dispatcher fills
every slot with its default, applies the config's overrides, and records
the result in the URDF as `<assembly_part>` and `<assembly_slot>` elements,
a manifest that downstream tooling (the Gazebo composition, the bridge
generator, the `holybro_parts.assembly` config check) reads instead of
re-resolving anything. `x500_gazebo` runs the same resolution with Gazebo
emitters, so a propeller gets its motor plugin and a GPS part its NavSat
wherever the config mounted them, and the generated bridge can never
disagree with the model.

The machinery (the part contract, `assembly.xacro`, the manifest check) is
shared with
[bluerobotics_models](https://honurobotics.github.io/bluerobotics_models/),
where the design is documented in depth (Slots and assembly, Gazebo
composition); extraction into a common package is planned.

## Assets

The meshes are **temporary placeholders** reused from PX4's
[PX4-gazebo-models](https://github.com/PX4/PX4-gazebo-models) x500 model
(BSD 3 Clause, `holybro_parts/models/LICENSE`): the frame is the NXP
HoverGames body, geometrically close to but not the exact Holybro X500 V2
shell, and the motor bell is the HoverGames 5010. Inertias, rotor poses and
motor constants are PX4's matched, hover tuned set. Original Holybro art
(glTF, PBR) will replace them part by part.
