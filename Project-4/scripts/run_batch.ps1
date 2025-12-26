param(
    #[Parameter(Mandatory = $true)]
    [string]$StackName = 'benchmark-arena'
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Define Experiments
$experiments = @(
    @{ Name = 'tuned_t3-micro_100u_48i'; Count = 48; Type = 't3.micro'; Users = 100; Duration = '3m' },
    @{ Name = 'tuned_t3-micro_250u_48i'; Count = 48; Type = 't3.micro'; Users = 250; Duration = '3m' },
    @{ Name = 'tuned_t3-micro_500u_48i'; Count = 48; Type = 't3.micro'; Users = 500; Duration = '3m' },
    @{ Name = 'tuned_t3-micro_1000u_48i'; Count = 48; Type = 't3.micro'; Users = 1000; Duration = '3m' }
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
