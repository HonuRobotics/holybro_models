cmake_minimum_required(VERSION 3.14)
project(x500_description)

find_package(ament_cmake REQUIRED)
find_package(xacro REQUIRED)
# The description is assembled from the part library at build time, so it must
# be installed first: $(find holybro_parts) resolves while expanding.
find_package(holybro_parts REQUIRED)

# Expand the xacro into a concrete URDF at build time. Dependencies are listed
# EXPLICITLY: the configure time `xacro --deps` snapshot only warns on failure
# and is not refreshed until the next reconfigure, so on its own a config or
# include edit can silently fail to regenerate the URDF.
xacro_add_files(urdf/x500.urdf.xacro
  REMAP config_file:=${CMAKE_CURRENT_SOURCE_DIR}/config/x500.yaml
  DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/config/x500.yaml
  INSTALL DESTINATION urdf)

install(DIRECTORY
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
