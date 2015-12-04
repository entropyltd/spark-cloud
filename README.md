# spark-cloud
Spark-cloud is a set of scripts for starting spark clusters on ec2

[![Join the chat at https://gitter.im/entropyltd/spark-cloud](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/entropyltd/spark-cloud?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge)

[![Code Health](https://landscape.io/github/entropyltd/spark-cloud/master/landscape.svg?style=flat)](https://landscape.io/github/entropyltd/spark-cloud/master)

# Warning
spark-cloud is Alpha quality pre-relase software, you are using it at your own risk.
Always check that your clusters have properly started/stopped.

spark-cloud will currently only work in us-east AWS zone, support for other zones coming very soon!

# Cluster Security
Spark-cloud relies on ip level security for access to web UIs, you should specify `--authorized-address=your.ip.address/32` when running the real cluster.

At the moment the auto-scaling group will start with 2 slaves, the minimum will be 2 slaves and the maximum 8.

# Example usage

## To launch a cluster into VPC

```
# set credentials
export AWS_ACCESS_KEY=..
export AWS_SECRET_ACCESS_KEY=...
# start cluster
./spark-cloud.py -k keypair --vpc-id=vpc-XXXXX --subnet-id=subnet-XXXXXX --zone=us-east-1a launch sparkcluster1
```

## To launch a cluster into EC2-classic
```
# set credentials
export AWS_ACCESS_KEY=..
export AWS_SECRET_ACCESS_KEY=...
# start cluster
./spark-cloud.py -k keypair --zone=us-east-1e launch spark-ec2classic
```

## To ssh into your cluster and run the spark shell

To ssh in

```
ssh -i path-to-keypair.pem ubuntu@master-host-which-is-helpfully-printed-at-launch
```

To run `spark-shell` you can't use `--master yarn-client`.
The master URL will be of the form `spark://host:port` it can be found by opening up the spark UI (which is helpfully printed at launch time).


To run spark-shell just:
```
spark-shell
```

# Termination

Has a couple of issues in case it does not work just rerun the "destroy" command.
