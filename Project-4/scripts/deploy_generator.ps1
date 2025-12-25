# deploy_generator.ps1
# PowerShell version of deploy_generator.sh
param(
    [string]$StackName = "benchmark-arena",
    [string]$KeyPairName = "ppgia-dia-2025"
)

$ErrorActionPreference = 'Stop'

# --- CONFIG ---
$STACK_NAME = $StackName
$KEY_NAME = $KeyPairName 

Write-Host "--- Verificando gerador existente ---"
$EXISTING_ID = aws ec2 describe-instances --filters "Name=tag:Name,Values=Load-Generator" "Name=instance-state-name,Values=running,pending" --query "Reservations[0].Instances[0].InstanceId" --output text

if (-not [string]::IsNullOrWhiteSpace($EXISTING_ID) -and $EXISTING_ID -ne 'None') {
    $PUB_IP = aws ec2 describe-instances --instance-ids $EXISTING_ID --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
    Set-Content -Path (Join-Path (Split-Path -Parent $MyInvocation.MyCommand.Path) '.generator_ip') -Value $PUB_IP -Encoding ASCII
    Write-Host "Gerador existente: $PUB_IP"
    exit 0
}

Write-Host "--- Provisionando novo gerador ---"
$AMI_ID = aws ssm get-parameters --names /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2 --query 'Parameters[0].Value' --output text
$SG_ID = aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].Outputs[?OutputKey=='SecurityGroupID'].OutputValue" --output text
$SUBNET_ID = aws cloudformation describe-stack-resources --stack-name $STACK_NAME --query "StackResources[?LogicalResourceId=='PublicSubnet1'].PhysicalResourceId" --output text

# Generate user-data script that installs locust and helper wrapper
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$userDataLocust = Join-Path $scriptDir 'data_scripts/user_data_locust.sh'
$homeDir = '/home/ec2-user'

$ud = @'
#!/bin/bash
yum update -y
yum install -y python3-pip git
pip3 install "urllib3<2.0" locust
HOME_DIR="/home/ec2-user"

cat << 'PY_EOF' > $HOME_DIR/locustfile.py
import random
from locust import HttpUser, task, between
class WordPressUser(HttpUser):
   wait_time = between(1, 3)
   @task(3)
   def view_home(self): self.client.get("/")
   @task(10)
   def view_post(self): self.client.get(f"/post-{random.randint(1, 100)}/", name="/post-detail")
PY_EOF

cat << 'SH_EOF' > $HOME_DIR/wrapper.sh
#!/bin/bash
rm -f dados_*.csv
TARGET=$1
USERS=$2
DURATION=${3:-5m}
SPAWN_RATE=$(($USERS / 10))
[ "$SPAWN_RATE" -lt 1 ] && SPAWN_RATE=1
locust -f locustfile.py --headless --host "$TARGET" --users "$USERS" --spawn-rate "$SPAWN_RATE" --run-time "$DURATION" --stop-timeout 10 --csv dados --only-summary
SH_EOF

chown -R ec2-user:ec2-user $HOME_DIR
chmod +x $HOME_DIR/wrapper.sh
'@

Set-Content -Path $userDataLocust -Value $ud -Encoding UTF8

$INSTANCE_ID = aws ec2 run-instances `
    --image-id $AMI_ID `
    --count 1 `
    --instance-type t3.medium `
    --key-name $KEY_NAME `
    --security-group-ids $SG_ID `
    --subnet-id $SUBNET_ID `
    --user-data "file://$userDataLocust" `
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=Load-Generator}]" `
    --query 'Instances[0].InstanceId' `
    --output text

aws ec2 wait instance-running --instance-ids $INSTANCE_ID | Out-Null
$PUB_IP = aws ec2 describe-instances --instance-ids $INSTANCE_ID --query 'Reservations[0].Instances[0].PublicIpAddress' --output text
Set-Content -Path (Join-Path $scriptDir '.generator_ip') -Value $PUB_IP -Encoding ASCII
Write-Host "Gerador criado: $PUB_IP (Aguarde 4 min para instalação)"