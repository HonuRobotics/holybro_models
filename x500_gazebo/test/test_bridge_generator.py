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
"""Unit tests for the ros_gz bridge config generator (pure Python, no xacro)."""

import importlib.util
from pathlib import Path
import subprocess
import sys

from ament_index_python.packages import get_package_prefix  # noqa: I100

_SCRIPT = (Path(get_package_prefix('x500_gazebo'))
           / 'lib' / 'x500_gazebo' / 'generate_bridge_config.py')
_spec = importlib.util.spec_from_file_location('bridge_gen', _SCRIPT)
bridge_gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bridge_gen)

# Airframe topics, always present (the flight sensors belong to the
# airframe, not to a fitted part).
ALWAYS = {'/clock', '/joint_states', '/x500/imu', '/x500/air_pressure', '/x500/mag'}


def entries_for(cfg, instances):
    """Run the generator and index the entries by ros topic."""
    entries = bridge_gen.bridge_entries(cfg, instances)
    return {e['ros_topic_name']: e for e in entries}


def test_airframe_sensors_always_bridged():
    """Clock, joint states and the airframe sensors exist even with no parts."""
    entries = entries_for({}, [])
    assert set(entries) == ALWAYS
    imu = entries['/x500/imu']
    assert imu['ros_type_name'] == 'sensor_msgs/msg/Imu'
    assert imu['gz_type_name'] == 'gz.msgs.IMU'
    assert 'lazy' not in entries['/clock']
    assert imu['lazy'] is True


def test_gps_part_bridges_its_fix():
    """A GPS instance (defaults included) produces its NavSatFix entry, lazily."""
    entries = entries_for({}, [('x500_airframe', 'base_link'), ('gps_mast', 'gps')])
    fix = entries['/x500/gps/fix']
    assert fix['ros_type_name'] == 'sensor_msgs/msg/NavSatFix'
    assert fix['lazy'] is True
    # A renamed or extra instance follows its name.
    assert '/x500/rtk/fix' in entries_for({}, [('gps_mast', 'rtk')])


def test_geometry_only_parts_produce_nothing():
    """Parts without simulated topics add no bridge entries."""
    instances = [('battery_4s', 'battery'), ('companion_computer', 'companion'),
                 ('gimbal_camera', 'gimbal'), ('prop_1345_ccw', 'rotor_0')]
    assert set(entries_for({}, instances)) == ALWAYS


def test_topic_and_namespace_overrides():
    """Gz_topic/ros_topic > topic > /<namespace>/<name>, matched by instance."""
    cfg = {'topic_namespace': 'uav_a', 'parts': [
        {'slot': 'gps', 'type': 'gps_mast',
         'gz_topic': 'uav_a/gps_raw', 'ros_topic': '/sensors/gps'}]}
    entries = entries_for(cfg, [('gps_mast', 'gps')])
    fix = entries['/sensors/gps/fix']
    assert fix['gz_topic_name'] == '/uav_a/gps_raw/fix'
    assert '/uav_a/imu' in entries and '/x500/imu' not in entries


def test_extra_bridge_topics_verbatim():
    """Extra_bridge_topics entries are appended untouched (e.g. the motor bus)."""
    extra = {'ros_topic_name': '/x500/motors',
             'gz_topic_name': '/x500/command/motor_speed',
             'ros_type_name': 'actuator_msgs/msg/Actuators',
             'gz_type_name': 'gz.msgs.Actuators', 'direction': 'ROS_TO_GZ'}
    cfg = {'extra_bridge_topics': [dict(extra)]}
    assert entries_for(cfg, [])['/x500/motors'] == extra


def test_cli_rejects_a_config_that_matches_nothing(tmp_path):
    """The generator runs the assembly check: a stray entry fails with the reason."""
    urdf = ('<robot name="x"><assembly_part type="x500_airframe" name="base_link" parent=""/>'
            '<assembly_slot of="base_link" name="gps"/><link name="base_link"/></robot>')
    (tmp_path / 'v.urdf').write_text(urdf)
    (tmp_path / 'bad.yaml').write_text('parts:\n  - {slot: gpss, type: none}\n')
    out = subprocess.run([sys.executable, str(_SCRIPT), str(tmp_path / 'bad.yaml'),
                          str(tmp_path / 'v.urdf'), str(tmp_path / 'out.yaml')],
                         capture_output=True, text=True)
    assert out.returncode != 0 and "'gpss' of 'base_link'" in out.stderr, out.stderr
    assert not (tmp_path / 'out.yaml').exists()
