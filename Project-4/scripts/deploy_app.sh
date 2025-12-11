#!/bin/bash
# deploy_app.sh


# --- CONFIGURAÇÃO (EDITE AQUI) ---
INSTANCE_COUNT=1          # Quantidade de instâncias (Escala Horizontal)
INSTANCE_TYPE="t3.micro"  # Tipo da instância (Escala Vertical)
KEY_NAME="CHAVE_DO_ALUNO" # NOME DA SUA CHAVE NA AWS
STACK_NAME="benchmark-arena"
# ---------------------------------


# --- Validação de Outputs ---
get_output() {
   KEY=$1
   VAL=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].Outputs[?OutputKey=='$KEY'].OutputValue" --output text 2>/dev/null)
   if [ "$VAL" == "None" ] || [ -z "$VAL" ]; then
       echo "ERRO CRÍTICO: Output '$KEY' não encontrado na stack '$STACK_NAME'." >&2
       return 1
   fi
   echo "$VAL"
}


echo "--- 1. Lendo dados da Arena ---"
TG_ARN=$(get_output "TargetGroupARN") || exit 1
DB_IP=$(get_output "DatabasePrivateIP") || exit 1
SG_ID=$(get_output "SecurityGroupID") || exit 1
LB_DNS=$(get_output "LoadBalancerDNS") || exit 1
SUBNET_ID=$(aws cloudformation describe-stack-resources --stack-name $STACK_NAME --query "StackResources[?LogicalResourceId=='PublicSubnet1'].PhysicalResourceId" --output text)
AMI_ID=$(aws ssm get-parameters --names /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2 --query 'Parameters[0].Value' --output text)


# --- Check de Idempotência ---
EXISTING_IDS=$(aws ec2 describe-instances --filters "Name=tag:Name,Values=App-Benchmark" "Name=instance-state-name,Values=running,pending" --query "Reservations[].Instances[].InstanceId" --output text)
if [ "$EXISTING_IDS" != "" ] && [ "$EXISTING_IDS" != "None" ]; then
   echo "AVISO: Instâncias já existem ($EXISTING_IDS). URL: http://$LB_DNS"
   echo "       Para aplicar nova configuração, rode 'bash teardown.sh app' antes."
   exit 0
fi


echo "--- 2. Preparando Configuração ---"
# Injeta os valores reais no template de configuração
sed -e "s/PLACEHOLDER_DB_IP/$DB_IP/g" \
   -e "s/PLACEHOLDER_LB_DNS/$LB_DNS/g" \
   user_data_template.sh > user_data_final.sh


echo "--- 3. Lançando Aplicação ($INSTANCE_COUNT x $INSTANCE_TYPE) ---"
INSTANCE_IDS=$(aws ec2 run-instances \
   --image-id $AMI_ID \
   --count $INSTANCE_COUNT \
   --instance-type $INSTANCE_TYPE \
   --key-name $KEY_NAME \
   --security-group-ids $SG_ID \
   --subnet-id $SUBNET_ID \
   --user-data file://user_data_final.sh \
   --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=App-Benchmark}]' \
   --query 'Instances[*].InstanceId' \
   --output text)


echo "Instâncias criadas: $INSTANCE_IDS"
echo "Aguardando boot (30s)..."
aws ec2 wait instance-running --instance-ids $INSTANCE_IDS


echo "Registrando no Load Balancer..."
for id in $INSTANCE_IDS; do
   aws elbv2 register-targets --target-group-arn "$TG_ARN" --targets Id=$id
done


echo "========================================="
echo " DEPLOY PRONTO: http://$LB_DNS"
echo "========================================="


