param(
    #[Parameter(Mandatory = $true)]
    [string]$StackName = 'benchmark-arena'
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Define Experiments
$experiments = @(
    @{ Name = 't3-micro_100u_48i'; Count = 48; Type = 't3.micro'; Users = 100; Duration = '3m' },
    @{ Name = 't3-small_100u_24i'; Count = 24; Type = 't3.small'; Users = 100; Duration = '3m' },
    @{ Name = 't3-medium_100u_12i'; Count = 12; Type = 't3.medium'; Users = 100; Duration = '3m' },
    @{ Name = 't3-large_100u_6i'; Count = 6; Type = 't3.large'; Users = 100; Duration = '3m' },
    @{ Name = 't3-xlarge_100u_3i'; Count = 3; Type = 't3.xlarge'; Users = 100; Duration = '3m' },
    @{ Name = 't3-2xlarge_100u_1i'; Count = 1; Type = 't3.2xlarge'; Users = 100; Duration = '3m' }
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
