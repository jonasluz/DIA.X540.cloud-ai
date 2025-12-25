# Projeto #4 - Planejamento de Capacidade na Nuvem

## Equipe

- Carlos Duarte - matr. 2527530
- Jonas de A. Luz Jr. - matr. 2519171

----

## Objetivo
>
> Fonte: [Especificação do projeto 4](https://docs.google.com/document/d/13QL64Om-XBFfEqDDyZp8czq-vdWQG-e4mvE3uwRpi-c/edit?tab=t.0)

**Da expecificação original:**

- Arquitetar a infraestrutura de um serviço de blog (WordPress) na AWS.
- Desafio: Maximizar o RPS (Requests Per Second) suportado pelo serviço, sujeito às seguintes restrições:
  - Orçamento: O custo da sua camada de aplicação não pode exceder US$0.50/hora (preço On-Demand us-east-1).
  - Qualidade (SLO): Taxa de Erro < 1% e Latência P95 < 10000ms.
  - Componentes Fixos: O Banco de Dados e o Load Balancer são fornecidos pela "Arena" e não podem ser modificados.
- O trabalho é ajustar a camada de aplicação, escolhendo a melhor combinação de escalabilidade vertical (tamanho da máquina) e horizontal (quantidade de máquinas) para implantar o WordPress.

São fornecidos os *scripts base* para a implementação do WordPress, que podem ser encontrados na pasta `scripts` do projeto.

## Estratégia de Implementação

Nossa estratégia de implementação do trabalho foi a seguinte:

1. Converter os scripts originais para o formato de *batch* do PowerShell, uma vez que o trabalho foi realizado em ambiente de desenvolvimento Windows.
2. Levantar os custos operacionais das instâncias de teste, uma vez que o orçamento foi limitado a US$0.50/hora. Os custos oficiais da AWS foram consultados [no site oficial do serviço EC2](https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1).
3. Definição de experimentos para teste de escalabilidade vertical e horizontal, com o objetivo de encontrar a melhor combinação de tamanho da máquina e quantidade de máquinas para implantar o WordPress.
4. Implementação de scripts de apoio com o objetivo de automatizar a execução dos experimentos e coleta de métricas.
5. Implementação de scripts de apoio para coleta de métricas e análise de resultados.
6. Realização de modificações na configuração da aplicação WordPress para otimização do desempenho.
7. Avaliação dos resultados dos experimentos e coleta de métricas.
8. Elaboração de relatório com os resultados dos experimentos e coleta de métricas e escolha da melhor combinação de tamanho da máquina e quantidade de máquinas para implantar o WordPress.

O detalhamento das etapas é descrito nas seções seguintes.

## Implementação

### Conversão dos Scripts para o PowerShell

Os scripts originais foram convertidos para o formato de *batch* do PowerShell, uma vez que o trabalho foi realizado em ambiente de desenvolvimento Windows.

Os novos scripts constam na pasta `scripts` do projeto, enquanto os scripts originais foram preservados na subpasta `scripts/_original_bash_scripts`.

Foram mantidos em formato bash os scripts que, na verdade, são transferidos para as instâncias de teste, guardados na subpasta `scripts/data_scripts`.

### Levantamento de Custos Operacionais

Os custos operacionais das instâncias de teste foram obtidos [no site oficial do serviço EC2](https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1). A partir da tabela de preços, foram identificadas os tipos de instância candidatos para o experimento, tendo sido selecionadas as instâncias t3.micro (tipo base, mais barato e mais leve, utilizado como exemplo na especificação do trabalho), c5.large, c5.xlarge e c5.2xlarge (tipo premium, mais caro e mais pesado). Estas escolhas visavam permitir os testes de escalabilidade horizontal e vertical, conforme definido na especificação do trabalho. O Quadro 1 apresenta os custos operacionais das instâncias de teste e respectivas quantidades máximas, considerando-se o limite de US$0.50/hora.

| Instância | Preço/h (US$) | Qtde. Máxima |
| --- | --- | --- |
| [t3.micro](https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#InstanceTypeDetails:instanceType=t3.micro) | 0.0104 | 48 |
| [c5.large](https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#InstanceTypeDetails:instanceType=c5.large) | 0.085 | 5 |
| [c5.xlarge](https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#InstanceTypeDetails:instanceType=c5.xlarge) | 0.17 | 2 |
| [c5.2xlarge](https://us-east-1.console.aws.amazon.com/ec2/home?region=us-east-1#InstanceTypeDetails:instanceType=c5.2xlarge) | 0.34 | 1 |

### Definição dos Experimentos

Os experimentos foram definidos na tabela abaixo:

#### Fase 1  Escalabilidade Horizontal

O ambiente foi implantado com aumento de instâncias de *t3.micro*; no caso, 4 e 8 instâncias.
O que se procurou avaliar neste caso é se alguma destas configurações atenderiam os requisitos originais do trabalho, ou seja, se atenderiam ao orçamento de US$0.50/hora e ao SLO de Taxa de Erro < 1% e Latência P95 < 10000ms.

Os resultados, detalhados mas planilhas [ScaleOut_t3micro_4_stats.csv](../results/ScaleOut_t3micro_4_stats.csv) e [ScaleOut_t3micro_8_stats.csv](../results/ScaleOut_t3micro_8_stats.csv), são consolidados na tabela abaixo:

| Qtde. Instâncias | RPS | Latência P95 (ms) | Custo/h (US$) | Cumpriu taxa de erro < 1%? | Cumpriu latência P95 < 10000ms? |
| --- | --- | --- | --- | --- | --- |
| 4 | 57.29 | 1057.996 | 0.0416 | Não | Não |
| 8 | 25.2 | 1057.996 | 0.0832 | Não | Não |

#### Fase 2  Escalabilidade Vertical
