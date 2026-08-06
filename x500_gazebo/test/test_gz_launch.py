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

The X500's flight sensors (IMU, baro, mag, GPS) need no rendering, so the
sensor-data assertions here are hard requirements, not skip-tolerant smoke.
"""

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import uuid

from ament_index_python.packages import get_package_share_directory
import pytest

WORLD = (Path(get_package_share_directory('x500_gazebo'))
         / 'worlds' / 'x500_playground.sdf')
WORLD_NAME = 'x500_playground'


def gz(env, *args, timeout=10):
    """Run a gz CLI command; return (returncode, stdout)."""
    try:
        out = subprocess.run(['gz', *args], env=env, capture_output=True,
                             text=True, timeout=timeout)
        return out.returncode, out.stdout
    except subprocess.TimeoutExpired:
        return -1, ''


@pytest.fixture(scope='module')
def sim(request):
    """Start a headless gz server on an isolated partition; yield its env."""
    if shutil.which('gz') is None:
        pytest.fail('gz CLI not available: the simulation suite cannot run')
    env = dict(os.environ, GZ_PARTITION=f'test_{uuid.uuid4().hex[:8]}')
    log = tempfile.NamedTemporaryFile('w+', suffix='.log', delete=False,
                                      prefix='gz_launch_')
    # -v 3 so warnings and messages (not just errors) reach the audited log.
    proc = subprocess.Popen(['gz', 'sim', '-s', '-r', '-v', '3', str(WORLD)],
                            env=env, stdout=log, stderr=subprocess.STDOUT)

    def fail(message):
        log.flush()
        tail = ''.join(open(log.name).readlines()[-40:])
        pytest.fail(f'{message}\nlast gz output ({log.name}):\n{tail}')

    def teardown():
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=10)
        # Always surface the server output: warnings matter even when every
        # assertion passed, and exit codes underreport partial failures.
        log.flush()
        tail = ''.join(open(log.name).readlines()[-60:])
        print(f'\n--- gz sim output tail ({log.name}) ---\n{tail}')

    request.addfinalizer(teardown)
    deadline = time.time() + 120
    while time.time() < deadline:
        if proc.poll() is not None:
            fail('gz server exited during startup')
        _, out = gz(env, 'model', '--list')
        if 'x500' in out:
            return env
        time.sleep(2)
    fail('model never appeared in the world')


def test_model_loaded(sim):
    """The composed model is in the world."""
    _, out = gz(sim, 'model', '--list')
    assert 'x500' in out


def test_sensor_topics_advertised(sim):
    """The flight-sensor topics and world clock are advertised."""
    deadline = time.time() + 30
    needed = ('/x500/imu', '/x500/air_pressure', '/x500/mag', '/x500/gps',
              f'/world/{WORLD_NAME}/clock')
    while time.time() < deadline:
        _, out = gz(sim, 'topic', '-l')
        if all(topic in out for topic in needed):
            return
        time.sleep(2)
    pytest.fail(f'missing topics; last listing:\n{out}')


def test_physics_steps(sim):
    """Simulation iterations advance (systems survive stepping)."""
    deadline = time.time() + 30
    while time.time() < deadline:
        code, out = gz(sim, 'topic', '-e', '-t',
                       f'/world/{WORLD_NAME}/stats', '-n', '1', timeout=15)
        if code == 0 and 'iterations' in out:
            if int(out.split('iterations:')[1].split()[0]) > 0:
                return
        time.sleep(2)
    pytest.fail('sim iterations did not advance')


def test_imu_publishes_data(sim):
    """The IMU streams real data (non-render sensor: hard assertion)."""
    deadline = time.time() + 45
    while time.time() < deadline:
        code, out = gz(sim, 'topic', '-e', '-t', '/x500/imu', '-n', '1',
                       timeout=15)
        if code == 0 and 'linear_acceleration' in out:
            return
        time.sleep(2)
    pytest.fail('no IMU data')


def test_gps_publishes_fix(sim):
    """The NavSat sensor resolves the world spherical coordinates to a fix."""
    deadline = time.time() + 45
    while time.time() < deadline:
        code, out = gz(sim, 'topic', '-e', '-t', '/x500/gps', '-n', '1',
                       timeout=15)
        if code == 0 and 'latitude_deg' in out:
            return
        time.sleep(2)
    pytest.fail('no GPS fix')
