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
export GIT_ROS_NAOQI_BRIDGE= https://github.com/ros-naoqi/naoqi_bridge_msgs

tput setaf 7
#create package's and source's folder
echo "Creating package folder and source folder ..."
tput setaf 2
mkdir $PACKAGE_FOLDER
cd $PACKAGE_FOLDER
mkdir $PACKAGE_SOURCE 

tput setaf 7
#clone Dialog System Git Repository
echo "Cloning Dialog System Git Repository ..."
tput setaf 2
cd $PACKAGE_SOURCE 
git clone $GIT_DIALOG_SYSTEM

tput setaf 7
#clone ChatSrcipt Git Repository
echo "Cloning ChatScript Git Repository ..."
tput setaf 2
cd $GIT_DIALOG_REPO/$DIALOG_PACKAGE_NAME 
git clone $GIT_CHATSCRIPT

tput setaf 7
#install ChatSrcipt
echo "Installing ChatScript ..."
tput setaf 2
cp -r PEPPER1 ChatScript/RAWDATA
cp -r PEPPER2 ChatScript/RAWDATA
cp -r filespepper.txt ChatScript/RAWDATA

tput setaf 7
#make ChatScript executable 
echo "Making ChatScript executable ..."
tput setaf 2
sudo chmod +x ChatScript/BINARIES/LinuxChatScript64

tput setaf 7
#install python naoqi
echo "Installing Python Naoqi ..."
tput setaf 2
cd NAOqi
tar -xf $PYTHON_NAOQI_TAR_GZ_PATH
cd ..
echo export PYTHONPATH="$"PYTHONPATH:$PWD/NAOqi/pynaoqi-python2.7-2.5.5.5-linux64/lib/python2.7/site-packages >> $HOME/.bashrc

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

