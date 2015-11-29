# spark-cloud
Spark-cloud is a set of scripts for starting spark clusters on ec2

# Warning
spark-cloud is Alpha quality pre-relase software, you are using it at your own risk.
Always check that your clusters have properly started/stopped.

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

