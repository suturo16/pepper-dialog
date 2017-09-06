echo "Configuring ros core node ..."
export ROS_MASTER_URI=http://localhost:11311/
echo "registring package ..."
source devel/setup.bash
echo "Starting package ..."
roslaunch dialogsystem dialog.launch
