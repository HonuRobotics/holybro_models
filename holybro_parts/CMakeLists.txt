cmake_minimum_required(VERSION 3.14)
project(holybro_parts)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

# Put this package's share dir on GZ_SIM_RESOURCE_PATH so package:// URIs into
# models/ resolve in Gazebo. RViz resolves package:// through the ament index.
ament_environment_hooks("hooks/resource_paths.dsv.in")
ament_environment_hooks("hooks/resource_paths.sh.in")

# models/ carries the meshes (PX4 BSD 3 placeholders, see models/LICENSE);
# urdf/ carries the parts, one macro file each, the parts level library
# that includes them and the assembly dispatcher.
install(DIRECTORY
  models
  urdf
  DESTINATION share/${PROJECT_NAME})

# The Python side: the assembly manifest reader and the config check that
# vehicle builds and launches run (holybro_parts.assembly).
ament_python_install_package(${PROJECT_NAME})

# Tooling run by a person, never by the build: check_assembly.py is the
# config check as a CLI. (The SDF bootstrap and glTF tools live in
# bluerobotics_parts until the shared machinery is extracted.)
install(PROGRAMS
  scripts/check_assembly.py
  DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_parts test/test_parts.py TIMEOUT 180)
endif()

ament_package()
