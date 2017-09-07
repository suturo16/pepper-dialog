#Variables. Change the default values if needed

tput setaf 2
echo "Initialiyzing temporary global variables ..."
tput setaf 7
export PACKAGE_FOLDER=pepperdialog
export OPENCV_FOLDER=OpenCV
export PACKAGE_SOURCE=src
export GIT_DIALOG_SYSTEM=https://github.com/suturo16/pepper-dialog
export GIT_DIALOG_REPO=pepper-dialog
export DIALOG_PACKAGE_NAME=dialogsystem
export GIT_CHATSCRIPT=https://github.com/bwilcox-1234/ChatScript
export PYTHON_NAOQI_TAR_GZ_PATH=$HOME/Downloads/pynaoqi-python2.7-2.5.5.5-linux64.tar.gz
export GIT_ROS_NAOQI_BRIDGE=https://github.com/ros-naoqi/naoqi_bridge_msgs
export CMU_SPHINX_ROOT=sphinx-source
export GIT_SPHINXBASE=https://github.com/cmusphinx/sphinxbase
export GIT_POCKETSPHINX=https://github.com/cmusphinx/pocketsphinx
export GIT_SHINXTRAIN=https://github.com/cmusphinx/sphinxtrain
export GIT_OPENCV=https://github.com/Itseez/opencv.git
export GIT_OPENCV_CONTRIB=https://github.com/Itseez/opencv_contrib.git

tput setaf 2
#Cleaning Workspace
echo "Cleaning and Preparing Workspace $GIT_DIALOG_REPO ..."
tput setaf 7
rm -r -f $GIT_DIALOG_REPO


tput setaf 2
#create package's and source's folder
echo "Creating package folder and source folder ..."
tput setaf 7
mkdir $PACKAGE_FOLDER
cd $PACKAGE_FOLDER
mkdir $PACKAGE_SOURCE 

tput setaf 2
#clone Dialog System Git Repository
echo "Cloning Dialog System Git Repository ..."
tput setaf 7
cd $PACKAGE_SOURCE 
git clone $GIT_DIALOG_SYSTEM

tput setaf 2
#clone ChatSrcipt Git Repository
echo "Cloning ChatScript Git Repository ..."
tput setaf 7
cd $GIT_DIALOG_REPO/$DIALOG_PACKAGE_NAME 
git clone $GIT_CHATSCRIPT

tput setaf 2
#install ChatSrcipt
echo "Installing ChatScript ..."
tput setaf 7
cp -r PEPPER1 ChatScript/RAWDATA
cp -r PEPPER2 ChatScript/RAWDATA
cp -r filespepper.txt ChatScript/RAWDATA

tput setaf 2
#make ChatScript executable 
echo "Making ChatScript executable ..."
tput setaf 7
sudo chmod +x ChatScript/BINARIES/LinuxChatScript64

tput setaf 2
#install python naoqi
echo "Installing Python Naoqi ..."
tput setaf 7
cd NAOqi
tar -xf $PYTHON_NAOQI_TAR_GZ_PATH
cd ..
echo export PYTHONPATH="$"PYTHONPATH:$PWD/NAOqi/pynaoqi-python2.7-2.5.5.5-linux64/lib/python2.7/site-packages >> $HOME/.bashrc

tput setaf 2
#install ros-naoqi bridge 
echo "Installing ros-naoqi bridge ..."
tput setaf 7
cd ..
git clone $GIT_ROS_NAOQI_BRIDGE
cd ..
cd ..
catkin build 
cd $PACKAGE_SOURCE/$GIT_DIALOG_REPO/$DIALOG_PACKAGE_NAME

tput setaf 2
#install  
echo "Cloning modified CMU Sphinx ..."
tput setaf 7
cd CMU
mkdir $CMU_SPHINX_ROOT
cd $CMU_SPHINX_ROOT
git clone $GIT_SPHINXBASE
git clone $GIT_POCKETSPHINX
git clone $GIT_SHINXTRAIN
cd ..
cd ..



tput setaf 2
#install  
echo "Installing modified CMU PocketSphinx ..."
echo "Installing dependencies"
tput setaf 7
cd CMU/cnodes
cp fdsink.h ../$CMU_SPHINX_ROOT/pocketsphinx/include
cd ..
#modify speech recognizer
cd $CMU_SPHINX_ROOT/pocketsphinx/src/programs
rm  -r -f continuous.c
cd ..
cd ..
cd ..
cd ..
cd cnodes
cp continuous.cpp ../$CMU_SPHINX_ROOT/pocketsphinx/src/programs
cd ..
cd ..
sudo apt-get install gcc g++ automake autoconf libtool bison swig python-dev libpulse-dev libboost-dev libxmlrpc-core-c3-dev libgstreamer1.0-0 gstreamer1.0-tools libglib2.0-dev



tput setaf 2
#install  
echo "Compiling CMU Sphinxbase ..."
tput setaf 7
cd CMU/$CMU_SPHINX_ROOT/sphinxbase
./autogen.sh
make
sudo make install
cd ..
cd ..
cd ..

tput setaf 2
#install  
echo "Compiling CMU Sphinxtrain ..."
tput setaf 7
cd CMU/$CMU_SPHINX_ROOT/sphinxtrain
./autogen.sh
make
sudo make install
cd ..
cd ..
cd ..

tput setaf 2
#install  
echo "Compiling CMU pocketsphinx ..."
tput setaf 7
cd CMU/$CMU_SPHINX_ROOT/pocketsphinx
rm -r -f configure.ac
cd src/programs
rm -r -f Makefile.am
cd ../../../../cnodes
cp Makefile.am ../$CMU_SPHINX_ROOT/pocketsphinx/src/programs
cp configure.ac ../$CMU_SPHINX_ROOT/pocketsphinx
cd ../$CMU_SPHINX_ROOT/pocketsphinx
./autogen.sh
make
sudo make install
cd ..
cd ..
cd ..

tput setaf 2
#install  opencv
echo "Installing OpenCV 3 ..."
tput setaf 7
mkdir $OPENCV_FOLDER
cd $OPENCV_FOLDER
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install build-essential cmake git pkg-config 
sudo apt-get install libjpeg8-dev libtiff4-dev 
sudo apt-get install libjasper-dev libpng12-dev
sudo apt-get install libgtk2.0-dev
sudo apt-get install libavcodec-dev libavformat-dev libswscale-dev
sudo apt-get install libv4l-dev
sudo apt-get install libatlas-base-dev gfortran
wget https://bootstrap.pypa.io/get-pip.py
sudo python get-pip.py
sudo apt-get install python2.7-dev
sudo pip install numpy
git clone $GIT_OPENCV
cd opencv
git checkout 3.0.0
cd ..
git clone $GIT_OPENCV_CONTRIB
cd opencv_contrib
git checkout 3.0.0
cd ..
cd opencv
mkdir build 
cd build
cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D INSTALL_C_EXAMPLES=ON -D INSTALL_PYTHON_EXAMPLES=ON \
      -D OPENCV_EXTRA_MODULES_PATH=../opencv_contrib/modules -D BUILD_EXAMPLES=ON -D BUILD_opencv_gpu=OFF -D WITH_CUDA=OFF ..
make -j4
sudo make install
sudo ldconfig



tput setaf 2
#creating launch file
echo "Creating launch file ..."
tput setaf 7
cp launcher.sh ../../../

tput setaf 2
echo "Installation of Dialog System successfully terminated !"
tput setaf 7
source $HOME/.bashrc
echo "End."
