# Design

A vehicle here is not a hand written URDF. It is a set of **parts** fitted
into **slots**, assembled on the fly from the part library
(`holybro_parts`).

## Parts

Every part is a hand maintained URDF xacro macro that describes itself:

| A part declares | What it is for |
|---|---|
| inertia, visuals, collisions | the physical body |
| **slots** | where other parts fit: the accepted options and a default |
| **frames** | named attachment points, such as a GPS antenna |
| **drive** table (propellers only) | what a simulator needs to spin it |

Because each part carries its own slots, the airframe does not need to know
what a GPS mast is, and the mast does not need to know what it is bolted
to.

## Assembly

The assembly dispatcher builds the vehicle in three steps:

1. Fill every slot with its default.
2. Apply the overrides from the vehicle config.
3. Record the result in the URDF as `<assembly_part>` and
   `<assembly_slot>` elements.

That third step is the important one. It leaves a **manifest** in the URDF
saying what was fitted and where. Downstream tooling reads the manifest
rather than resolving the config a second time:

- the Gazebo composition,
- the bridge generator,
- the `holybro_parts.assembly` config check.

## Gazebo

`x500_gazebo` runs the same resolution again, this time with Gazebo
emitters. A propeller gets its motor plugin and a GPS part its NavSat
sensor, wherever the config happened to mount them. Since the model and
the bridge come out of one resolution, the generated bridge cannot
disagree with the model it is bridging.

## Shared machinery

The part contract, `assembly.xacro` and the manifest check are shared with
[bluerobotics_models](https://honurobotics.github.io/bluerobotics_models/),
where the design is documented in depth (Slots and assembly, Gazebo
composition). Extracting the machinery into a common package is planned.

## Assets

Every visual is a glTF part (`.glb`) built to the
[Honu glTF Asset Profile](https://github.com/HonuRobotics/gltf-robotics):
one part per file, in glTF's own axes, with its origin on a named datum and
its PBR materials embedded. Every part is modeled by script from the kit's
dimensions.
`holybro_parts/models/README.md` lists each part, its datum and its source.

A glTF visual needs a fixed rotation onto the link's axes, and the two
consumers differ: RViz rolls glTF onto ROS axes as it loads, Gazebo does
not. `part_visual` (in `parts.xacro`) writes the right rotation for each,
and `x500_gazebo` expands its own copy of the URDF with `gltf_up:=z`.

The slot positions are the kit's measured ones. The inertias and motor
constants are still PX4's matched, hover tuned x500 set (BSD 3 Clause,
`holybro_parts/models/LICENSE`).
