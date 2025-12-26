param(
    #[Parameter(Mandatory = $true)]
    [string]$StackName = 'benchmark-arena'
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Define Experiments
$experiments = @(
    @{ Name = 'tuned_c5-2xlarge_100u_1i'; Count = 1; Type = 'c5.2xlarge'; Users = 100; Duration = '3m' },
    @{ Name = 'tuned_c5-2xlarge_250u_1i'; Count = 1; Type = 'c5.2xlarge'; Users = 250; Duration = '3m' },
    @{ Name = 'tuned_c5-2xlarge_500u_1i'; Count = 1; Type = 'c5.2xlarge'; Users = 500; Duration = '3m' },
    @{ Name = 'tuned_c5-2xlarge_1000u_1i'; Count = 1; Type = 'c5.2xlarge'; Users = 1000; Duration = '3m' }
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
