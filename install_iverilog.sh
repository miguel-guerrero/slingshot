#/bin/bash

inst_dir=$HOME/iverilog

export TARGET_ARCH=  #in mac-os if this is set, linking fails

error_exit() {
    echo "$1" 1>&2
    exit 1
}

#check if wget is available, if not exit
which wget || error_exit "install wget before proceeding please. Exiting.."

#use this script to install from source in a local directory (no need for root
#access). If the install directory is changed from the default above, make sure 
#to update common/include.mk PATH variable accordingly or have the new path/bin
#area in your path

ver=20150513
wget ftp://ftp.icarus.com/pub/eda/verilog/snapshots/pre-v10/verilog-$ver.tar.gz 
tar xvfz verilog-$ver.tar.gz
cd verilog-$ver
./configure --prefix=$inst_dir && make && make install
cd ..
rm -rf verilog-$ver
rm -f verilog-$ver.tar.gz

echo -e "Remember to add the following to your .profile or equivalent:\n"
echo -e "    export PATH=$inst_dir/bin:\$PATH"
echo -e "\nor\n"
echo -e "    set path=($inst_dir/bin \$path)"
echo -e "\ndepending on your shell"
