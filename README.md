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

## ✅ Status do Projeto

- [x] **Modelagem do banco de dados** - Tabela `agricultural_production` com todos os campos necessários
- [x] **app.py** - Interface CLI completa com menu interativo para CRUD
- [x] **db.py** - Operações completas de banco de dados (Create, Read, Update, Delete)
- [x] **export_csv.py** - Exportação de dados para CSV com métricas calculadas
- [x] **analise.r** - Script de análise quantitativa com indicadores de ROI, eficiência e ciclos
- [x] **graficos.r** - Geração de gráficos e visualizações
- [x] **relatorio.Rmd** - Relatório automático em HTML/PDF com análises integradas
- [x] **setup.py** - Script de configuração e dados de exemplo

## 🚀 Como Executar o Projeto

### Pré-requisitos

1. **Python 3.8+** instalado
2. **R 4.0+** instalado
3. **Oracle Database** acessível (FIAP)
4. **Bibliotecas Python:**
   ```bash
   pip install oracledb
   ```

5. **Bibliotecas R:**
   ```r
   install.packages(c("readr", "dplyr", "ggplot2", "lubridate", "scales", 
                      "gridExtra", "RColorBrewer", "knitr", "DT", "plotly", "rmarkdown"))
   ```

### Passo a Passo

#### 1. Configuração Inicial
```bash
# Execute o script de setup (cria diretórios e dados de exemplo)
python setup.py
```

#### 2. Interface Principal (CLI)
```bash
# Execute a interface de usuário
python src/python/app.py
```

**Funcionalidades da CLI:**
- 📝 Cadastrar nova produção
- 📋 Listar todas as produções
- 🔍 Buscar produção por ID
- ✏️ Atualizar produção
- 🗑️ Deletar produção
- 📊 Exportar dados para CSV
- 📈 Gerar relatórios (R)

#### 3. Análises e Relatórios

**Exportar dados do banco:**
```bash
python src/python/export_csv.py
```

**Executar análise quantitativa:**
```bash
Rscript src/r/analise.r
```

**Gerar gráficos:**
```bash
Rscript src/r/graficos.r
```

**Gerar relatório completo:**
```bash
Rscript -e "rmarkdown::render('src/r/relatorio.Rmd')"
```

### Estrutura dos Dados

A aplicação trabalha com os seguintes campos:
- **Produto:** Nome do produto agrícola
- **Quantidade:** Quantidade produzida
- **Custo:** Investimento na produção
- **Preço de Venda:** Valor de venda
- **Datas:** Plantio e colheita
- **Status:** PLANTED, HARVESTED, SOLD

### Métricas Calculadas

- **ROI (Return on Investment):** Retorno percentual do investimento
- **Eficiência de Produção:** Quantidade produzida por real investido
- **Ciclo Produtivo:** Tempo entre plantio e colheita
- **Análise Temporal:** Performance por mês/período
- **Correlações:** Investimento vs. Retorno

## 📊 Exemplos de Saída

### CLI Interface
```
🌾 SISTEMA DE GESTÃO DE PRODUÇÃO AGRÍCOLA 🌾
==================================================
1. 📝 Cadastrar nova produção
2. 📋 Listar todas as produções
3. 🔍 Buscar produção por ID
...
```

### Relatórios Gerados
- **CSV:** Dados estruturados para análise
- **Gráficos PNG:** Visualizações de performance
- **Relatório HTML/PDF:** Análise executiva completa

## 🎯 Casos de Uso

### Para o Agricultor:
1. **Registrar Produção:** "Plantei 100kg de tomate, investindo R$500"
2. **Acompanhar Ciclo:** "Quando devo colher para maximizar lucro?"
3. **Analisar ROI:** "Qual produto me deu melhor retorno?"
4. **Planejar Futuro:** "Em que mês é melhor plantar?"

### Perguntas Respondidas:
- ✅ Qual mês mais produziu em relação ao investimento?
- ✅ Qual produto teve maior volume de vendas?
- ✅ Quando vale mais a pena produzir e vender?
- ✅ Qual a eficiência de cada produto?