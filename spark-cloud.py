#!/usr/bin/env python
# pylint: disable=line-too-long
# idea based on https://github.com/apache/spark/blob/master/ec2/spark_ec2.py
from __future__ import absolute_import, division, print_function, unicode_literals
import random

import sys
import time
import socket
from optparse import OptionParser
from datetime import datetime

import boto
import boto.ec2.autoscale
import boto.ec2.cloudwatch
from boto.ec2.autoscale import LaunchConfiguration, AutoScalingGroup, ScalingPolicy
from boto.ec2.cloudwatch import MetricAlarm
from boto.ec2.networkinterface import NetworkInterfaceSpecification, NetworkInterfaceCollection


def get_group(conn, name):
    """
    Get the EC2 security group of the given name
    """
    groups = conn.get_all_security_groups()
    return [g for g in groups if g.name == name]

def get_or_make_group(conn, name, vpc_id):
    """
        Get the EC2 security group of the given name, creating it if it doesn't exist
    """
    groups = conn.get_all_security_groups()
    group = [g for g in groups if g.name == name]
    if len(group) > 0:
        return group[0]
    else:
        print("Creating security group " + name)
        return conn.create_security_group(name, "Spark Cloud group", vpc_id)


def wait_for_tcp_port(host, port=22):
    sys.stdout.write(
        "Waiting for port {port} to be available".format(port=port)
    )
    sys.stdout.flush()
    start_time = datetime.now()
    while True:
        sys.stdout.write(".")
        sys.stdout.flush()
        s = socket.socket()
        result = s.connect_ex((host, port))
        if result == 0:
            s.close()
            break
        time.sleep(5)
    end_time = datetime.now()
    print("Port {port} is now available. Waited {t} seconds.".format(
        port=port,
        t=(end_time - start_time).seconds
    ))


def wait_for_cluster_state(conn, cluster_instances, cluster_state="running", name="master"):
    """
    Wait for all the instances in the cluster to reach a designated state.
    cluster_instances: a list of boto.ec2.instance.Instance
    cluster_state: a string representing the desired state of all the instances in the cluster
           value can be valid value from boto.ec2.instance.InstanceState such as
           'running', 'terminated', etc.
    """
    sys.stdout.write(
        "Waiting for {n} to enter '{s}' state.".format(n=name, s=cluster_state)
    )
    sys.stdout.flush()
    start_time = datetime.now()
    while True:
        for i in cluster_instances:
            i.update()
        max_batch = 100
        statuses = []
        for j in xrange(0, len(cluster_instances), max_batch):
            batch = [i.id for i in cluster_instances[j:j + max_batch]]
            statuses.extend(conn.get_all_instance_status(instance_ids=batch))
        if all(i.state == cluster_state for i in cluster_instances):
            break
        sys.stdout.write(".")
        sys.stdout.flush()
        time.sleep(5)
    sys.stdout.write("\n")
    end_time = datetime.now()
    print("Cluster is now in '{s}' state. Waited {t} seconds.".format(
        s=cluster_state,
        t=(end_time - start_time).seconds
    ))


def setup_security_groups(conn, cluster_name, opts):
    print("Setting up security groups...")
    master_group = get_or_make_group(
        conn, cluster_name + "-master", opts.vpc_id)
    worker_group = get_or_make_group(
        conn, cluster_name + "-workers", opts.vpc_id)
    authorized_address = opts.authorized_address
    if master_group.rules == []:  # Group was just now created
        if opts.vpc_id is None:
            master_group.authorize(src_group=master_group)
            master_group.authorize(src_group=worker_group)
        else:
            master_group.authorize(ip_protocol='-1', from_port=None, to_port=None,
                                   src_group=master_group)
            master_group.authorize(ip_protocol='-1', from_port=None, to_port=None,
                                   src_group=worker_group)
        master_group.authorize('tcp', 0, 65535, authorized_address)
    if worker_group.rules == []:  # Group was just now created
        if opts.vpc_id is None:
            worker_group.authorize(src_group=master_group)
            worker_group.authorize(src_group=worker_group)
        else:
            worker_group.authorize(ip_protocol='-1', from_port=None, to_port=None,
                                  src_group=master_group)
            worker_group.authorize(ip_protocol='-1', from_port=None, to_port=None,
                                  src_group=worker_group)
        worker_group.authorize('tcp', 22, 22, authorized_address)
    return (master_group, worker_group)


def delete_security_groups(conn, cluster_name):
    print("Deleting security groups...")
    master_group = get_group(conn, cluster_name + "-master")
    # TODO: deprecate this in Jan 2016
    slave_group = get_group(conn, cluster_name + "-slaves")
    worker_group = get_group(conn, cluster_name + "-workers")
    groups = master_group + worker_group + slave_group
    success = True
    for group in groups:
        print("Deleting rules in security group " + group.name)
        for rule in group.rules:
            for grant in rule.grants:
                success &= conn.revoke_security_group(group_id=group.id, ip_protocol=rule.ip_protocol,
                                                      from_port=rule.from_port, to_port=rule.to_port,
                                                      src_security_group_group_id=grant.group_id, cidr_ip=grant.cidr_ip)
    time.sleep(2)
    for group in groups:
        try:
            conn.delete_security_group(group_id=group.id)
            print("Deleted security group %s" % group.name)
        except boto.exception.EC2ResponseError, e:
            success = False
            print("Failed to delete security group %s" % group.name)
            print(e)
    if not success:
        print("Failed to delete all security groups, try again later")


def parse_options():
    parser = OptionParser(
        usage="%prog [options] <action> <cluster_name>\n\n"
              + "<action> can be: launch, destroy")
    parser.add_option(
        "-k", "--key-pair", default=None,
        help="Key pair to use on instances")
    parser.add_option(
        "-i", "--identity-file",
        help="SSH private key file to use for logging into instances")
    parser.add_option(
        "-r", "--region", default="us-east-1",
        help="EC2 region used to launch instances in, or to find them in (default: %default)")
    parser.add_option(
        "-a", "--ami", default="ami-cdf3bea7",
        help="Amazon Machine Image ID to use")
    parser.add_option(
        "--authorized-address", type="string", default="0.0.0.0/0",
        help="Address to authorize on created security groups (default: %default)")
    parser.add_option(
        "-t", "--instance-type", default="m3.medium",
        help="Type of instance to launch (default: %default). ")
    parser.add_option(
        "-m", "--master-instance-type", default="m3.medium",
        help="Master instance type (default: %default)")
    parser.add_option(
        "--spot-price", metavar="PRICE", type="float",
        help="If specified, launch workers as spot instances with the given " +
             "maximum price (in dollars)")
    parser.add_option(
        "--subnet-id", default=None,
        help="VPC subnet to launch instances in")
    parser.add_option(
        "--vpc-id", default=None,
        help="VPC to launch instances in")
    parser.add_option(
        "-z", "--zone", default=None,
        help="Availability zone to launch instances in")

    (opts, args) = parser.parse_args()
    if len(args) != 2:
        parser.print_help()
        sys.exit(1)

    (action, cluster_name) = args
    return (opts, action, cluster_name)


def find_instance_by_name(conn, name):
    reservations = conn.get_all_instances()
    instances = [i for r in reservations for i in r.instances]
    for i in instances:
        if "Name" in i.tags and name == i.tags['Name']:
            return i
    return None


def start_master(conn, opts, cluster_name, master_group):
    try:
        conn.get_all_images(image_ids=[opts.ami])[0]
    except boto.exception.EC2ResponseError:
        print("Could not find AMI " + opts.ami)
        sys.exit(1)
    if opts.vpc_id:
        interface = NetworkInterfaceSpecification(subnet_id=opts.subnet_id,
                                                  groups=[master_group.id],
                                                  associate_public_ip_address=True)
        interfaces = NetworkInterfaceCollection(interface)
        security_group_ids = None
    else:
        interfaces = None
        security_group_ids = [master_group.id]
    master_res = conn.run_instances(
        image_id=opts.ami,
        key_name=opts.key_pair,
        instance_type=opts.master_instance_type,
        placement=opts.zone,
        min_count=1,
        max_count=1,
        network_interfaces=interfaces,
        security_group_ids=security_group_ids)
    instance = master_res.instances[0]
    time.sleep(1)
    conn.create_tags(
        [instance.id], {"Name": "{c}-master".format(c=cluster_name)})
    return instance


def validate_opts(conn, opts, action):
    if opts.zone is None and opts.vpc_id is None:
        opts.zone = random.choice(conn.get_all_zones()).name
    if opts.vpc_id is not None and opts.zone is None:
        print("please specify zone with vpc_id")
        sys.exit(1)
    if opts.zone is None:
        print("please specify zone (--zone)")
        sys.exit(1)
    if action == "launch":
        if opts.key_pair is None:
            print("please specify keypair (-k)")
            sys.exit(1)
    return opts


def create_autoscaling_group(autoscale, cluster_name, master_node, opts, slave_group):
    lclist = autoscale.get_all_launch_configurations(
        names=[cluster_name + "-lc"])
    if lclist:
        lc = lclist[0]
    else:
        lc = LaunchConfiguration(
            name=cluster_name + "-lc",
            image_id=opts.ami,
            key_name=opts.key_pair,
            security_groups=[slave_group.id],
            instance_type=opts.instance_type,
            user_data="SPARK_MASTER=" + master_node.private_dns_name + "\n",
            instance_monitoring=True,
            spot_price=opts.spot_price)
        autoscale.create_launch_configuration(lc)
    aglist = autoscale.get_all_groups(names=[cluster_name + "-ag"])
    if aglist:
        ag = aglist[0]
    else:
        ag = AutoScalingGroup(group_name=cluster_name + "-ag",
                              launch_config=lc,
                              min_size=2,
                              max_size=8,
                              connection=autoscale,
                              vpc_zone_identifier=opts.subnet_id,
                              availability_zones=[opts.zone])
        autoscale.create_auto_scaling_group(ag)
    as_tag = boto.ec2.autoscale.Tag(key='Name',
                                    value=cluster_name + '-worker',
                                    propagate_at_launch=True,
                                    resource_id=cluster_name + "-ag")
    autoscale.create_or_update_tags([as_tag])


def create_autoscaling_policy(autoscale, cluster_name, opts):
    scale_up_policy = ScalingPolicy(
        name='scale_up', adjustment_type='ChangeInCapacity',
        as_name=cluster_name + "-ag", scaling_adjustment=5, cooldown=60)
    scale_down_policy = ScalingPolicy(
        name='scale_down', adjustment_type='ChangeInCapacity',
        as_name=cluster_name + "-ag", scaling_adjustment=-1, cooldown=60)
    autoscale.create_scaling_policy(scale_up_policy)
    autoscale.create_scaling_policy(scale_down_policy)
    scale_up_policy = autoscale.get_all_policies(
        as_group=cluster_name + "-ag", policy_names=['scale_up'])[0]
    scale_down_policy = autoscale.get_all_policies(
        as_group=cluster_name + "-ag", policy_names=['scale_down'])[0]
    alarm_dimensions = {"AutoScalingGroupName": cluster_name + "-ag"}
    cloudwatch = boto.ec2.cloudwatch.connect_to_region(opts.region)
    scale_up_alarm = MetricAlarm(
        name='scale_up_on_cpu', namespace='AWS/EC2',
        metric='CPUUtilization', statistic='Average',
        comparison='>', threshold='50',
        period='60', evaluation_periods=1,
        alarm_actions=[scale_up_policy.policy_arn],
        dimensions=alarm_dimensions)
    cloudwatch.create_alarm(scale_up_alarm)
    scale_down_alarm = MetricAlarm(
        name='scale_down_on_cpu', namespace='AWS/EC2',
        metric='CPUUtilization', statistic='Average',
        comparison='<', threshold='40',
        period='60', evaluation_periods=1,
        alarm_actions=[scale_down_policy.policy_arn],
        dimensions=alarm_dimensions)
    cloudwatch.create_alarm(scale_down_alarm)


def main():
    (opts, action, cluster_name) = parse_options()
    conn = boto.ec2.connect_to_region(opts.region)
    opts = validate_opts(conn, opts, action)

    if action == "launch":
        (master_group, slave_group) = setup_security_groups(conn, cluster_name, opts)
        master_node = find_instance_by_name(conn, cluster_name + '-master')
        if not master_node:
            master_node = start_master(conn, opts, cluster_name, master_group)
        print("Master node: {m}".format(m=master_node))
        wait_for_cluster_state(
            conn=conn,
            cluster_instances=([master_node]),
        )
        autoscale = boto.ec2.autoscale.connect_to_region(opts.region)
        create_autoscaling_group(autoscale, cluster_name, master_node, opts, slave_group)
        create_autoscaling_policy(autoscale, cluster_name, opts)

        wait_for_tcp_port(master_node.public_dns_name)
        print("SSH ready:")
        print("ssh ubuntu@{h}".format(h=master_node.public_dns_name))
        wait_for_tcp_port(master_node.public_dns_name, port=18080)
        print("Spark master ready:")
        print(
            "Spark WebUI: http://{h}:18080".format(h=master_node.public_dns_name))
    if action == "destroy":
        master_node = find_instance_by_name(conn, cluster_name + '-master')
        if master_node:
            print("Terminating master...")
            conn.create_tags([master_node.id], {"Name": "{c}-master-terminated".format(c=cluster_name)})
            master_node.terminate()
        print("Shutting down autoscaling group...")
        autoscale = boto.ec2.autoscale.connect_to_region(opts.region)
        aglist = autoscale.get_all_groups(names=[cluster_name + "-ag"])
        ag = None
        if aglist:
            ag = aglist[0]
            ag.shutdown_instances()
            instances_ids = [i.instance_id for i in ag.instances]
            instances = conn.get_only_instances(instances_ids)
        else:
            instances = []
        lclist = autoscale.get_all_launch_configurations(names=[cluster_name + "-lc"])
        lc = None
        if lclist:
            lc = lclist[0]
        wait_for_cluster_state(
            conn, instances, cluster_state="terminated", name="instances")
        time.sleep(10)
        if ag:
            try:
                ag.delete()
            except Exception, e:
                print("Couldn't delete autoscaling group: %s" % e)
        if lc:
            try:
                lc.delete()
            except Exception, e:
                print("Couldn't delete launch configuration: %s" % e)
        delete_security_groups(conn, cluster_name)
        print("All done.")


if __name__ == "__main__":
    main()
