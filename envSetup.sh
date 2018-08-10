#!/bin/bash
#echo -e "\n## NOTE ## ---> ** Before running the script, switch to root user! If you are not root, "CTRL + C" now!!! **"
#sleep 3

echo -e "\n**** Running the iptables script now!"
./bg.sh&

echo -e "\n\n******Starting with environment setup******\n"
sudo apt-get -y install qemu-kvm
sleep 2
sudo apt-get -y install libvirt-bin
sleep 2
sudo apt-get -y install virt-manager
sleep 2
sudo apt-get -y install virt-viewer
sleep 2
sudo apt-get -y install libguestfs-tools
sleep 2
sudo apt-get install python-libvirt
sleep 2
sudo apt-get install libvirt-doc
sleep 2
sudo apt install -y python-pip
sleep 2
sudo pip install --upgrade pip
sleep 2
sudo pip install docker
sleep 2
sudo apt-get install python-paramiko -y
sleep 2
#sudo python -m easy_install --upgrade pyOpenSSL
sudo apt-get install python-jinja2 -y
sleep 2
sudo apt-get install python-yaml -y
sleep 2
sudo apt-get install bridge-utils
sleep 1
sudo sysctl -w net.ipv4.ip_forward=1
sleep 1
sudo usermod -a -G libvirtd $USER

#sleep 2
#sudo wget http://distro.ibiblio.org/tinycorelinux/9.x/x86/release/TinyCore-current.iso -O /root/TinyCore.iso

sudo sed -i -e 's/#user/user/g' /etc/libvirt/qemu.conf
sudo sed -i -e 's/#group/group/g' /etc/libvirt/qemu.conf
sudo service libvirtd restart
################################################# DOCKER SETUP HERE ONWARDS ###############################################

echo -e "\n*********Setting up docker environment now!\n"
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sleep 1
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sleep 2
sudo apt-get update
sleep 2
sudo apt-get install -y docker-ce
sleep 2
#sudo usermod -aG docker ${USER}
#sleep 2
echo -e "\n\nDownloading ubuntu image now!*****"
sudo docker pull atandon70/ubuntu_project:loadedUBUNTUimage
sleep 2
sudo sed -i  's|ExecStart=/usr/bin/dockerd -H fd://*|ExecStart=/usr/bin/dockerd -H fd:// -H tcp://0.0.0.0:2375|' /lib/systemd/system/docker.service
sudo service docker stop
sleep 2
sudo systemctl daemon-reload
sleep 2
sudo service docker start
sleep 2
sudo pip install ipcalc
echo -e "\n**** Docker Installation done ****\n\n"

####################################################### IP Tables Here Onwards ###################################################


echo -e "\n\n******Environment setup completed! ****\n"
