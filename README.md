# ros_onewire_server

This package reads sensor data from from a onewire server (ow-server)
and publishes them to ROS.

Tested on Ubuntu only.

## How to install

First, install [ow-server](http://owfs.org/) on your platform. On
Ubuntu this should work:

    apt-get install owserver ow-tools

Configure owserver as per online instructions. Confirm that the
commands ``owdir`` and ``owget`` successfully read the sensor data.


Inside the ``src`` directory of your ROS workspace, do:

    git clone https://github.com/berndpfrommer/ros_onewire_server.git

Build:

    cd ros_onewire_server
	catkin bt

Now adjust the config file to your needs:

    cd config
    cp example_config.yaml my_config.yaml
    emacs -nw my_config.yaml

Run it:

    roslaunch ros_onewire_server onewire_server.launch config_file:=`rospack find ros_onewire_server`/config/my_config.yaml

You should now see messages like this:

    [INFO] [1547051394.510679]: frequency: 0.10, tolerance: 0.500, frame_id: example_id
    [INFO] [1547051396.168964]: sensor  28.186CE3080000: temperature =  9.750C
    [INFO] [1547051397.823713]: sensor  28.C1BAE3080000: temperature = 10.875C
    [INFO] [1547051397.893296]: sensor  26.48F813020000: temperature =  9.781C
    [INFO] [1547051398.027243]: sensor  26.48F813020000: humidity    = 43.333%
