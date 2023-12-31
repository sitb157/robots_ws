# Copyright 2022 Open Source Robotics Foundation, Inc.
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

import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription, ExecuteProcess
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution

from launch_ros.actions import Node


def generate_launch_description():
    # Configure ROS nodes for launch
    use_sim_time = LaunchConfiguration('use_sim_time', default='True')

    # Setup project paths
    pkg_gazebo_worlds = get_package_share_directory('gz_worlds')
    
    # Set up world sdf file
    sdf_world_file  =  os.path.join(pkg_gazebo_worlds, 'worlds', 'worlds.sdf')

    # Process gz sim
    gz_proc = ExecuteProcess(cmd=['gz', 'sim', sdf_world_file, '-v'], output='screen')

    # Load the SDF file from "description" package
    sdf_model_file  =  os.path.join(pkg_gazebo_worlds, 'models', 'diff_drive','model.sdf')
    with open(sdf_model_file, 'r') as infp:
        robot_desc = infp.read()

    # Takes the description and joint angles as inputs and publishes the 3D poses of the robot links
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='both',
        parameters=[
            {'use_sim_time': use_sim_time},
            {'robot_description': robot_desc},
            {'frame_prefix': 'diff_drive/'},
        ]
    )

    # Visualize in RViz
    rviz2 = Node(
       package='rviz2',
       executable='rviz2',
       arguments=['-d', os.path.join(pkg_gazebo_worlds, 'config', 'diff_drive.rviz')],
       condition=IfCondition(LaunchConfiguration('rviz'))
    )

    # Bridge ROS topics and Gazebo messages for establishing communication
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        parameters=[{
            'config_file': os.path.join(pkg_gazebo_worlds, 'config', 'gz_bridge.yaml'),
            'qos_overrides./tf_static.publisher.durability': 'transient_local',
        }],
        output='screen'
    )

    robot_localization_node = Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            parameters=[
                {os.path.join(pkg_gazebo_worlds, 'params', 'ekf.yaml')}, 
                {'use_sim_time': use_sim_time}],
            remappings=[('odometry/filtered', 'diff_drive/odometry/filtered')],
            output='screen'
    )
 
    declare_rviz_condition = DeclareLaunchArgument('rviz', default_value='true',
        description='Open RViz.'
    )

    declare_use_sim_time = DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'
    )
 
    return LaunchDescription([
        declare_rviz_condition,
        declare_use_sim_time,
        gz_proc,
        robot_state_publisher,
        robot_localization_node,
        bridge,
        rviz2
    ])
