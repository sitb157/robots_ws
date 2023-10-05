FROM ros:humble-perception-jammy

ARG USER_NAME
ARG USER_ID=1000
ARG GROUP_ID=1000
RUN groupadd ${USER_NAME} --gid ${USER_ID}\
    && useradd -l -m ${USER_NAME} -u ${USER_ID} -g ${USER_ID} -s /bin/bash

USER root

ARG ROS_DISTRO=humble
RUN apt-get update 
RUN apt-get install -y \
    vim \ 
    git

# Install rmf
RUN apt-get update && apt-get install -y \
    python3-pip \
    curl \
    python3-colcon-mixin \
    ros-dev-tools
 
# install gazebo garden
RUN apt-get update &&  apt-get install -y \
    lsb-release \
    wget \
    gnupg

RUN apt-get update && apt-get install -y \
    ros-${ROS_DISTRO}-rviz2 \
    ros-${ROS_DISTRO}-rqt* 

COPY ./src /root/robots_ws/src
WORKDIR /root/robots_ws/src
#RUN git clone --depth 1 -b humble https://github.com/gazebosim/ros_gz.git 
WORKDIR /root/robots_ws
ENV GZ_VERSION=garden
RUN rosdep install -r --from-paths src -i -y --rosdistro humble

RUN wget https://packages.osrfoundation.org/gazebo.gpg -O /usr/share/keyrings/pkgs-osrf-archive-keyring.gpg
RUN echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/pkgs-osrf-archive-keyring.gpg] http://packages.osrfoundation.org/gazebo/ubuntu-stable $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/gazebo-stable.list > /dev/null
RUN apt-get update && apt-get install -y gz-garden
RUN apt-get install -y \
    ros-${ROS_DISTRO}-ros-gz-bridge \
    ros-${ROS_DISTRO}-ros-gz-sim


RUN echo "source /opt/ros/$ROS_DISTRO/setup.bash" >> ~/.bashrc
