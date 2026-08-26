cmake_minimum_required(VERSION 3.14)
project(x500_gazebo)

find_package(ament_cmake REQUIRED)
find_package(xacro REQUIRED)
find_package(x500_description REQUIRED)
find_package(holybro_parts REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter)

# Put this package's models dir on GZ_SIM_RESOURCE_PATH so model://x500
# (the composed model, installed under share/x500_gazebo/models/x500)
# resolves in Gazebo. The model is deliberately NOT named after the package:
# Gazebo tries model:// names relative to the current directory first, and a
# source checkout has a directory called x500_gazebo.
ament_environment_hooks("hooks/resource_paths.dsv.in")
ament_environment_hooks("hooks/resource_paths.sh.in")

install(DIRECTORY
  launch
  worlds
  DESTINATION share/${PROJECT_NAME})

# ros_gz bridge config is GENERATED from the vehicle config plus the
# assembled URDF (whose <assembly_part> manifest lists the resolved parts,
# defaults included), so bridge topics always match the fitted parts.
# Re-runs when the config, the URDF or the generator changes.
set(vehicle_config ${x500_description_DIR}/../config/x500.yaml)
set(desc_urdf ${x500_description_DIR}/../urdf/x500.urdf)
set(bridge_yaml ${CMAKE_CURRENT_BINARY_DIR}/ros_gz_bridge.yaml)
add_custom_command(
  OUTPUT ${bridge_yaml}
  COMMAND Python3::Interpreter
          ${CMAKE_CURRENT_SOURCE_DIR}/scripts/generate_bridge_config.py
          ${vehicle_config} ${desc_urdf} ${bridge_yaml}
  DEPENDS ${vehicle_config} ${desc_urdf}
          ${CMAKE_CURRENT_SOURCE_DIR}/scripts/generate_bridge_config.py
  COMMENT "Generating ros_gz_bridge.yaml from x500.yaml and x500.urdf")
add_custom_target(${PROJECT_NAME}_bridge_yaml ALL DEPENDS ${bridge_yaml})
install(FILES ${bridge_yaml} DESTINATION share/${PROJECT_NAME}/config)

# The URDF the model merges, installed next to it so model://x500/x500.urdf
# resolves. (No Gazebo flavoured copy here: the x500 meshes are dae/stl,
# which Gazebo and the ROS tools orient identically; only glTF differs.)
install(FILES ${desc_urdf} DESTINATION share/${PROJECT_NAME}/models/x500)

# Composed simulation model. model.sdf is GENERATED from model.sdf.xacro at
# build time (reads x500_description/config/x500.yaml, adds the Gazebo
# plugins) and installed as models/x500/model.sdf next to the static
# model.config, i.e. model://x500. The config dependency is EXPLICIT: the
# configure time xacro --deps snapshot cannot resolve $(find) and fails with
# only a warning, leaving the rule without deps.
xacro_add_files(model.sdf.xacro DEPENDS ${vehicle_config} ${desc_urdf}
  INSTALL DESTINATION models/x500)
install(FILES model.config DESTINATION share/${PROJECT_NAME}/models/x500)
install(FILES model.sdf.xacro DESTINATION share/${PROJECT_NAME})
install(PROGRAMS
  scripts/generate_bridge_config.py
  scripts/configure_vehicle.py
  DESTINATION lib/${PROJECT_NAME})

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
  find_package(ament_cmake_pytest REQUIRED)
  ament_add_pytest_test(test_bridge_generator test/test_bridge_generator.py
    TIMEOUT 60)
  ament_add_pytest_test(test_configure_vehicle test/test_configure_vehicle.py
    TIMEOUT 300)
  ament_add_pytest_test(test_model_generation test/test_model_generation.py
    TIMEOUT 180)
  # NOCAPTURE so the sim output printed at teardown reaches the test logs
  # even when every assertion passes.
  ament_add_pytest_test(test_gz_launch test/test_gz_launch.py TIMEOUT 420
    NOCAPTURE)
  ament_add_pytest_test(test_ros_launch test/test_ros_launch.py TIMEOUT 300
    NOCAPTURE)
endif()

ament_package()
