param(
    [Parameter(Mandatory = $true)]
    [string]$StackName
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Define Experiments
$experiments = @(
    @{ Name = 't3-small_500u_12i'; Count = 12; Type = 't3.small'; Users = 500; Duration = '3m' },
    #@{ Name = 't3-small_1000u_24i'; Count = 24; Type = 't3.small'; Users = 1000; Duration = '3m' },
    @{ Name = 't3-medium_500u_6i'; Count = 6; Type = 't3.medium'; Users = 500; Duration = '3m' },
    #@{ Name = 't3-medium_1000u_12i'; Count = 12; Type = 't3.medium'; Users = 1000; Duration = '3m' },
    @{ Name = 't3-large_500u_3i'; Count = 3; Type = 't3.large'; Users = 500; Duration = '3m' },
    #@{ Name = 't3-large_1000u_6i'; Count = 6; Type = 't3.large'; Users = 1000; Duration = '3m' },
    @{ Name = 't3-xlarge_500u_2i'; Count = 1; Type = 't3.xlarge'; Users = 500; Duration = '3m' },
    #@{ Name = 't3-xlarge_1000u_4i'; Count = 3; Type = 't3.xlarge'; Users = 1000; Duration = '3m' },
    @{ Name = 't3-2xlarge_1000u_1i'; Count = 1; Type = 't3.2xlarge'; Users = 1000; Duration = '3m' }
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
