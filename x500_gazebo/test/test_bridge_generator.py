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

from ament_index_python.packages import get_package_prefix  # noqa: I100

_SCRIPT = (Path(get_package_prefix('x500_gazebo'))
           / 'lib' / 'x500_gazebo' / 'generate_bridge_config.py')
_spec = importlib.util.spec_from_file_location('bridge_gen', _SCRIPT)
bridge_gen = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(bridge_gen)


def entries_for(cfg):
    """Run the generator and index the entries by ros topic."""
    entries = bridge_gen.bridge_entries(cfg)
    return {e['ros_topic_name']: e for e in entries}


def test_flight_sensors_always_bridged():
    """Clock + the four flight sensors exist even with no accessories."""
    entries = entries_for({'accessories': []})
    assert set(entries) == {'/clock', '/x500/imu', '/x500/air_pressure',
                            '/x500/mag', '/x500/gps'}
    imu = entries['/x500/imu']
    assert imu['ros_type_name'] == 'sensor_msgs/msg/Imu'
    assert imu['gz_type_name'] == 'gz.msgs.IMU'
    assert entries['/x500/gps']['ros_type_name'] == 'sensor_msgs/msg/NavSatFix'


def test_lazy_default_clock_eager():
    """Sensor entries are lazy, /clock is not."""
    entries = entries_for({})
    assert 'lazy' not in entries['/clock']
    assert entries['/x500/imu']['lazy'] is True


def test_namespace_override():
    """topic_namespace renames every sensor topic."""
    entries = entries_for({'topic_namespace': 'uav_a'})
    assert '/uav_a/imu' in entries and '/x500/imu' not in entries


def test_accessories_produce_nothing_yet():
    """Current accessory types carry no simulated topics."""
    cfg = {'accessories': [
        {'type': 'battery', 'name': 'battery', 'xyz': '0 0 0',
         'rpy': '0 0 0'},
        {'type': 'gimbal', 'name': 'gimbal', 'xyz': '0 0 0',
         'rpy': '0 0 0'}]}
    assert len(entries_for(cfg)) == 5  # clock + 4 flight sensors


def test_extra_bridge_topics_verbatim():
    """extra_bridge_topics entries are appended untouched."""
    extra = {'ros_topic_name': '/x500/motors',
             'gz_topic_name': '/x500/command/motor_speed',
             'ros_type_name': 'actuator_msgs/msg/Actuators',
             'gz_type_name': 'gz.msgs.Actuators', 'direction': 'ROS_TO_GZ'}
    cfg = {'extra_bridge_topics': [dict(extra)]}
    assert entries_for(cfg)['/x500/motors'] == extra
