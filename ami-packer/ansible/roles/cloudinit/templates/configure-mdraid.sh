#!/usr/bin/env bash
### Setup instance stores with raid0

NUM_DEVICES=`find /dev -name 'xvd[b-z]*' | wc -l`
DEVICES=`find /dev -name 'xvd[b-z]*' -printf '%p\040'`

mount -l | grep '/dev/md127'

if [ $? -eq 1 ]; then
	echo "Mounting /dev/md127"

	for DEVICE in $DEVICES; do
		umount $DEVICE
	done


	yes | mdadm --create /dev/md127 --name=0 --level=0 -c256 --raid-devices=${NUM_DEVICES} --force $DEVICES
	echo "DEVICE $DEVICES" > /etc/mdadm.conf
	mdadm --detail --scan >> /etc/mdadm.conf

	blockdev --setra 65536 /dev/md127
	mkfs.ext4 /dev/md127
	mount -t ext4 -o noatime /dev/md127 /mnt
	mkdir /mnt/tmp
	chmod -R 777 /mnt
	chmod 1777 /mnt/tmp
	mount -o bind /mnt/tmp /tmp
else
	echo "/dev/md127 already configured"
fi

