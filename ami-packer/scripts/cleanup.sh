#!/bin/bash

sudo apt-get -y autoremove
sudo apt-get -y clean

echo "cleaning up dhcp leases"
sudo rm /var/lib/dhcp/*

echo "cleaning up udev rules"
sudo rm -f /etc/udev/rules.d/70-persistent-net.rules
sudo mkdir /etc/udev/rules.d/70-persistent-net.rules
sudo rm -rf /dev/.udev/
sudo rm -f /lib/udev/rules.d/75-persistent-net-generator.rules


