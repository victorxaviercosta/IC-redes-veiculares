# IC-redes-veiculares
Repositório destinado aos trabalhos desenvolvidos no âmbito do projeto de Iniciação Cientifica sobre o tema "Soluções para redução de congestionamento em Redes Veiculares e Veículos Elétricos". DECOM - UFOP


```
python -m src.tools.generic_routes -wd scenarios/BH -i bh.net.xml -o bh_routes.rou.xml -n 5000 -f0

python -m src.tools.define_ev -wd scenarios/BH -i bh_routes.rou.xml -p (0.01, 0.05, 0.1, 0.15, 0.2) -n 5
```