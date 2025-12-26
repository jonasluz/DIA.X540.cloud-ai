param(
    [Parameter(Mandatory = $true)]
    [string]$StackName
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Define Experiments
$experiments = @(
    @{ Name = 'm5-large_250u_5i'; Count = 5; Type = 'm5.large'; Users = 250; Duration = '3m' },
    @{ Name = 'm5-xlarge_250u_2i'; Count = 2; Type = 'm5.xlarge'; Users = 250; Duration = '3m' },
    @{ Name = 'm5-2xlarge_250u_1i'; Count = 1; Type = 'm5.2xlarge'; Users = 250; Duration = '3m' }
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

Write-Host "Batch Execution Complete."
