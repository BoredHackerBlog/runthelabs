#This script installs dependencies to run the python code, minimega, and virtual machines
#Update and install required packages
apt-get update
apt-get install -y git golang gcc libpcap-dev libreadline-dev dnsmasq qemu-kvm openvswitch-switch python python-pip python-openssl
#apt-get install -y python-mysql.connector
pip install Flask
#Get minimega 2.0 from github
git clone https://github.com/ITLivLab/minimega
#Build minimega
bash minimega/build.bash
#Copy the minimega binary to current folder
cp ./minimega/bin/minimega mm
#Remove minimega source code and other binary because we don't need it
rm -rf minimega/
