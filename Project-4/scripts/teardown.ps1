# teardown.ps1
# PowerShell version of teardown.sh

param(
    [Parameter(Mandatory=$true)][ValidateSet('app','generator','db','all')][string]$Target
)

$ErrorActionPreference = 'Stop'
$STACK_NAME = 'benchmark-arena'
$scriptDir  = Split-Path -Parent $MyInvocation.MyCommand.Path

function Remove-InstancesByTag {
    param([Parameter(Mandatory=$true)][string]$TagValue)
    $ids = aws ec2 describe-instances --filters "Name=tag:Name,Values=$TagValue" "Name=instance-state-name,Values=running,pending,stopped" --query "Reservations[].Instances[].InstanceId" --output text
    if (-not [string]::IsNullOrWhiteSpace($ids) -and $ids -ne 'None') {
        Write-Host "Terminando ${TagValue}: $ids"
        aws ec2 terminate-instances --instance-ids $ids --output text | Out-Null
        aws ec2 wait instance-terminated --instance-ids $ids | Out-Null
    } else {
        Write-Host "Nenhum $TagValue encontrado."
    }
}

switch ($Target) {
    'app' {
        Remove-InstancesByTag -TagValue 'App-Benchmark'
    }
    'generator' {
        Remove-InstancesByTag -TagValue 'Load-Generator'
        Remove-Item -ErrorAction Ignore -Path (Join-Path $scriptDir '.generator_ip')
    }
    'db' {
        aws cloudformation delete-stack --stack-name $STACK_NAME | Out-Null
        Write-Host "Solicitada remoção da stack $STACK_NAME."
    }
    'all' {
        Remove-InstancesByTag -TagValue 'App-Benchmark'
        Remove-InstancesByTag -TagValue 'Load-Generator'
        Remove-Item -ErrorAction Ignore -Path (Join-Path $scriptDir '.generator_ip')
        aws cloudformation delete-stack --stack-name $STACK_NAME | Out-Null
        Write-Host "Solicitada remoção da stack $STACK_NAME."
    }
}