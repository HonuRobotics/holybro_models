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
"""configure_vehicle.py: every loadout artifact from one config, at any time."""

import os
from pathlib import Path
import subprocess
import tempfile
import xml.etree.ElementTree as ET

from ament_index_python.packages import (get_package_prefix,
                                         get_package_share_directory)
import yaml

GZ_SHARE = Path(get_package_share_directory('x500_gazebo'))
DESC_SHARE = Path(get_package_share_directory('x500_description'))
TOOL = (Path(get_package_prefix('x500_gazebo')) / 'lib' / 'x500_gazebo'
        / 'configure_vehicle.py')
DEFAULT_CONFIG = DESC_SHARE / 'config' / 'x500.yaml'


def configure(config_path, out_dir):
    """Run the tool; fail the test with its stderr."""
    out = subprocess.run([str(TOOL), '--config', str(config_path), '--out-dir', str(out_dir)],
                         capture_output=True, text=True, timeout=180)
    assert out.returncode == 0, f'configure_vehicle failed:\n{out.stderr}'
    return Path(out_dir)


def links(urdf_path):
    """Return the link names of a URDF file."""
    return {li.get('name') for li in ET.parse(urdf_path).getroot().findall('link')}


def test_default_config_reproduces_the_installed_artifacts(tmp_path):
    """Run on the shipped config, the tool regenerates what the build installed."""
    out = configure(DEFAULT_CONFIG, tmp_path / 'v')
    for name in ('x500.urdf', 'model.sdf', 'model.config', 'ros_gz_bridge.yaml',
                 'robot_description.yaml'):
        assert (out / name).is_file(), f'{name} not generated'
    assert links(out / 'x500.urdf') == links(DESC_SHARE / 'urdf' / 'x500.urdf')
    assert yaml.safe_load((out / 'ros_gz_bridge.yaml').read_text()) == \
        yaml.safe_load((GZ_SHARE / 'config' / 'ros_gz_bridge.yaml').read_text())
    generated = ET.parse(out / 'model.sdf').getroot()
    installed = ET.parse(GZ_SHARE / 'models' / 'x500' / 'model.sdf').getroot()
    assert [s.get('name') for s in generated.iter('sensor')] == \
        [s.get('name') for s in installed.iter('sensor')]
    assert len(list(generated.iter('plugin'))) == len(list(installed.iter('plugin')))
    # The generated model merges the generated URDF.
    uri = next(generated.iter('include')).find('uri').text
    assert uri == f'file://{out / "x500.urdf"}'


def test_custom_loadout_flows_to_every_artifact(tmp_path):
    """A different loadout changes URDF, model and bridge consistently."""
    cfg = yaml.safe_load(DEFAULT_CONFIG.read_text())
    cfg['parts'] = [{'slot': 'gps', 'type': 'none'},
                    {'slot': 'gimbal', 'type': 'gimbal_camera'}]
    config = tmp_path / 'custom.yaml'
    config.write_text(yaml.safe_dump(cfg, sort_keys=False))
    out = configure(config, tmp_path / 'v')
    urdf_links = links(out / 'x500.urdf')
    assert 'gimbal' in urdf_links and 'gps' not in urdf_links
    model = ET.parse(out / 'model.sdf').getroot()
    assert not [s for s in model.iter('sensor') if s.get('type') == 'navsat']
    topics = {e['ros_topic_name'] for e in
              yaml.safe_load((out / 'ros_gz_bridge.yaml').read_text())}
    assert '/x500/gps/fix' not in topics
    assert '/x500/imu' in topics


def test_mismatched_config_fails_with_the_reason(tmp_path):
    """A slot entry that matches nothing fails the tool (and so the launch)."""
    cfg = yaml.safe_load(DEFAULT_CONFIG.read_text())
    cfg['parts'] = [{'slot': 'gpss', 'type': 'none'}]
    config = tmp_path / 'custom.yaml'
    config.write_text(yaml.safe_dump(cfg, sort_keys=False))
    out = subprocess.run([str(TOOL), '--config', str(config), '--out-dir', str(tmp_path / 'v')],
                         capture_output=True, text=True, timeout=180)
    assert out.returncode != 0 and "unknown slot 'gpss'" in out.stderr, out.stderr


def test_cache_mode_prints_only_the_directory():
    """--cache writes under $ROS_HOME, keyed by the config, and prints the path only."""
    with tempfile.TemporaryDirectory() as ros_home:
        env = dict(os.environ, ROS_HOME=ros_home)
        out = subprocess.run([str(TOOL), '--config', str(DEFAULT_CONFIG), '--cache'],
                             capture_output=True, text=True, timeout=180, env=env)
        assert out.returncode == 0, out.stderr
        path = Path(out.stdout)
        assert path.is_dir() and (path / 'model.sdf').is_file()
        assert out.stdout == str(path), 'stdout must be the bare path (launch uses it)'
        assert path.parent == Path(ros_home) / 'x500_gazebo'
        # Same config, same directory: nothing piles up launch after launch.
        again = subprocess.run([str(TOOL), '--config', str(DEFAULT_CONFIG), '--cache'],
                               capture_output=True, text=True, timeout=180, env=env)
        assert again.stdout == out.stdout
