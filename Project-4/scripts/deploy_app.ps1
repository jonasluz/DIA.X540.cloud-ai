param(
    [int]$InstanceCount = 1,
    [string]$InstanceType = "t3.micro"
)

# deploy_app.ps1
# PowerShell version of deploy_app.sh

# --- CONFIGURAÇÃO ----------------
$KEY_NAME       = "ppgia-dia-2025"      # Chave SSH cadastrada na AWS
$STACK_NAME     = "benchmark-arena"
# ---------------------------------

$ErrorActionPreference = 'Stop'

Write-Host "DEBUG: InstanceCount=$InstanceCount"
Write-Host "DEBUG: InstanceType=$InstanceType"

function Get-Output {
    param(
        [Parameter(Mandatory=$true)][string]$Key
    )
    try {
        $val = aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].Outputs[?OutputKey=='$Key'].OutputValue" --output text 2>$null
        if ([string]::IsNullOrWhiteSpace($val) -or $val -eq 'None') {
            Write-Error "ERRO CRÍTICO: Output '$Key' não encontrado na stack '$STACK_NAME'."
        }
        return $val
    } catch {
        throw $_
    }
}

Write-Host "--- 1. Lendo dados da Arena ---"
$TG_ARN = Get-Output -Key 'TargetGroupARN'
$DB_IP  = Get-Output -Key 'DatabasePrivateIP'
$SG_ID  = Get-Output -Key 'SecurityGroupID'
$LB_DNS = Get-Output -Key 'LoadBalancerDNS'

# PublicSubnet1 PhysicalResourceId
$SUBNET_ID = aws cloudformation describe-stack-resources --stack-name $STACK_NAME --query "StackResources[?LogicalResourceId=='PublicSubnet1'].PhysicalResourceId" --output text
# Latest Amazon Linux 2 AMI (x86_64)
$AMI_ID    = aws ssm get-parameters --names /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2 --query 'Parameters[0].Value' --output text

# --- Check de Idempotência ---
$EXISTING_IDS = aws ec2 describe-instances --filters "Name=tag:Name,Values=App-Benchmark" "Name=instance-state-name,Values=running,pending" --query "Reservations[].Instances[].InstanceId" --output text
if (-not [string]::IsNullOrWhiteSpace($EXISTING_IDS) -and $EXISTING_IDS -ne 'None') {
    Write-Host "AVISO: Instâncias já existem ($EXISTING_IDS). URL: http://$LB_DNS"
    Write-Host "       Para aplicar nova configuração, rode 'pwsh ./teardown.ps1 app' antes."
    exit 0
}

Write-Host "--- 2. Preparando Configuração ---"
# Injeta os valores reais no template de configuração
$scriptDir        = Split-Path -Parent $MyInvocation.MyCommand.Path
$userDataTemplate = Join-Path $scriptDir 'data_scripts/user_data_template.sh'
$userDataFinal    = Join-Path $scriptDir 'data_scripts/user_data_final.sh'

if (-not (Test-Path $userDataTemplate)) {
    throw "Arquivo de template não encontrado: $userDataTemplate"
}

# Substituição simples de placeholders
$content = Get-Content -Path $userDataTemplate -Raw
$content = $content -replace 'PLACEHOLDER_DB_IP', [Regex]::Escape($DB_IP)
$content = $content -replace 'PLACEHOLDER_LB_DNS', [Regex]::Escape($LB_DNS)
Set-Content -Path $userDataFinal -Value $content -Encoding UTF8

Write-Host "--- 3. Lançando Aplicação ($InstanceCount x $InstanceType) ---"
$INSTANCE_IDS = aws ec2 run-instances `
    --image-id $AMI_ID `
    --count $InstanceCount `
    --instance-type $InstanceType `
    --key-name $KEY_NAME `
    --security-group-ids $SG_ID `
    --subnet-id $SUBNET_ID `
    --user-data "file://$userDataFinal" `
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=App-Benchmark}]" `
    --query 'Instances[*].InstanceId' `
    --output text

Write-Host "Instâncias criadas: $INSTANCE_IDS"
$ids = $INSTANCE_IDS -split '\s+' | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }

Write-Host "Aguardando boot (30s)..."
# Espera até status running
if ($ids.Count -gt 0) {
    aws ec2 wait instance-running --instance-ids $ids | Out-Null
}

Write-Host "Registrando no Load Balancer..."
foreach ($id in $ids) {
    aws elbv2 register-targets --target-group-arn "$TG_ARN" --targets Id=$id | Out-Null
}

Write-Host "========================================="
Write-Host " DEPLOY PRONTO: http://$LB_DNS"
Write-Host "========================================="