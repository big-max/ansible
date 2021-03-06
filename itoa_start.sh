#!/bin/bash

tornado_pid=`ps -ef|grep -i '/opt/tornado/server.py'|grep -v grep|awk '{print $2}'`
if [ ! -z "$tornado_pid" ];
then
   kill -9 $tornado_pid
fi 

celery_pid=`ps -ef|grep -i celery|grep -v grep|awk '{print $2}'`
if [ ! -z "$celery_pid" ];
then
   for c in $celery_pid 
   do 
      kill -9 $c
   done
fi   

tomcat_pid=`ps -ef|grep -i tomcat|grep -v grep|awk '{print $2}'`
if [ ! -z "$tomcat_pid" ];
then
   kill -9 $tomcat_pid
fi 

nohup python /opt/tornado/server.py 1>/var/log/itoa/tornado.out 2>/var/log/itoa/tornado.err &
cd /opt/tornado;nohup celery -A proj worker -l info -c 5 1>/var/log/itoa/celery.out 2>/var/log/itoa/celery.err & 
nohup /opt/apache-tomcat-7.0.69/bin/startup.sh 1>/var/log/itoa/tomcat.out 2>/var/log/itoa/tomcat.err & 

