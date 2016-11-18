#!/bin/sh

PATH="/usr/sbin:/usr/bin:/bin"
#hdisks=`cfgmgr && lspv|grep -v rootvg|awk '{print $1}' |perl -pe 's/\n/ /g'`
hdisks=`cfgmgr && lspv|grep -v rootvg|awk '{print $1}'`

for i in $hdisks;
do
  size=`bootinfo -s $i`;
  let sizeg=$size/1024;
  echo $i"("${sizeg}G")";
done

