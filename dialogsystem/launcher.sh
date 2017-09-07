echo "registring package ..."
source devel/setup.bash
echo "Localizing OpenCV3 ..."
export PYTHONPATH=src/pepper-dialog/dialogsystem/OpenCV/local/lib/python2.7/dist-packages:$PYTHONPATH
echo "Starting package ..."
roslaunch dialogsystem dialog.launch
