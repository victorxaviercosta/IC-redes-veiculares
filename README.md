# IC-redes-veiculares
Repositório destinado aos trabalhos desenvolvidos no âmbito do projeto de Iniciação Cientifica sobre o tema **"Soluções para redução de congestionamento em Redes Veiculares e Veículos Elétricos"**. DECOM - UFOP


## Descrição

Este projeto investiga estratégias para o **posicionamento de estações de recarga** em redes viárias, com o objetivo de melhorar o atendimento a veículos elétricos e reduzir impactos como:

- Tempo de deslocamento até estações.
- Distância percorrida.
- Possíveis congestionamentos associados à demanda por recarga.

As simulações são realizadas utilizando o simulador de tráfego [SUMO (Simulation of Urban Mobility)](https://github.com/eclipse-sumo/sumo).

O trabalho tem como principais objetivos:

- Elabaorar um framework de simulação de veículos elétricos;
- Avaliar estratégias de deposição de estações de recarga;
- Investigar o efeito da distribuição espacial das estações.

Foram avaliados comparativamente os métodos de deposição Aleatória, Gulosa, Aleatória por região (*Region Random*) e Gulosa por Região (*Region Greedy*).
Os resultados obtidos indicam que abordagens baseadas em regiões apresentam desempenho superior às versões simples dos métodos avaliados, proporcionando reduções significativas no tempo e na distância percorrida pelos veículos até o atendimento. 

Além disso, observa-se que a abordagem gulosa baseada em regiões apresenta maior consistência no atendimento da demanda, embora soluções aleatórias também apresentem desempenhos competitivos nos cenários simulados.


## Pré-requistos
- Python 3
- SUMO 1.23.1 ou superior

para a geração do ambiente virtual python com as dependências listadas em `requirements.txt` execute:

```bash
make
```

## Execução

A partir da raiz do projeto:

```bash
python -m src.main
```

## Geração de cenários de teste

Exemplo de geração dos arquivos de rota para os cenarios de teste:

```bash
python -m src.tools.generic_routes -wd scenarios/BH -i bh.net.xml -o bh_routes.rou.xml -n 5000 -f0

python -m src.tools.define_ev -wd scenarios/BH -i bh_routes.rou.xml -p (0.01, 0.05, 0.1, 0.15, 0.2) -n 5
```