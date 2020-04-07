#!/bin/bash
os_type=`awk -F= '/^NAME/{print $2}' /etc/os-release`
if [ $os_type=="Ubuntu" ]; then
    # Do something under GNU/Linux platform
    sudo apt-get update
    sudo apt-get install -y python2.7
    sudo apt install -y python-pip
    sudo pip install -r requirement.txt
elif [ $os_type=="CentOS Linux" ]; then
    sudo yum update
    sudo yum -y install python2.7
    sudo yum -y install python-setuptools
    sudo yum -y install epel-release
    sudo yum -y install python-pip
    sudo pip install -r requirement.txt
fi
#For MacOS
if [ "${OS}" = "Darwin" ]; then
	$xcode-select --install
	/usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

	brew install python3
	sudo easy_install pip 
	sudo pip install

	sudo pip install -r requirement.txt
fi
