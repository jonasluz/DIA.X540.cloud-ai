$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Tuning Experiment: 8x t3.micro with Apache Limit (30 workers)
# Target: 400 Users

Write-Host "==========================================================="
Write-Host " TUNING EXPERIMENT: Tuning_t3micro_8_Limit30"
Write-Host "==========================================================="

& (Join-Path $scriptDir 'run_experiment.ps1') `
    -InstanceCount 8 `
    -InstanceType 't3.micro' `
    -Users 400 `
    -Duration '3m' `
    -ExperimentName 'Tuning_t3micro_8_Limit30'

Write-Host "Tuning Experiment Complete."
