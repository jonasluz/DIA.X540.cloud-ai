#!/bin/bash
# teardown.sh
TARGET=$1


delete_instances() {
   TAG=$1
   IDS=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=$TAG" "Name=instance-state-name,Values=running,pending,stopped" --query "Reservations[].Instances[].InstanceId" --output text)
   if [ "$IDS" != "" ] && [ "$IDS" != "None" ]; then
       echo "Terminando $TAG: $IDS"
       aws ec2 terminate-instances --instance-ids $IDS --output text > /dev/null
       aws ec2 wait instance-terminated --instance-ids $IDS
   else
       echo "Nenhum $TAG encontrado."
   fi
}


case "$TARGET" in
   app) delete_instances "App-Benchmark" ;;
   generator) delete_instances "Load-Generator"; rm -f .generator_ip ;;
   db) aws cloudformation delete-stack --stack-name benchmark-arena ;;
   all)
       delete_instances "App-Benchmark"
       delete_instances "Load-Generator"
       rm -f .generator_ip
       aws cloudformation delete-stack --stack-name benchmark-arena
       ;;
   *) echo "Uso: bash teardown.sh <app|generator|db|all>" ;;
esac
