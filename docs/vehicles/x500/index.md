# X500

The [Holybro X500 V2](https://holybro.com/products/x500-v2-kits) development
kit quadcopter, assembled from the `holybro_parts` library.

```{toctree}
:maxdepth: 1

running
actuators
sensors
configuration
```

## The default vehicle

Launch the X500 without a config and you get the airframe with:

- **four 1345 propellers**, in the PX4 quad X layout: rotors 0 and 1 spin
  counter clockwise, rotors 2 and 3 clockwise.
- **the 4S battery**.
- **the GPS mast**.

That is enough to fly. Two more parts sit in the catalog unfitted, the
companion computer and the gimbal camera, and nothing above is fixed: fit
an optional part, swap a default for another accepted type, or leave a
default off entirely. See [Configuration](configuration.md).
