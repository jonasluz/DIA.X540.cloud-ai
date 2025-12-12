$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Define Experiments
# Strategy: Test Scale Out (cheap/many) vs Scale Up (expensive/few) vs Hybrid
# Budget Limit: $0.50/hr

$experiments = @(
    # --- Scale Out (t3.micro - ~$0.0104/hr each) ---
    # 4x t3.micro (~$0.04/hr)
    @{ Name='ScaleOut_t3micro_4'; Count=4; Type='t3.micro'; Users=200; Duration='3m' },
    # 8x t3.micro (~$0.08/hr)
    @{ Name='ScaleOut_t3micro_8'; Count=8; Type='t3.micro'; Users=400; Duration='3m' },

    # --- Scale Up (Compute Optimized c5 - ~$0.085/hr per large) ---
    # 1x c5.large (~$0.085/hr)
    @{ Name='ScaleUp_c5large_1';  Count=1; Type='c5.large';  Users=200; Duration='3m' },
    # 1x c5.xlarge (~$0.17/hr)
    @{ Name='ScaleUp_c5xlarge_1'; Count=1; Type='c5.xlarge'; Users=500; Duration='3m' },
    # 1x c5.2xlarge (~$0.34/hr)
    @{ Name='ScaleUp_c52xlarge_1'; Count=1; Type='c5.2xlarge'; Users=1000; Duration='3m' },

    # --- Hybrid / Premium Scale Out ---
    # 2x c5.large (~$0.17/hr) - Compare vs 1x c5.xlarge
    @{ Name='ScaleOut_c5large_2'; Count=2; Type='c5.large'; Users=500; Duration='3m' }
)

foreach ($exp in $experiments) {
    Write-Host "==========================================================="
    Write-Host " BATCH ITEM: $($exp.Name)"
    Write-Host "==========================================================="
    
    & (Join-Path $scriptDir 'run_experiment.ps1') `
        -InstanceCount $exp.Count `
        -InstanceType $exp.Type `
        -Users $exp.Users `
        -Duration $exp.Duration `
        -ExperimentName $exp.Name
}

Write-Host "Batch Execution Complete."
