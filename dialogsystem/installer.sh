#Variables. Change the default values if needed

tput setaf 7
echo "Initialiyzing temporary global variables ..."
tput setaf 2
export PACKAGE_FOLDER=pepperdialog
export PACKAGE_SOURCE=src
export GIT_DIALOG_SYSTEM=https://github.com/suturo16/pepper-dialog
export GIT_DIALOG_REPO=pepper-dialog
export DIALOG_PACKAGE_NAME=dialogsystem
export GIT_CHATSCRIPT=https://github.com/bwilcox-1234/ChatScript
export PYTHON_NAOQI_TAR_GZ_PATH=$HOME/Downloads/pynaoqi-python2.7-2.5.5.5-linux64.tar.gz
export GIT_ROS_NAOQI_BRIDGE=https://github.com/ros-naoqi/naoqi_bridge_msgs


tput setaf 7
#install ros-naoqi bridge 
echo "Installing ros-naoqi bridge ..."
tput setaf 2
cd ..
git clone $GIT_ROS_NAOQI_BRIDGE
cd ..
cd ..
catkin build 
cd $PACKAGE_SOURCE/$GIT_DIALOG_REPO/$DIALOG_PACKAGE_NAME

tput setaf 7
#install  
echo "Installing modified CMU PocketSphinx ..."
echo "Installing dependencies"
tput setaf 2
cd CMU
sudo apt-get install gcc g++ automake autoconf libtool bison swig python-dev libpulse-dev libboost-dev libxmlrpc-core-c3-dev

