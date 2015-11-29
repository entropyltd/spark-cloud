#!/bin/bash

# wait for things to settle
sleep 30

# do not try to start services after installing
cat <<EOF | sudo tee /usr/sbin/policy-rc.d
#!/bin/sh
exit 101
EOF
sudo chmod 755 /usr/sbin/policy-rc.d

echo grub-pc grub2/linux_cmdline string | sudo debconf-set-selections
echo grub-pc grub-pc/install_devices_empty boolean true | sudo debconf-set-selections

sudo apt-get update
sudo apt-get -y install python python-pip python-dev
sudo apt-get -y build-dep ansible
sudo pip install ansible

