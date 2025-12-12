# run_remote_test.ps1
# PowerShell version of run_remote_test.sh

param(
    [Parameter(Mandatory=$true)][string]$Target,
    [Parameter(Mandatory=$true)][int]$Users,
    [string]$Duration = '2m'
)

$ErrorActionPreference = 'Stop'

$KEY_FILE        = 'ppgia-dia-2025.pem'
$scriptDir       = Split-Path -Parent $MyInvocation.MyCommand.Path
$generatorIpFile = Join-Path $scriptDir '.generator_ip'

if (-not (Test-Path $generatorIpFile)) {
    Write-Error "Erro: .generator_ip não encontrado. Rode deploy_generator.ps1 primeiro."
}
$GEN_IP = Get-Content -Path $generatorIpFile -Raw
$GEN_IP = $GEN_IP.Trim()

if (-not (Test-Path (Join-Path $scriptDir $KEY_FILE))) {
    Write-Warning "Arquivo de chave '$KEY_FILE' não encontrado no diretório do script. Ajuste o caminho conforme necessário."
}

Write-Host ">>> Testando $Target com $Users users por $Duration..."

# Ensure OpenSSH client is available on Windows
try {
    $sshVersion = & ssh -V 2>&1
} catch {
    Write-Error 'ssh client não encontrado no PATH. Instale OpenSSH Client no Windows.'
}

# Remote execution of wrapper.sh
& ssh -i (Join-Path $scriptDir $KEY_FILE) -o StrictHostKeyChecking=no "ec2-user@${GEN_IP}" "./wrapper.sh $Target $Users $Duration"

Write-Host ">>> Teste concluído. Relatório salvo em ./dados_stats.csv"

# Copy CSV back
& scp -i (Join-Path $scriptDir $KEY_FILE) -o StrictHostKeyChecking=no "ec2-user@${GEN_IP}:/home/ec2-user/dados_stats.csv" (Join-Path $scriptDir '../results' "${Users}_users_for_${Duration}_stats.csv")

Write-Host 'Concluído.'