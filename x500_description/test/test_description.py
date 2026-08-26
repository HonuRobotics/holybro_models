# Copyright 2026 Honu Robotics
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Generation pipeline tests: config yaml + part slots -> URDF."""

from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from ament_index_python.packages import get_package_share_directory
from holybro_parts import assembly
import yaml

SHARE = Path(get_package_share_directory('x500_description'))
PARTS_SHARE = Path(get_package_share_directory('holybro_parts'))
TOP_XACRO = SHARE / 'urdf' / 'x500.urdf.xacro'
PARTS_XACRO = PARTS_SHARE / 'urdf' / 'parts.xacro'

DEFAULT_CONFIG = (SHARE / 'config' / 'x500.yaml').read_text()

# What the airframe slots fill with when the config is silent.
DEFAULT_LOADOUT = {'base_link': 'x500_airframe',
                   'rotor_0': 'prop_1345_ccw', 'rotor_1': 'prop_1345_ccw',
                   'rotor_2': 'prop_1345_cw', 'rotor_3': 'prop_1345_cw',
                   'battery': 'battery_4s', 'gps': 'gps_mast'}


def catalog():
    """Part types the library offers: the include list of parts.xacro."""
    names = re.findall(r'/urdf/([a-z0-9_]+)\.urdf\.xacro', PARTS_XACRO.read_text())
    return sorted(set(names) - {'part_probe'})


def make_config(parts=(), slots=()):
    """Vehicle config yaml: airframe base, overrides/additions."""
    cfg = {'base': {'type': 'x500_airframe', 'name': 'base_link'},
           'parts': [dict(p) for p in parts]}
    if slots:
        cfg['slots'] = [dict(s) for s in slots]
    return yaml.safe_dump(cfg, sort_keys=False)


def xacro_run(config_text):
    """Run xacro on the top-level file with the given config."""
    with tempfile.NamedTemporaryFile('w', suffix='.yaml', delete=False) as f:
        f.write(config_text)
        config_path = f.name
    return subprocess.run(
        ['xacro', str(TOP_XACRO), f'config_file:={config_path}'],
        capture_output=True, text=True, timeout=120)


def xacro_output(config_text):
    """Expand; fail the test with xacro's stderr on error."""
    out = xacro_run(config_text)
    assert out.returncode == 0, (
        f'xacro failed ({out.returncode})\n--- stderr ---\n{out.stderr}')
    return out.stdout


def generate_urdf(config_text):
    """Generate the URDF for a config and return the parsed XML root."""
    return ET.fromstring(xacro_output(config_text))


def expect_failure(config_text, fragment):
    """Assert the expansion fails and names the problem."""
    out = xacro_run(config_text)
    assert out.returncode != 0, 'xacro accepted a config it should reject'
    assert fragment in out.stderr, (
        f'expected {fragment!r} in the error, got:\n{out.stderr[-800:]}')


def link_names(root):
    """Return the set of link names in a URDF tree."""
    return {link.get('name') for link in root.findall('link')}


def manifest(root):
    """Map instance name -> part type from the <assembly_part> elements."""
    return {e.get('name'): e.get('type') for e in root.findall('assembly_part')}


def test_default_config_is_the_dev_kit_loadout():
    """The shipped default builds 4 rotors + battery + GPS from slot defaults."""
    root = generate_urdf(DEFAULT_CONFIG)
    assert manifest(root) == DEFAULT_LOADOUT
    assert set(DEFAULT_LOADOUT) <= link_names(root)


def test_quad_x_spin_convention():
    """PX4 quad_x chirality: ccw props on rotors 0/1, cw on 2/3, continuous."""
    root = generate_urdf(DEFAULT_CONFIG)
    parts = manifest(root)
    for number in range(4):
        expected = 'ccw' if number < 2 else 'cw'
        assert parts[f'rotor_{number}'] == f'prop_1345_{expected}'
    joints = {j.get('name'): j.get('type') for j in root.findall('joint')}
    for number in range(4):
        # Propellers declare a drive table, so they land on continuous joints.
        assert joints[f'rotor_{number}_joint'] == 'continuous'


def test_slot_override_and_none():
    """A slot entry can empty a slot or fill one that has no default."""
    root = generate_urdf(make_config([{'slot': 'gps', 'type': 'none'},
                                      {'slot': 'gimbal', 'type': 'gimbal_camera'},
                                      {'slot': 'companion', 'type': 'companion_computer'}]))
    parts = manifest(root)
    assert 'gps' not in parts
    assert parts['gimbal'] == 'gimbal_camera'
    assert parts['companion'] == 'companion_computer'


def test_slot_rejects_parts_that_do_not_fit():
    """A type outside the slot's accepts list fails the expansion."""
    expect_failure(make_config([{'slot': 'rotor_0', 'type': 'prop_1345_cw'}]),
                   'does not fit')


def test_unknown_slot_on_base_fails():
    """A typo in the slot name fails the expansion naming it."""
    expect_failure(make_config([{'slot': 'nope', 'type': 'gimbal_camera'}]),
                   "unknown slot 'nope'")


def test_bare_on_key_is_rejected():
    """A bare on: key is the YAML boolean true; the expansion says so."""
    text = make_config() + 'slots:\n  - {on: base_link, name: x, xyz: "0 0 0"}\n'
    expect_failure(text, "bare 'on:' key")


def test_free_placement_and_adhoc_slot():
    """Free placements and ad hoc slots work as in the config schema."""
    root = generate_urdf(make_config(
        parts=[{'type': 'battery_4s', 'name': 'battery_aft',
                'xyz': '-0.09 0 -0.045', 'rpy': '0 0 0'},
               {'slot': 'camera', 'type': 'gimbal_camera', 'name': 'cam'}],
        slots=[{'of': 'base_link', 'name': 'camera', 'xyz': '0.12 0 0.02'}]))
    links = link_names(root)
    assert {'battery_aft', 'cam', 'base_link_camera'} <= links


def test_check_catches_what_the_expansion_cannot():
    """Entries matching nothing deeper down, duplicate names, unknown keys."""
    cfg = yaml.safe_load(make_config([{'slot': 'gps', 'of': 'nowhere', 'type': 'none'}]))
    root = generate_urdf(yaml.safe_dump(cfg))
    found = assembly.problems(cfg, root)
    assert any("no instance named 'nowhere'" in f for f in found), found
    cfg = yaml.safe_load(make_config([{'slot': 'gps', 'type': 'gps_mast', 'bogus': 1}]))
    found = assembly.problems(cfg, generate_urdf(yaml.safe_dump(cfg)))
    assert any("['bogus']" in f for f in found), found
    cfg = yaml.safe_load(DEFAULT_CONFIG)
    assert assembly.problems(cfg, generate_urdf(DEFAULT_CONFIG)) == []


def test_catalog_covered_by_defaults_plus_overrides():
    """Every catalog type is reachable: default loadout + the no-default slots."""
    root = generate_urdf(make_config([{'slot': 'companion', 'type': 'companion_computer'},
                                      {'slot': 'gimbal', 'type': 'gimbal_camera'}]))
    assert set(manifest(root).values()) == set(catalog())


def test_mesh_references_resolve():
    """Every package:// mesh URI in the generated URDF exists on disk."""
    root = generate_urdf(DEFAULT_CONFIG)
    uris = {m.get('filename') for m in root.findall('.//mesh')}
    assert uris
    for uri in uris:
        assert uri.startswith('package://holybro_parts/'), uri
        rel = uri.replace('package://holybro_parts/', '')
        assert (PARTS_SHARE / rel).is_file(), f'missing mesh {uri}'


def test_check_urdf_accepts_generated():
    """The generated URDF parses with urdfdom's check_urdf."""
    text = xacro_output(DEFAULT_CONFIG)
    with tempfile.NamedTemporaryFile('w', suffix='.urdf', delete=False) as f:
        f.write(text)
        path = f.name
    out = subprocess.run(['check_urdf', path], capture_output=True, text=True,
                         timeout=60)
    assert out.returncode == 0, f'check_urdf rejected the URDF:\n{out.stderr}'
