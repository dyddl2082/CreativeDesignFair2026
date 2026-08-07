cmake_minimum_required(VERSION 3.8)
project(macrobot_description)

find_package(ament_cmake REQUIRED)

install(DIRECTORY urdf meshes launch rviz config docs images
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
