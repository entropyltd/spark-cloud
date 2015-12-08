#!/bin/bash

set -e

key_pair_path=$1
key_pair=$2

cluster_name=spark-ec2classic-test
jar_name=test-spark-app.jar
local_jar_path=test-spark-app/target/scala-2.10/spark-cluster-launch-test_2.10-0.1-SNAPSHOT.jar
test_log_path=/tmp/spark-cloud-test.log

user=ubuntu
home_dir=/home/${user}

job_result=job-result.txt

working_directory=`pwd`

correct_value="-1696934592"

ssh_args="-o StrictHostKeyChecking=no -i ${key_pair_path}"

script_path="../spark-cloud.py"

if [ "${key_pair_path}" = "" ]; then
    echo "ERROR: please supply the key pair path as the first arg to this script"
    exit 1
fi

if [ "${key_pair}" = "" ]; then
    echo "ERROR: please supply the key pair as the second arg to this script"
    exit 1
fi

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
    master=`cat ${test_log_path} | grep -o "ec2.*compute[\-]*[0-9]*\.amazonaws\.com" | head -1`
    if [ "${master}" = "" ]; then
        echo "ERROR: Did not find master node"
        exit 1
    fi
    echo ${master}
}

function create-cluster {
    ${script_path} -k ${key_pair} --zone=us-east-1e --spot-price=0.02 launch ${cluster_name} | tee ${test_log_path}
}

function build-simple-spark-app {
    cd ${working_directory}/test-spark-app
    sbt package
    cd ${working_directory}
}

function spark-submit-simple-app {
    echo "INFO: Copying jar"
    scp ${ssh_args} ${local_jar_path} ${user}@$1:${home_dir}/${jar_name}

    echo "INFO: Getting spark master URL"
    host=`ssh ${ssh_args} ${user}@$1 "hostname"`
    spark_master=spark://${host}.ec2.internal:7077

    echo "INFO: Spark master url: $spark_master"

    echo "INFO: Running spark-submit"
    ssh ${ssh_args} ${user}@$1 "spark-submit --master $spark_master --class test.app.AddLotsOfNumbers ${jar_name} ${home_dir}/${job_result}"
}

# TODO Add more tests, like:
# to force it to scale
# curl the UI, etc
function check-output-of-job {
    scp ${ssh_args} ${user}@$1:${home_dir}/${job_result} /tmp/
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
    ${script_path} destroy spark-ec2classic-test
}

trap destroy-cluster EXIT

create-cluster
master=`extract-master-node-from-log`

echo "INFO: master: $master"

build-simple-spark-app

spark-submit-simple-app ${master}

check-output-of-job ${master}
