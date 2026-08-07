cmake_minimum_required(VERSION 3.14)
project(x500_description)

find_package(ament_cmake REQUIRED)
find_package(xacro REQUIRED)

# Generate urdf/x500.urdf from the xacro at build time. REMAP passes the source
# config so accessory edits re-trigger regen (xacro --deps tracks the yaml).
xacro_add_files(urdf/x500.urdf.xacro
  REMAP config_file:=${CMAKE_CURRENT_SOURCE_DIR}/config/x500.yaml
  INSTALL DESTINATION urdf)

# Put this package's share dir on GZ_SIM_RESOURCE_PATH so package:// mesh URIs
# resolve in Gazebo (RViz resolves package:// via the ament index directly).
ament_environment_hooks("hooks/resource_paths.dsv.in")
ament_environment_hooks("hooks/resource_paths.sh.in")

install(DIRECTORY
  meshes
  urdf
  rviz
  launch
  config
  DESTINATION share/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_description test/test_description.py TIMEOUT 180)
endif()

ament_package()
