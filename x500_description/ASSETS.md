# X500 assets

The meshes under `meshes/` are **temporary placeholders** reused from PX4's
[`PX4-gazebo-models`](https://github.com/PX4/PX4-gazebo-models) `x500` model:

| File | Role |
|------|------|
| `NXP-HGD-CF.dae` (+ `CF.png`) | Carbon frame (diffuse texture embedded in the .dae) |
| `5010Base.dae` | Static lower motor housing (×4) |
| `5010Bell.dae` | Rotating motor bell (on each rotor) |
| `1345_prop_ccw.stl` / `1345_prop_cw.stl` | 10×4.5 propellers |

**License: BSD-3-Clause** ("Copyright (c) 2022, PX4 Autopilot"); see
`meshes/LICENSE`. These are **redistributable** (unlike the BlueBoat placeholders),
provided the copyright/notice is retained.

**Caveat:** PX4's frame mesh is the **NXP HoverGames** body, geometrically close
to but **not** the exact Holybro X500 shell.

Inertias, collision boxes, rotor poses and the quad-X spin convention are copied
from the PX4 model (a matched, hover-tuned set with the motor constants used in
`x500_gazebo`).
