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
Headless Gazebo integration: world loads, sensors publish, physics steps.

The X500's flight sensors (IMU, baro, mag, GPS) need no rendering, so every
assertion here is a hard requirement: a missing gz CLI fails the suite rather
than skipping it, and a broken environment cannot report green.
"""

import os
from pathlib import Path
import uuid

from ament_index_python.packages import get_package_share_directory
from conftest import launch_sim, make_cli, poll_until
import pytest

WORLD = (Path(get_package_share_directory('x500_gazebo'))
         / 'worlds' / 'x500_playground.sdf')
WORLD_NAME = 'x500_playground'

gz = make_cli('gz')


@pytest.fixture(scope='module')
def sim(request):
    """Start a headless gz server on an isolated partition; yield its env."""
    env = dict(os.environ, GZ_PARTITION=f'test_{uuid.uuid4().hex[:8]}')
    # -v 3 so warnings and messages (not just errors) reach the audited log.
    return launch_sim(
        request, 'gz sim',
        ['gz', 'sim', '-s', '-r', '-v', '3', str(WORLD)], env,
        ready=lambda e: 'x500' in gz(e, 'model', '--list')[1])


def test_model_loaded(sim):
    """The composed model is in the world."""
    _, out, _ = gz(sim, 'model', '--list')
    assert 'x500' in out


def test_sensor_topics_advertised(sim):
    """The flight-sensor topics and world clock are advertised."""
    needed = ('/x500/imu', '/x500/air_pressure', '/x500/mag', '/x500/gps/fix',
              f'/world/{WORLD_NAME}/clock')
    poll_until(
        lambda: all(t in gz(sim, 'topic', '-l')[1] for t in needed), 30,
        lambda: f'missing topics; last listing:\n{gz(sim, "topic", "-l")[1]}')


def test_physics_steps(sim):
    """Simulation iterations advance (systems survive stepping)."""
    def advancing():
        code, out, _ = gz(sim, 'topic', '-e', '-t',
                          f'/world/{WORLD_NAME}/stats', '-n', '1', timeout=15)
        return (code == 0 and 'iterations' in out
                and int(out.split('iterations:')[1].split()[0]) > 0)
    poll_until(advancing, 30, 'sim iterations did not advance')


def test_imu_publishes_data(sim):
    """The IMU streams real data."""
    code, out, err = gz(sim, 'topic', '-e', '-t', '/x500/imu', '-n', '1',
                        timeout=30)
    assert code == 0 and 'linear_acceleration' in out, f'no IMU data\n{err}'


def test_gps_publishes_fix(sim):
    """The NavSat sensor resolves the world spherical coordinates to a fix."""
    code, out, err = gz(sim, 'topic', '-e', '-t', '/x500/gps/fix', '-n', '1',
                        timeout=30)
    assert code == 0 and 'latitude_deg' in out, f'no GPS fix\n{err}'
