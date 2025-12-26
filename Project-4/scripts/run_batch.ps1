param(
    [Parameter(Mandatory = $true)]
    [string]$StackName
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Define Experiments
$experiments = @(
    @{ Name = 'm5-large_100u_5i'; Count = 5; Type = 'm5.large'; Users = 100; Duration = '3m' },
    @{ Name = 'm5-xlarge_100u_2i'; Count = 2; Type = 'm5.xlarge'; Users = 100; Duration = '3m' },
    @{ Name = 'm5-2xlarge_100u_1i'; Count = 1; Type = 'm5.2xlarge'; Users = 100; Duration = '3m' }
)

foreach ($exp in $experiments) {
    Write-Host "==========================================================="
    Write-Host " BATCH ITEM: $($exp.Name)"
    Write-Host "==========================================================="
    
    & (Join-Path $scriptDir 'run_experiment.ps1') `
        -StackName $StackName `
        -InstanceCount $exp.Count `
        -InstanceType $exp.Type `
        -Users $exp.Users `
        -Duration $exp.Duration `
        -ExperimentName $exp.Name
}

# Tear the application down.
& (Join-Path $scriptDir 'teardown.ps1') -Target 'app' -StackName $StackName

Write-Host "Batch Execution Complete."
