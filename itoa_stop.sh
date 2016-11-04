#!/bin/bash
mkdir -p /tmp/itoa/

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


