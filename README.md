## 📊 Sistema de Gestão de Produção Agrícola e Análise

Este projeto tem como objetivo desenvolver um sistema completo de controle e análise da produção agrícola, permitindo que o produtor registre suas entradas e saídas de produção, acompanhe seus investimentos e visualize relatórios de desempenho.

A aplicação foi desenvolvida em Python, integrando coleta de dados, armazenamento em banco de dados e geração de relatórios automáticos para apoiar a tomada de decisão.

```
/src
  /python
    app.py               -> Interface de cadastro de dados
    db.py                -> Conexão e manipulação do banco de dados
    export_csv.py        -> Exporta dados
README.md
```

[video explicativo do projeto](https://youtu.be/6PdlNmKSkL0)

## ✅ Status do Projeto

- [x] **Modelagem do banco de dados** - Tabela `agricultural_production` com todos os campos necessários
- [x] **app.py** - Interface CLI completa com menu interativo para CRUD
- [x] **db.py** - Operações completas de banco de dados (Create, Read, Update, Delete)
- [x] **export_csv.py** - Exportação de dados para CSV com métricas calculadas
- [x] **setup.py** - Script de configuração e dados de exemplo

## 🚀 Como Executar o Projeto

### Pré-requisitos

1. **Python 3.8+** instalado
2. **Oracle Database** acessível (FIAP)
3. **Bibliotecas Python:**
   ```bash
   pip install oracledb
   ```

### Passo a Passo

#### 1. Configuração Inicial
```bash
# Execute o script de setup (cria diretórios e dados de exemplo)
python src/python/setup.py
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
- 📈 Gerar relatórios

#### 3. Análises e Relatórios

**Exportar dados do banco:**
```bash
python src/python/export_csv.py
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
- **RELATÓRIO VIA TERMINAL**

## 🎯 Casos de Uso

### Para o Agricultor:
1. **Registrar Produção:** "Plantei 100kg de tomate, investindo R$500"
3. **Analisar ROI:** "Qual produto me deu melhor retorno?"

### Perguntas Respondidas:
- ✅ Qual produto teve maior volume de vendas?
- ✅ Quando vale mais a pena produzir e vender?
- ✅ Qual a eficiência de cada produto?