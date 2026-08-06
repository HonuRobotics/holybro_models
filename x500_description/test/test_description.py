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
"""Generation-pipeline tests: config yaml -> URDF (validity, quad-X, catalog)."""

from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from ament_index_python.packages import get_package_share_directory

SHARE = Path(get_package_share_directory('x500_description'))
TOP_XACRO = SHARE / 'urdf' / 'x500.urdf.xacro'
ACCESSORIES_XACRO = SHARE / 'urdf' / 'accessories.xacro'

# Full accessory catalog: type -> demo pose.
CATALOG = {
    'battery': '0 0 -0.045',
    'companion_computer': '-0.05 0 0.045',
    'gps_mast': '-0.11 0 0.045',
    'gimbal': '0.12 0 -0.05',
}


def make_config(accessories=()):
    """Return vehicle-config yaml text for the given loadout."""
    lines = ['accessories:']
    if not accessories:
        lines = ['accessories: []']
    for type_name, name, xyz in accessories:
        lines.append(
            f'  - {{type: {type_name}, name: {name}, '
            f'xyz: "{xyz}", rpy: "0 0 0"}}')
    return '\n'.join(lines) + '\n'


def full_catalog_accessories():
    """Return one accessory entry per catalog type."""
    return [(t, f'acc_{t}', pose) for t, pose in CATALOG.items()]


def xacro_output(config_text):
    """Run xacro on the top-level file with the given config; return the URDF."""
    with tempfile.NamedTemporaryFile('w', suffix='.yaml', delete=False) as f:
        f.write(config_text)
        config_path = f.name
    out = subprocess.run(
        ['xacro', str(TOP_XACRO), f'config_file:={config_path}'],
        capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, (
        f'xacro failed ({out.returncode})\n--- stderr ---\n{out.stderr}')
    return out.stdout


def generate_urdf(config_text):
    """Generate the URDF for a config and return the parsed XML root."""
    return ET.fromstring(xacro_output(config_text))


def link_names(root):
    """Return the set of link names in a URDF tree."""
    return {link.get('name') for link in root.findall('link')}


def test_default_config_dev_kit_loadout():
    """The shipped default builds 4 rotors + the dev-kit accessories."""
    default = (SHARE / 'config' / 'x500.yaml').read_text()
    links = link_names(generate_urdf(default))
    rotors = {li for li in links if re.fullmatch(r'rotor_\d', li)}
    assert len(rotors) == 4
    assert {'battery', 'companion', 'gps', 'gimbal'} <= links


def test_quad_x_spin_convention():
    """PX4 quad_x chirality: ccw props on rotors 0/1, cw on 2/3."""
    text = xacro_output(make_config())
    root = ET.fromstring(text)
    for number in range(4):
        rotor = next(li for li in root.findall('link')
                     if li.get('name') == f'rotor_{number}')
        mesh = rotor.find('.//mesh').get('filename')
        expected = 'ccw' if number < 2 else 'cw'
        assert f'1345_prop_{expected}' in mesh, f'rotor_{number} wrong prop'
    joints = {j.get('name'): j.get('type') for j in root.findall('joint')}
    for number in range(4):
        assert joints[f'rotor_{number}_joint'] == 'continuous'


def test_catalog_completeness_and_toggle():
    """Every accessory type generates its link, and only when configured."""
    empty_links = link_names(generate_urdf(make_config()))
    for type_name, pose in CATALOG.items():
        name = f'acc_{type_name}'
        root = generate_urdf(make_config([(type_name, name, pose)]))
        assert name in link_names(root), f'{type_name} missing link'
        assert name not in empty_links
    # The dispatcher invokes the config type directly as a macro, so every
    # catalog type must have a same-named macro.
    macros = set(re.findall(r'<xacro:macro name="([a-z]\w*)"',
                            ACCESSORIES_XACRO.read_text()))
    assert set(CATALOG) <= macros, f'missing macros: {set(CATALOG) - macros}'


def test_mesh_references_resolve():
    """Every package:// mesh URI in the generated URDF exists on disk."""
    root = generate_urdf(make_config(full_catalog_accessories()))
    uris = {m.get('filename') for m in root.findall('.//mesh')}
    assert uris
    for uri in uris:
        package, _, rel = uri.removeprefix('package://').partition('/')
        path = Path(get_package_share_directory(package)) / rel
        assert path.is_file(), f'missing mesh {uri}'


def test_check_urdf_accepts_generated():
    """The urdfdom validator accepts the generated URDF."""
    text = xacro_output(make_config(full_catalog_accessories()))
    with tempfile.NamedTemporaryFile('w', suffix='.urdf', delete=False) as f:
        f.write(text)
        urdf_path = f.name
    out = subprocess.run(['check_urdf', urdf_path], capture_output=True,
                         text=True, timeout=30)
    assert out.returncode == 0, (
        f'check_urdf rejected the URDF ({out.returncode})\n'
        f'--- stdout ---\n{out.stdout}\n--- stderr ---\n{out.stderr}')
