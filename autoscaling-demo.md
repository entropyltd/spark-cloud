
# Autoscaling Demo

(This demo assumes default puny instance size)

Once in the shell try running some dummy code to consume the resources, e.g.

```
sc.makeRDD(1 to 1000000).repartition(400).map(_ => (1 to 20000).map(_.toString.length).reduce(_ + _)).reduce(_ + _)
```

You should observe the rate of log entries is around 2 - 5 seconds, e.g.

```
15/12/03 14:01:55 INFO scheduler.TaskSetManager: Starting task 15.0 in stage 1.0 (TID 18, 172.31.60.214, partition 15,PROCESS_LOCAL, 2170 bytes)
15/12/03 14:01:55 INFO scheduler.TaskSetManager: Finished task 12.0 in stage 1.0 (TID 15) in 5668 ms on 172.31.60.214 (13/400)
15/12/03 14:01:55 INFO scheduler.TaskSetManager: Starting task 16.0 in stage 1.0 (TID 19, 172.31.51.194, partition 16,PROCESS_LOCAL, 2170 bytes)
15/12/03 14:01:55 INFO scheduler.TaskSetManager: Finished task 13.0 in stage 1.0 (TID 16) in 5627 ms on 172.31.51.194 (14/400)
15/12/03 14:01:56 INFO scheduler.TaskSetManager: Starting task 17.0 in stage 1.0 (TID 20, 172.31.54.237, partition 17,PROCESS_LOCAL, 2170 bytes)
15/12/03 14:01:56 INFO scheduler.TaskSetManager: Finished task 14.0 in stage 1.0 (TID 17) in 5621 ms on 172.31.54.237 (15/400)
15/12/03 14:02:01 INFO scheduler.TaskSetManager: Starting task 18.0 in stage 1.0 (TID 21, 172.31.60.214, partition 18,PROCESS_LOCAL, 2170 bytes)
15/12/03 14:02:01 INFO scheduler.TaskSetManager: Finished task 15.0 in stage 1.0 (TID 18) in 5665 ms on 172.31.60.214 (16/400)
15/12/03 14:02:01 INFO scheduler.TaskSetManager: Starting task 19.0 in stage 1.0 (TID 22, 172.31.51.194, partition 19,PROCESS_LOCAL, 2170 bytes)
15/12/03 14:02:01 INFO scheduler.TaskSetManager: Finished task 16.0 in stage 1.0 (TID 19) in 5621 ms on 172.31.51.194 (17/400)
```

After around 50 tasks you should see some nodes spinning up in the ec2 dashboard (https://console.aws.amazon.com/ec2/v2/home?region=us-east-1#Instances:securityGroupName=spark-ec2classic-slaves;sort=instanceId)

After around 120 tasks you should see some messages about adding executors:

```
15/12/03 14:05:17 INFO client.AppClient$ClientEndpoint: Executor added: app-20151203140010-0003/3 on worker-20151203140515-172.31.61.144-7078 (172.31.61.144:7078) with 1 cores
15/12/03 14:05:17 INFO cluster.SparkDeploySchedulerBackend: Granted executor ID app-20151203140010-0003/3 on hostPort 172.31.61.144:7078 with 1 cores, 1024.0 MB RAM
15/12/03 14:05:17 INFO client.AppClient$ClientEndpoint: Executor updated: app-20151203140010-0003/3 is now RUNNING
15/12/03 14:05:18 INFO scheduler.TaskSetManager: Starting task 123.0 in stage 1.0 (TID 126, 172.31.51.194, partition 123,PROCESS_LOCAL, 2170 bytes)
15/12/03 14:05:18 INFO scheduler.TaskSetManager: Finished task 120.0 in stage 1.0 (TID 123) in 5628 ms on 172.31.51.194 (121/400)
15/12/03 14:05:18 INFO scheduler.TaskSetManager: Starting task 124.0 in stage 1.0 (TID 127, 172.31.54.237, partition 124,PROCESS_LOCAL, 2170 bytes)
15/12/03 14:05:18 INFO scheduler.TaskSetManager: Finished task 121.0 in stage 1.0 (TID 124) in 5567 ms on 172.31.54.237 (122/400)
15/12/03 14:05:18 INFO client.AppClient$ClientEndpoint: Executor updated: app-20151203140010-0003/3 is now LOADING
15/12/03 14:05:22 INFO client.AppClient$ClientEndpoint: Executor added: app-20151203140010-0003/4 on worker-20151203140520-172.31.61.145-7078 (172.31.61.145:7078) with 1 cores
15/12/03 14:05:22 INFO cluster.SparkDeploySchedulerBackend: Granted executor ID app-20151203140010-0003/4 on hostPort 172.31.61.145:7078 with 1 cores, 1024.0 MB RAM
15/12/03 14:05:22 INFO client.AppClient$ClientEndpoint: Executor updated: app-20151203140010-0003/4 is now RUNNING
15/12/03 14:05:22 INFO client.AppClient$ClientEndpoint: Executor updated: app-20151203140010-0003/4 is now LOADING
15/12/03 14:05:22 INFO scheduler.TaskSetManager: Starting task 125.0 in stage 1.0 (TID 128, 172.31.60.214, partition 125,PROCESS_LOCAL, 2170 bytes)
15/12/03 14:05:22 INFO scheduler.TaskSetManager: Finished task 122.0 in stage 1.0 (TID 125) in 6466 ms on 172.31.60.214 (123/400)
15/12/03 14:05:22 INFO client.AppClient$ClientEndpoint: Executor added: app-20151203140010-0003/5 on worker-20151203140521-172.31.61.146-7078 (172.31.61.146:7078) with 1 cores
15/12/03 14:05:22 INFO cluster.SparkDeploySchedulerBackend: Granted executor ID app-20151203140010-0003/5 on hostPort 172.31.61.146:7078 with 1 cores, 1024.0 MB RAM
15/12/03 14:05:22 INFO client.AppClient$ClientEndpoint: Executor updated: app-20151203140010-0003/5 is now RUNNING
15/12/03 14:05:23 INFO client.AppClient$ClientEndpoint: Executor updated: app-20151203140010-0003/5 is now LOADING
```

Then you should start to see more distinct IP addresses in the log entires and the log entries should be printed at a perceivably faster rate (every second). Your job is now using more nodes!

```
15/12/03 14:07:36 INFO scheduler.TaskSetManager: Starting task 302.0 in stage 1.0 (TID 305, 172.31.60.214, partition 302,PROCESS_LOCAL, 2170 bytes)
15/12/03 14:07:36 INFO scheduler.TaskSetManager: Finished task 294.0 in stage 1.0 (TID 297) in 5641 ms on 172.31.60.214 (295/400)
15/12/03 14:07:37 INFO scheduler.TaskSetManager: Starting task 303.0 in stage 1.0 (TID 306, 172.31.61.142, partition 303,PROCESS_LOCAL, 2170 bytes)
15/12/03 14:07:37 INFO scheduler.TaskSetManager: Finished task 295.0 in stage 1.0 (TID 298) in 5561 ms on 172.31.61.142 (296/400)
15/12/03 14:07:38 INFO scheduler.TaskSetManager: Starting task 304.0 in stage 1.0 (TID 307, 172.31.51.194, partition 304,PROCESS_LOCAL, 2170 bytes)
15/12/03 14:07:38 INFO scheduler.TaskSetManager: Finished task 296.0 in stage 1.0 (TID 299) in 5744 ms on 172.31.51.194 (297/400)
15/12/03 14:07:38 INFO scheduler.TaskSetManager: Starting task 305.0 in stage 1.0 (TID 308, 172.31.54.237, partition 305,PROCESS_LOCAL, 2170 bytes)
15/12/03 14:07:38 INFO scheduler.TaskSetManager: Finished task 297.0 in stage 1.0 (TID 300) in 5611 ms on 172.31.54.237 (298/400)
15/12/03 14:07:38 INFO scheduler.TaskSetManager: Starting task 306.0 in stage 1.0 (TID 309, 172.31.61.144, partition 306,PROCESS_LOCAL, 2170 bytes)
15/12/03 14:07:38 INFO scheduler.TaskSetManager: Finished task 298.0 in stage 1.0 (TID 301) in 5790 ms on 172.31.61.144 (299/400)
15/12/03 14:07:40 INFO scheduler.TaskSetManager: Starting task 307.0 in stage 1.0 (TID 310, 172.31.61.143, partition 307,PROCESS_LOCAL, 2170 bytes)
15/12/03 14:07:40 INFO scheduler.TaskSetManager: Finished task 299.0 in stage 1.0 (TID 302) in 5749 ms on 172.31.61.143 (300/400)
15/12/03 14:07:41 INFO scheduler.TaskSetManager: Starting task 308.0 in stage 1.0 (TID 311, 172.31.61.145, partition 308,PROCESS_LOCAL, 2170 bytes)
15/12/03 14:07:41 INFO scheduler.TaskSetManager: Finished task 301.0 in stage 1.0 (TID 304) in 5402 ms on 172.31.61.145 (301/400)
15/12/03 14:07:41 INFO scheduler.TaskSetManager: Starting task 309.0 in stage 1.0 (TID 312, 172.31.61.146, partition 309,PROCESS_LOCAL, 2170 bytes)
15/12/03 14:07:41 INFO scheduler.TaskSetManager: Finished task 300.0 in stage 1.0 (TID 303) in 5634 ms on 172.31.61.146 (302/400)
15/12/03 14:07:42 INFO scheduler.TaskSetManager: Starting task 310.0 in stage 1.0 (TID 313, 172.31.60.214, partition 310,PROCESS_LOCAL, 2170 bytes)
15/12/03 14:07:42 INFO scheduler.TaskSetManager: Finished task 302.0 in stage 1.0 (TID 305) in 5676 ms on 172.31.60.214 (303/400)
15/12/03 14:07:42 INFO scheduler.TaskSetManager: Starting task 311.0 in stage 1.0 (TID 314, 172.31.61.142, partition 311,PROCESS_LOCAL, 2170 bytes)
```

A minute or two later and it finsihes

```
15/12/03 14:08:49 INFO scheduler.DAGScheduler: Job 0 finished: reduce at <console>:16, took 452.183523 s
res0: Int = -1300313216
```

Now try running the exact same command again (promptly after the other command), you will see the job end faster since the whole job will be running with more resources rather than just part of it:

```
15/12/03 14:16:57 INFO scheduler.DAGScheduler: Job 1 finished: reduce at <console>:16, took 282.684993 s
res1: Int = -1300313216
```

Finally, go make a cup of tea or something and when you return you will see that some of the instances have been terminated, wait for a few more minutes and it will be back to just 2.

http://i.imgur.com/fBLF2EN.gif

