param(
    #[Parameter(Mandatory = $true)]
    [string]$StackName = 'benchmark-arena'
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Define Experiments
$experiments = @(
    @{ Name = 'tuned_t3-small_100u_24i'; Count = 24; Type = 't3.small'; Users = 100; Duration = '3m' },
    @{ Name = 'tuned_t3-small_250u_24i'; Count = 24; Type = 't3.small'; Users = 250; Duration = '3m' },
    @{ Name = 'tuned_t3-small_500u_24i'; Count = 24; Type = 't3.small'; Users = 500; Duration = '3m' },
    @{ Name = 'tuned_t3-small_1000u_24i'; Count = 24; Type = 't3.small'; Users = 1000; Duration = '3m' }
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
