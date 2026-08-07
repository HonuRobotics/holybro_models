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
"""Generation tests for the composed model: rotors, sensors, hover margin."""

import importlib.util
from pathlib import Path
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from ament_index_python.packages import (get_package_prefix,
                                         get_package_share_directory)
import yaml

GZ_SHARE = Path(get_package_share_directory('x500_gazebo'))
DESC_SHARE = Path(get_package_share_directory('x500_description'))
MODEL_XACRO = GZ_SHARE / 'model.sdf.xacro'
URDF_XACRO = DESC_SHARE / 'urdf' / 'x500.urdf.xacro'

_SCRIPT = (Path(get_package_prefix('x500_gazebo'))
           / 'lib' / 'x500_gazebo' / 'generate_bridge_config.py')
_spec = importlib.util.spec_from_file_location('bridge_gen', _SCRIPT)
bridge_gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bridge_gen)

GRAVITY = 9.81


def xacro(top_file, config_text):
    """Run xacro with a temp config; return the parsed XML root and text."""
    with tempfile.NamedTemporaryFile('w', suffix='.yaml', delete=False) as f:
        f.write(config_text)
        config_path = f.name
    out = subprocess.run(
        ['xacro', str(top_file), f'config_file:={config_path}'],
        check=True, capture_output=True, text=True, timeout=60)
    return ET.fromstring(out.stdout), out.stdout


def default_config():
    """Return the shipped default vehicle config text."""
    return (DESC_SHARE / 'config' / 'x500.yaml').read_text()


def motor_plugins(root):
    """Return the MulticopterMotorModel plugin elements."""
    return [p for p in root.iter('plugin')
            if p.get('filename') == 'gz-sim-multicopter-motor-model-system']


def test_model_generation_rotors_and_sensors():
    """Four motors with the quad_x spin sequence; flight sensors present."""
    root, text = xacro(MODEL_XACRO, default_config())
    assert 'xacro:' not in text and 'xmlns:xacro' not in text
    motors = motor_plugins(root)
    assert len(motors) == 4
    by_number = {int(m.find('motorNumber').text):
                 m.find('turningDirection').text for m in motors}
    assert by_number == {0: 'ccw', 1: 'ccw', 2: 'cw', 3: 'cw'}
    sensors = {s.get('type') for s in root.iter('sensor')}
    assert sensors == {'imu', 'air_pressure', 'magnetometer', 'navsat'}


def test_hover_thrust_margin():
    """Max total thrust exceeds the default all-up weight with margin."""
    root, _ = xacro(MODEL_XACRO, default_config())
    motor = motor_plugins(root)[0]
    k = float(motor.find('motorConstant').text)
    omega_max = float(motor.find('maxRotVelocity').text)
    max_thrust = 4 * k * omega_max ** 2
    urdf_root, _ = xacro(URDF_XACRO, default_config())
    mass = sum(float(m.get('value'))
               for m in urdf_root.findall('.//inertial/mass'))
    ratio = max_thrust / (mass * GRAVITY)
    assert ratio > 1.3, f'thrust/weight {ratio:.2f} cannot hover with margin'


def test_plugin_references_survive_lumping():
    """
    Plugin joint/link refs exist in the POST-lumping converted model.

    gz's URDF conversion lumps fixed joints away, so references must be
    validated against the converted model, not the raw URDF.
    """
    sdf_root, _ = xacro(MODEL_XACRO, default_config())
    urdf_root, urdf_text = xacro(URDF_XACRO, default_config())
    joint_refs = {ref.text for ref in sdf_root.iter('jointName')}
    link_refs = {ref.text for ref in sdf_root.iter('linkName')}
    assert joint_refs and link_refs
    with tempfile.NamedTemporaryFile('w', suffix='.urdf', delete=False) as f:
        f.write(urdf_text)
        urdf_path = f.name
    out = subprocess.run(['gz', 'sdf', '-p', urdf_path], check=True,
                         capture_output=True, text=True, timeout=60)
    converted = ET.fromstring(out.stdout)
    surviving_joints = {j.get('name') for j in converted.iter('joint')}
    surviving_links = {li.get('name') for li in converted.iter('link')}
    assert joint_refs <= surviving_joints, (
        f'plugin joints lumped away: {joint_refs - surviving_joints}')
    assert link_refs <= surviving_links, (
        f'plugin links lumped away: {link_refs - surviving_links}')


def test_sensor_and_bridge_topics_agree():
    """Model gz topics equal generated bridge gz topics, by construction."""
    for config in (default_config(),
                   default_config().replace('topic_namespace: x500',
                                            'topic_namespace: uav_a')):
        root, _ = xacro(MODEL_XACRO, config)
        sdf_topics = {t.text if t.text.startswith('/') else '/' + t.text
                      for t in root.iter('topic')}
        entries = bridge_gen.bridge_entries(yaml.safe_load(config))
        bridge_topics = {e['gz_topic_name'] for e in entries} - {'/clock'}
        assert sdf_topics == bridge_topics


def test_default_config_covers_catalog():
    """The shipped dev-kit loadout exercises every accessory type."""
    xacro_text = (DESC_SHARE / 'urdf' / 'accessories.xacro').read_text()
    catalog = set(re.findall(r'<xacro:macro name="([a-z]\w*)"', xacro_text))
    catalog -= {'mount_accessories'}
    config_types = {a['type']
                    for a in yaml.safe_load(default_config())['accessories']}
    assert config_types == catalog, (
        f'default loadout drift: missing {catalog - config_types}, '
        f'unknown {config_types - catalog}')


def test_sensor_frame_ids_resolve_in_tf():
    """
    Every sensor's <frame_id> names a frame TF actually carries.

    TF comes from the URDF via robot_state_publisher; gz's derived SDF scoped
    ids and the sensor wrapper links are in neither, so an unset frame_id
    yields messages no lookup_transform can resolve. The deprecated
    gz_frame_id spelling also fails this test on purpose.
    """
    sdf_root, _ = xacro(MODEL_XACRO, default_config())
    urdf_root, _ = xacro(URDF_XACRO, default_config())
    urdf_links = {li.get('name') for li in urdf_root.findall('link')}
    sensors = list(sdf_root.iter('sensor'))
    assert sensors
    for sensor in sensors:
        frame = sensor.find('frame_id')
        assert frame is not None, (
            f'sensor {sensor.get("name")} sets no <frame_id>')
        assert frame.text in urdf_links, (
            f'sensor {sensor.get("name")} publishes frame_id {frame.text!r}, '
            f'which robot_state_publisher never puts in TF')
