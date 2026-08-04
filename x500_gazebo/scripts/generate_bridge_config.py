#!/usr/bin/env python3
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
"""
Generate the ros_gz bridge config from the vehicle config.

Run at build time (see CMakeLists.txt): emits /clock and the flight sensors
(IMU, air pressure, magnetometer, NavSat), which are always present on the
airframe. Accessory-driven topics can be added to ACCESSORY_TOPICS as sensor
accessories (e.g. a gimbal camera) gain simulation behaviour. The motor
command bus (gz.msgs.Actuators) is deliberately NOT bridged: that is the
control input, out of scope for the model; use `extra_bridge_topics` to
expose it if needed.

Usage: generate_bridge_config.py <vehicle_config.yaml> <output_bridge.yaml>
"""

import sys

import yaml

FLIGHT_SENSORS = [
    ('imu', 'sensor_msgs/msg/Imu', 'gz.msgs.IMU'),
    ('air_pressure', 'sensor_msgs/msg/FluidPressure', 'gz.msgs.FluidPressure'),
    ('mag', 'sensor_msgs/msg/MagneticField', 'gz.msgs.Magnetometer'),
    ('gps', 'sensor_msgs/msg/NavSatFix', 'gz.msgs.NavSat'),
]

# type -> [(topic suffix, ROS type, gz type, direction)]
ACCESSORY_TOPICS = {}


def absolute(topic):
    """Return the topic with a leading slash."""
    return topic if topic.startswith('/') else '/' + topic


def bridge_entries(cfg):
    """Build the list of bridge entries for a parsed vehicle config."""
    ns = cfg.get('topic_namespace', 'x500')
    entries = [{
        'ros_topic_name': '/clock',
        'gz_topic_name': '/clock',
        'ros_type_name': 'rosgraph_msgs/msg/Clock',
        'gz_type_name': 'gz.msgs.Clock',
        'direction': 'GZ_TO_ROS',
    }]
    for suffix, ros_type, gz_type in FLIGHT_SENSORS:
        entries.append({
            'ros_topic_name': absolute(f'{ns}/{suffix}'),
            'gz_topic_name': absolute(f'{ns}/{suffix}'),
            'ros_type_name': ros_type,
            'gz_type_name': gz_type,
            'direction': 'GZ_TO_ROS',
            'lazy': True,
        })
    for acc in cfg.get('accessories') or []:
        default_base = f"{ns}/{acc['name']}"
        gz_base = acc.get('gz_topic', acc.get('topic', default_base))
        ros_base = acc.get('ros_topic', acc.get('topic', default_base))
        for suffix, ros_type, gz_type, direction in \
                ACCESSORY_TOPICS.get(acc['type'], []):
            entry = {
                'ros_topic_name': absolute(f'{ros_base}/{suffix}'),
                'gz_topic_name': absolute(f'{gz_base}/{suffix}'),
                'ros_type_name': ros_type,
                'gz_type_name': gz_type,
                'direction': direction,
            }
            if direction == 'GZ_TO_ROS':
                entry['lazy'] = True
            entry.update(acc.get('bridge') or {})
            entries.append(entry)
    entries.extend(cfg.get('extra_bridge_topics') or [])
    return entries


def main():
    """Read the vehicle config and write the bridge yaml (see module doc)."""
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    with open(sys.argv[1]) as f:
        cfg = yaml.safe_load(f) or {}
    with open(sys.argv[2], 'w') as f:
        f.write('# GENERATED from the vehicle config '
                '(x500_description/config/x500.yaml)\n'
                '# by generate_bridge_config.py. Do not edit; edit the vehicle '
                'config and rebuild.\n')
        yaml.safe_dump(bridge_entries(cfg), f, sort_keys=False)


if __name__ == '__main__':
    main()
