echo "Installing prerequisites ..."
cd ./CMU
sudo apt-get install gcc automake autoconf libtool bison swig python-dev libpulse-dev
echo "Installing sphinxbase ..."
mkdir sphinx-source
cd sphinx-source/
git clone https://github.com/cmusphinx/sphinxbase.git
./sphinxbase/autogen.sh
make
sudo make install
# echo "Compiling package ..."
# catkin build dialogsystem
# echo "registring package ..."
# source devel/setup.sh
echo "changing nodes to executables ..."
sudo chmod +777 ../../nodes/*.*
