# Tuning de Aplicação para Diferentes Cenários de Hardware

Este documento detalha a estratégia de configuração do Apache/PHP para otimizar o desempenho em diferentes capacidades de hardware.

## Premissas de Cálculo

Para determinar o número ideal de workers (`MaxRequestWorkers`), utilizamos a seguinte fórmula baseada no consumo de memória, que é o recurso crítico para evitar swapping e OOM (Out of Memory):

$$ \text{MaxRequestWorkers} = \frac{\text{Memória Total} - \text{Memória Reservada SO}}{\text{Memória Média por Processo}} $$

* **Memória Reservada SO**: Estimativa de 250MB a 1GB dependendo do tamanho da instância (para Kernel, logs, cache de disco básico).
* **Memória Média por Processo (Apache + PHP)**: ~35MB (Valor típico para WordPress sem plugins pesados).

---

## Cenário 1: 2 vCPUs e 1GB de Memória (ex: t3.micro)

Este é um ambiente **altamente restrito por memória**. O gargalo principal será a RAM. Se configurarmos workers demais, a máquina fará swap e travará.

* **Cálculo**: `(1024MB - 250MB) / 35MB` ≈ **22 workers**
* **Ajuste Prático**: Podemos forçar até **30** (como visto nos testes anteriores), mas 25 é mais seguro.

**Configuração Recomendada (`httpd.conf` ou `00-custom.conf`):**

```apache
<IfModule mpm_prefork_module>
    StartServers             2
    MinSpareServers          2
    MaxSpareServers          5
    MaxRequestWorkers       25
    ServerLimit             25
</IfModule>
```

---

## Cenário 2: 2 vCPUs e 2GB de Memória (ex: t3.small)

Ambiente mais equilibrado para baixo tráfego. A memória ainda é o limite primário, mas permite o dobro de concorrência.

* **Cálculo**: `(2048MB - 350MB) / 35MB` ≈ **48 workers**

**Configuração Recomendada:**

```apache
<IfModule mpm_prefork_module>
    StartServers             5
    MinSpareServers          5
    MaxSpareServers         10
    MaxRequestWorkers       50
    ServerLimit             50
</IfModule>
```

---

## Cenário 3: 2 vCPUs e 4GB de Memória (ex: t3.medium)

Aqui o gargalo começa a migrar da Memória para a **CPU**.
Com 4GB, poderíamos ter ~100 workers. Porém, 2 vCPUs podem ter dificuldade em processar 100 requisições PHP pesadas simultaneamente, gerando latência (fila de CPU).

* **Cálculo Memória**: `(4096MB - 500MB) / 35MB` ≈ **102 workers**
* **Consideração de CPU**: Manteremos o limite pela memória, mas monitorando o *CPU Load*.

**Configuração Recomendada:**

```apache
<IfModule mpm_prefork_module>
    StartServers             5
    MinSpareServers          5
    MaxSpareServers         10
    MaxRequestWorkers      100
    ServerLimit            100
</IfModule>
```

---

## Cenário 4: 8 vCPUs e 16GB de Memória (ex: c5.2xlarge)

Ambiente de alta performance. O gargalo provavelmente será o **Banco de Dados** ou I/O de rede, não mais a aplicação em si.
Precisamos garantir que o PHP Opcache tenha memória suficiente e que não haja limites artificiais baixos.

* **Cálculo**: `(16384MB - 1000MB) / 35MB` ≈ **440 workers**

**Configuração Recomendada:**

```apache
<IfModule mpm_prefork_module>
    StartServers            10
    MinSpareServers         10
    MaxSpareServers         20
    MaxRequestWorkers      450
    ServerLimit            450
</IfModule>
```

**Ajustes Adicionais Importantes (PHP.ini):**
Para este cenário, aumentar o buffer do Opcache é crucial para performance:

```ini
opcache.memory_consumption=256
opcache.max_accelerated_files=10000
opcache.validate_timestamps=0 ; Em produção, para evitar I/O de disco
```

---

## Resumo Comparativo

| Cenário | vCPU | RAM | MaxWorkers (Est.) | Gargalo Provável |
| :--- | :--- | :--- | :--- | :--- |
| **1** | 2 | 1GB | **25 - 30** | Memória (OOM) |
| **2** | 2 | 2GB | **50** | Memória |
| **3** | 2 | 4GB | **100** | CPU / Memória |
| **4** | 8 | 16GB | **450** | Banco de Dados / Rede |
