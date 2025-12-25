param(
    [Parameter(Mandatory = $true)][int]$InstanceCount = 1,
    [Parameter(Mandatory = $true)][string]$InstanceType = 't3.micro',
    [Parameter(Mandatory = $true)][int]$Users = 100,
    [string]$Duration = '3m',
    [Parameter(Mandatory = $true)][string]$ExperimentName,
    [Parameter(Mandatory = $true)][string]$StackName
)

$ErrorActionPreference = 'Stop'
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "==========================================================="
Write-Host " EXPERIMENT: $ExperimentName"
Write-Host " Config: $InstanceCount x $InstanceType"
Write-Host " Load: $Users users for $Duration"
Write-Host "==========================================================="

# 1. Teardown existing app
Write-Host ">>> Step 1: Teardown..."
& (Join-Path $scriptDir 'teardown.ps1') app -StackName $StackName

# 2. Deploy new config
Write-Host ">>> Step 2: Deploying..."
& (Join-Path $scriptDir 'deploy_app.ps1') -InstanceCount $InstanceCount -InstanceType $InstanceType -StackName $StackName

# 3. Get LB DNS (Re-fetch to be safe)
$LB_DNS = aws cloudformation describe-stacks --stack-name $StackName --query "Stacks[0].Outputs[?OutputKey=='LoadBalancerDNS'].OutputValue" --output text
if ([string]::IsNullOrWhiteSpace($LB_DNS) -or $LB_DNS -eq 'None') {
    throw "Could not retrieve Load Balancer DNS."
}
$TargetUrl = "http://$LB_DNS"
Write-Host ">>> Target URL: $TargetUrl"

# 4. Wait for App Health
Write-Host ">>> Step 3: Waiting for App Health..."
$maxRetries = 60 # 60 * 10s = 10 minutes
$retryCount = 0
$healthy = $false

while ($retryCount -lt $maxRetries) {
    try {
        $response = Invoke-WebRequest -Uri $TargetUrl -Method Head -ErrorAction Stop -TimeoutSec 5
        if ($response.StatusCode -eq 200) {
            Write-Host "App is healthy!"
            $healthy = $true
            break
        }
    }
    catch {
        Write-Host "Waiting for app to be ready... ($($retryCount + 1)/$maxRetries)"
    }
    Start-Sleep -Seconds 10
    $retryCount++
}

if (-not $healthy) {
    throw "App did not become healthy within the timeout period."
}

# 5. Run Test
Write-Host ">>> Step 4: Running Load Test..."
& (Join-Path $scriptDir 'run_remote_test.ps1') -Target $TargetUrl -Users $Users -Duration $Duration

# 6. Save Results
Write-Host ">>> Step 5: Saving Results..."
$defaultResultFile = Join-Path $scriptDir '../results' "${Users}_users_for_${Duration}_stats.csv"
$newResultFile = Join-Path $scriptDir '../results' "${ExperimentName}_stats.csv"

if (Test-Path $defaultResultFile) {
    Move-Item -Path $defaultResultFile -Destination $newResultFile -Force
    Write-Host "Results saved to: $newResultFile"
}
else {
    Write-Error "Result file not found: $defaultResultFile"
}

Write-Host ">>> Experiment $ExperimentName Complete!"
