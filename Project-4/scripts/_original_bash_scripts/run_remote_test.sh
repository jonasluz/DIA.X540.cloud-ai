#!/bin/bash
# run_remote_test.sh
KEY_FILE="CHAVE_DO_ALUNO.pem" # NOME DO SEU ARQUIVO DE CHAVE LOCAL


if [ -z "$1" ] || [ -z "$2" ]; then
   echo "Uso: ./run_remote_test.sh <URL_ALB> <USUARIOS> [DURACAO]"
   echo "Unidades de Duração: s (segundos), m (minutos)"
   echo "Exemplo: ./run_remote_test.sh http://MeuALB.com 100 2m"
   exit 1
fi


TARGET=$1
USERS=$2
DURATION=${3:-2m}


if [ ! -f ".generator_ip" ]; then echo "Erro: .generator_ip não encontrado. Rode deploy_generator.sh primeiro."; exit 1; fi
GEN_IP=$(cat .generator_ip)


echo ">>> Testando $TARGET com $USERS users por $DURATION..."
ssh -i $KEY_FILE -o StrictHostKeyChecking=no ec2-user@$GEN_IP "./wrapper.sh $TARGET $USERS $DURATION"
echo ">>> Teste concluído. Relatório salvo em ./dados_stats.csv"
# Traz o CSV para a máquina local
scp -i $KEY_FILE -o StrictHostKeyChecking=no ec2-user@$GEN_IP:/home/ec2-user/dados_stats.csv .
