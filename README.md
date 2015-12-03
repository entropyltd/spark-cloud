# spark-cloud
Spark-cloud is a set of scripts for starting spark clusters on ec2

[![Code Health](https://landscape.io/github/entropyltd/spark-cloud/master/landscape.svg?style=flat)](https://landscape.io/github/entropyltd/spark-cloud/master)

# Warning
spark-cloud is Alpha quality pre-relase software, you are using it at your own risk.
Always check that your clusters have properly started/stopped.

spark-cloud will currently only work in us-east AWS zone, support for other zones coming very soon!

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

To run `spark-shell` you can't use `--master yarn-client` at the moment, you need to explicitly specify the master. The master URL will be of the form `spark://host:port` it can be found by opening up the spark UI (which is helpfully printed at launch time).

```
spark-shell --master <master-url-as-explained-above>
```

It might produce some weird exceptions, you might be able to ignore these and use the shell normally anyway.

# Termination

Has a couple of issues (see issues) but manual work arounds exist (see issues)
