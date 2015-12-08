#!/bin/bash

set -e

key_pair_path=$1

cluster_name=spark-ec2classic-test
jar=test-spark-app/test-spark-app.jar
test_log_path=/tmp/spark-cloud-test.log

user=ubuntu
home_dir=/home/${ubuntu}

job_result=job-result.txt

working_directory=`pwd`

correct_value=TODO

ssh_args="-o StrictHostKeyChecking=no -i ${key_pair_path}"

if [ "${key_pair}" = "" ]; then
	echo "ERROR: please supply the key pair path as the first arg to this script"
	exit 1
fi

key_pair=`basename ${key_pair_path} .pem`

# TODO take a look at s3 config or aws config files to set automatically

if [ "${AWS_SECRET_ACCESS_KEY}" = "" ]; then
	echo "ERROR: AWS_SECRET_ACCESS_KEY not set"
	exit 1
fi

if [ "${AWS_ACCESS_KEY}" = "" ]; then
	echo "ERROR: AWS_ACCESS_KEY not set"
	exit 1
fi

function extract-master-node-from-log {
	echo `cat ${test_log_path} | grep -o "ec2.*compute\.amazonaws\.com"`
}

function create-cluster {
	./spark-cloud.py -k ${key_pair} --zone=us-east-1e --spot-price-max=0.01 launch ${cluster_name} | tee ${test_log_path}
}

function build-simple-spark-app {
	cd ${working_directory}/test-spark-app
	sbt package
	cd ${working_directory}
}

function spark-submit-simple-app {
	scp ${ssh_args} ${jar} $1:${home_dir}/

	ssh ${ssh_args} ${user}@$1 "spark-submit ${jar}"
}

# TODO Add more tests, like:
# to force it to scale
# curl the UI, etc
function check-output-of-job {
	scp ${ssh_args} $1:${home_dir}/${job_result} /tmp/
	value=`cat /tmp/${job_result}`

	if [ "${value}" = "${correct_value}" ]; then
		echo "INFO: Test passed!!!"
	else
		echo "ERROR: Test failed, expected ${correct_value} but got ${value}"
		exit 1
	fi
}

function destroy-cluster {
	echo "INFO: Destroying cluster"
	./spark-cloud.py destroy spark-ec2classic-test
}

trap destroy-cluster EXIT

create-cluster
master=`extract-master-node-from-log`

echo "INFO: master: $master"


build-simple-spark-app
spark-submit-simple-app $master
check-output-of-job


