## 📊 Sistema de Gestão de Produção Agrícola e Análise

Este projeto tem como objetivo desenvolver um sistema completo de controle e análise da produção agrícola, permitindo que o produtor registre suas entradas e saídas de produção, acompanhe seus investimentos e visualize relatórios de desempenho.

A aplicação foi desenvolvida em Python e R, integrando coleta de dados, armazenamento em banco de dados e geração de relatórios automáticos com gráficos e insights para apoiar a tomada de decisão sobre o melhor momento de investir, produzir e vender.

## 🎯 Objetivos do sistema

O sistema busca responder perguntas práticas do dono da fazenda, como:
- 📈 Qual mês mais produziu em relação ao investimento feito?
→ Exemplo: investi 100 e produzi 200; investi 110 e produzi 250 — qual investimento foi mais eficiente?
- 💰 Qual mês teve maior volume de vendas e melhor preço médio?
- 🗓️ Quando vale mais a pena produzir, investir e vender?

Essas informações são apresentadas em relatórios automáticos, baseados nos dados coletados no dia a dia da produção.

```
/src
  /python
    app.py               -> Interface de cadastro de dados
    db.py                -> Conexão e manipulação do banco de dados
    export_csv.py        -> Exporta dados para análise em R
  /r
    analise.R            -> Processa dados e gera indicadores
    graficos.R           -> Cria gráficos de desempenho
    relatorio.Rmd        -> Gera relatório automático em PDF/HTML
README.md
```

## TO-DOs
- [ ] modelagem do banco de dados, definindo quais são as tabelas e campos e de que tipo cada campo será
- [ ] app.py para interface de linha de comando (CLI) para cadastro dos produtos
- [ ] db.py para operações com o banco de dados
- [ ] export_csv.py para operação de exportar os dados em csv para futura analise em R
- [ ] analise.r para gerar os indicadores quantitativos (númericos)
- [ ] graficos.r para gerar os gráficos
- [ ] (BONUS) relatorio.Rmd caso for fácil gerar um relatorio exportado para não ter que ver o relatorio diretamente pelo R
- [ ] (BONUS) executar a geração do relatorio do R de maneira simples, como se fosse clicar em um "executavel" ao invés de gerar diretamente dentro do Rstudio