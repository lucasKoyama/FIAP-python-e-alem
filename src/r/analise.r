# ============================================================================
# SISTEMA DE GESTÃO DE PRODUÇÃO AGRÍCOLA - ANÁLISE QUANTITATIVA
# Análise de dados exportados do banco de dados Oracle
# ============================================================================

# Carregamento das bibliotecas necessárias
suppressPackageStartupMessages({
  if (!require(readr)) install.packages("readr", quiet = TRUE)
  if (!require(dplyr)) install.packages("dplyr", quiet = TRUE)
  if (!require(lubridate)) install.packages("lubridate", quiet = TRUE)
  if (!require(knitr)) install.packages("knitr", quiet = TRUE)
  
  library(readr)
  library(dplyr)
  library(lubridate)
  library(knitr)
})

# Função para encontrar o arquivo CSV mais recente
find_latest_csv <- function(pattern = "agricultural_data_") {
  data_dir <- "../data"
  
  if (!dir.exists(data_dir)) {
    cat("❌ Diretório data não encontrado. Execute o export_csv.py primeiro!\n")
    return(NULL)
  }
  
  files <- list.files(data_dir, pattern = paste0(pattern, ".*\\.csv"), full.names = TRUE)
  
  if (length(files) == 0) {
    cat("❌ Nenhum arquivo CSV encontrado. Execute o export_csv.py primeiro!\n")
    return(NULL)
  }
  
  # Retorna o arquivo mais recente
  latest_file <- files[which.max(file.mtime(files))]
  cat("✅ Usando arquivo:", basename(latest_file), "\n")
  return(latest_file)
}

# Carregamento dos dados
load_data <- function() {
  csv_file <- find_latest_csv()
  
  if (is.null(csv_file)) {
    return(NULL)
  }
  
  tryCatch({
    data <- read_csv(csv_file, show_col_types = FALSE)
    
    # Conversão de datas
    data$planting_date <- as.Date(data$planting_date, format = "%Y-%m-%d")
    data$harvest_date <- as.Date(data$harvest_date, format = "%Y-%m-%d")
    data$created_at <- as.Date(data$created_at, format = "%Y-%m-%d")
    
    cat("✅ Dados carregados com sucesso!\n")
    cat("📊 Total de registros:", nrow(data), "\n")
    cat("📅 Período dos dados:", 
        min(data$created_at, na.rm = TRUE), "até", 
        max(data$created_at, na.rm = TRUE), "\n\n")
    
    return(data)
  }, error = function(e) {
    cat("❌ Erro ao carregar dados:", e$message, "\n")
    return(NULL)
  })
}

# Função principal de análise
analyze_agricultural_data <- function() {
  cat("🌾 INICIANDO ANÁLISE QUANTITATIVA\n")
  cat("==================================\n\n")
  
  # Carrega os dados
  data <- load_data()
  if (is.null(data)) {
    return(NULL)
  }
  
  # 1. ANÁLISE GERAL DOS DADOS
  cat("1️⃣ ANÁLISE GERAL DOS DADOS\n")
  cat("-------------------------\n")
  
  cat("Produtos únicos:", length(unique(data$product_name)), "\n")
  cat("Status das produções:\n")
  status_counts <- table(data$production_status)
  print(status_counts)
  cat("\n")
  
  # 2. ANÁLISE FINANCEIRA GERAL
  cat("2️⃣ ANÁLISE FINANCEIRA GERAL\n")
  cat("---------------------------\n")
  
  total_investment <- sum(data$cost_price, na.rm = TRUE)
  total_revenue <- sum(data$sale_price, na.rm = TRUE)
  total_profit <- total_revenue - total_investment
  
  if (total_investment > 0) {
    overall_roi <- (total_profit / total_investment) * 100
  } else {
    overall_roi <- 0
  }
  
  cat("💰 Investimento total: R$", format(total_investment, big.mark = ".", decimal.mark = ",", nsmall = 2), "\n")
  cat("💵 Receita total: R$", format(total_revenue, big.mark = ".", decimal.mark = ",", nsmall = 2), "\n")
  cat("📈 Lucro total: R$", format(total_profit, big.mark = ".", decimal.mark = ",", nsmall = 2), "\n")
  cat("📊 ROI geral:", format(overall_roi, nsmall = 1), "%\n\n")
  
  # 3. ANÁLISE POR PRODUTO
  cat("3️⃣ ANÁLISE POR PRODUTO\n")
  cat("---------------------\n")
  
  product_analysis <- data %>%
    group_by(product_name) %>%
    summarise(
      quantidade_total = sum(quantity, na.rm = TRUE),
      investimento_total = sum(cost_price, na.rm = TRUE),
      receita_total = sum(sale_price, na.rm = TRUE),
      lucro_total = receita_total - investimento_total,
      roi_percent = ifelse(investimento_total > 0, 
                          (lucro_total / investimento_total) * 100, 0),
      eficiencia_producao = ifelse(investimento_total > 0,
                                  quantidade_total / investimento_total, 0),
      numero_producoes = n(),
      .groups = 'drop'
    ) %>%
    arrange(desc(roi_percent))
  
  cat("🥇 TOP 5 PRODUTOS POR ROI:\n")
  top_products <- head(product_analysis, 5)
  
  for (i in 1:min(nrow(top_products), 5)) {
    product <- top_products[i, ]
    cat(sprintf("%d. %s: ROI %.1f%% (Lucro: R$ %.2f)\n", 
                i, product$product_name, product$roi_percent, product$lucro_total))
  }
  cat("\n")
  
  # 4. ANÁLISE TEMPORAL (MENSAL)
  cat("4️⃣ ANÁLISE TEMPORAL\n")
  cat("------------------\n")
  
  # Análise por mês de colheita
  monthly_analysis <- data %>%
    filter(!is.na(harvest_date)) %>%
    mutate(
      year_month = format(harvest_date, "%Y-%m"),
      month_name = format(harvest_date, "%B %Y")
    ) %>%
    group_by(year_month, month_name) %>%
    summarise(
      quantidade_total = sum(quantity, na.rm = TRUE),
      investimento_total = sum(cost_price, na.rm = TRUE),
      receita_total = sum(sale_price, na.rm = TRUE),
      lucro_total = receita_total - investimento_total,
      roi_percent = ifelse(investimento_total > 0, 
                          (lucro_total / investimento_total) * 100, 0),
      producoes_count = n(),
      .groups = 'drop'
    ) %>%
    arrange(desc(roi_percent))
  
  if (nrow(monthly_analysis) > 0) {
    cat("🗓️ MELHORES MESES POR ROI:\n")
    top_months <- head(monthly_analysis, 3)
    
    for (i in 1:min(nrow(top_months), 3)) {
      month <- top_months[i, ]
      cat(sprintf("%d. %s: ROI %.1f%% (Lucro: R$ %.2f)\n", 
                  i, month$month_name, month$roi_percent, month$lucro_total))
    }
  } else {
    cat("❌ Não há dados suficientes para análise mensal\n")
  }
  cat("\n")
  
  # 5. ANÁLISE DE EFICIÊNCIA
  cat("5️⃣ ANÁLISE DE EFICIÊNCIA\n")
  cat("-----------------------\n")
  
  # Produtos com melhor eficiência (quantidade por real investido)
  efficiency_analysis <- product_analysis %>%
    filter(eficiencia_producao > 0) %>%
    arrange(desc(eficiencia_producao)) %>%
    head(5)
  
  if (nrow(efficiency_analysis) > 0) {
    cat("⚡ TOP PRODUTOS POR EFICIÊNCIA PRODUTIVA:\n")
    for (i in 1:nrow(efficiency_analysis)) {
      product <- efficiency_analysis[i, ]
      cat(sprintf("%d. %s: %.2f unidades/R$ investido\n", 
                  i, product$product_name, product$eficiencia_producao))
    }
  }
  cat("\n")
  
  # 6. ANÁLISE DE CICLO PRODUTIVO
  cat("6️⃣ ANÁLISE DE CICLO PRODUTIVO\n")
  cat("-----------------------------\n")
  
  cycle_data <- data %>%
    filter(!is.na(planting_date) & !is.na(harvest_date)) %>%
    mutate(
      cycle_days = as.numeric(harvest_date - planting_date)
    ) %>%
    filter(cycle_days > 0)
  
  if (nrow(cycle_data) > 0) {
    avg_cycle <- mean(cycle_data$cycle_days, na.rm = TRUE)
    min_cycle <- min(cycle_data$cycle_days, na.rm = TRUE)
    max_cycle <- max(cycle_data$cycle_days, na.rm = TRUE)
    
    cat("🕐 Ciclo médio de produção:", round(avg_cycle, 1), "dias\n")
    cat("⚡ Ciclo mais rápido:", min_cycle, "dias\n")
    cat("🐌 Ciclo mais longo:", max_cycle, "dias\n")
    
    # Análise de ciclo por produto
    cycle_by_product <- cycle_data %>%
      group_by(product_name) %>%
      summarise(
        ciclo_medio = mean(cycle_days, na.rm = TRUE),
        roi_medio = mean(roi_percent, na.rm = TRUE),
        .groups = 'drop'
      ) %>%
      arrange(ciclo_medio)
    
    cat("\n🏃‍♂️ PRODUTOS POR VELOCIDADE DE CICLO:\n")
    for (i in 1:min(nrow(cycle_by_product), 5)) {
      product <- cycle_by_product[i, ]
      cat(sprintf("%d. %s: %.0f dias (ROI médio: %.1f%%)\n", 
                  i, product$product_name, product$ciclo_medio, product$roi_medio))
    }
  } else {
    cat("❌ Não há dados suficientes de ciclo produtivo\n")
  }
  cat("\n")
  
  # 7. RECOMENDAÇÕES ESTRATÉGICAS
  cat("7️⃣ RECOMENDAÇÕES ESTRATÉGICAS\n")
  cat("============================\n")
  
  # Produto mais lucrativo
  if (nrow(product_analysis) > 0) {
    best_product <- product_analysis[1, ]
    cat("🌟 PRODUTO MAIS RENTÁVEL:", best_product$product_name, "\n")
    cat("   ROI:", format(best_product$roi_percent, nsmall = 1), "%\n")
    cat("   Lucro total: R$", format(best_product$lucro_total, big.mark = ".", decimal.mark = ",", nsmall = 2), "\n\n")
  }
  
  # Melhor mês para colheita
  if (nrow(monthly_analysis) > 0) {
    best_month <- monthly_analysis[1, ]
    cat("📅 MELHOR MÊS PARA COLHEITA:", best_month$month_name, "\n")
    cat("   ROI:", format(best_month$roi_percent, nsmall = 1), "%\n")
    cat("   Lucro: R$", format(best_month$lucro_total, big.mark = ".", decimal.mark = ",", nsmall = 2), "\n\n")
  }
  
  # Produto mais eficiente
  if (nrow(efficiency_analysis) > 0) {
    most_efficient <- efficiency_analysis[1, ]
    cat("⚡ PRODUTO MAIS EFICIENTE:", most_efficient$product_name, "\n")
    cat("   Eficiência:", format(most_efficient$eficiencia_producao, nsmall = 2), "unidades/R$\n\n")
  }
  
  # Retorna dados para uso posterior
  results <- list(
    data = data,
    product_analysis = product_analysis,
    monthly_analysis = monthly_analysis,
    efficiency_analysis = efficiency_analysis,
    cycle_data = cycle_data
  )
  
  cat("✅ ANÁLISE QUANTITATIVA CONCLUÍDA!\n")
  cat("📊 Dados salvos na memória para uso em gráficos\n\n")
  
  return(results)
}

# Função para salvar resultados em arquivo
save_analysis_results <- function(results) {
  if (is.null(results)) {
    return(FALSE)
  }
  
  tryCatch({
    # Cria diretório de resultados
    results_dir <- "../results"
    if (!dir.exists(results_dir)) {
      dir.create(results_dir, recursive = TRUE)
    }
    
    # Salva resumo em texto
    timestamp <- format(Sys.time(), "%Y%m%d_%H%M%S")
    txt_file <- file.path(results_dir, paste0("analise_quantitativa_", timestamp, ".txt"))
    
    # Redireciona output para arquivo
    sink(txt_file)
    analyze_agricultural_data()
    sink()
    
    cat("💾 Análise salva em:", txt_file, "\n")
    
    # Salva dados processados em CSV
    csv_file <- file.path(results_dir, paste0("produtos_analisados_", timestamp, ".csv"))
    write_csv(results$product_analysis, csv_file)
    cat("📊 Dados de produtos salvos em:", csv_file, "\n")
    
    if (!is.null(results$monthly_analysis) && nrow(results$monthly_analysis) > 0) {
      monthly_csv <- file.path(results_dir, paste0("analise_mensal_", timestamp, ".csv"))
      write_csv(results$monthly_analysis, monthly_csv)
      cat("📅 Análise mensal salva em:", monthly_csv, "\n")
    }
    
    return(TRUE)
  }, error = function(e) {
    cat("❌ Erro ao salvar resultados:", e$message, "\n")
    return(FALSE)
  })
}

# EXECUÇÃO PRINCIPAL
main <- function() {
  cat("🌾 SISTEMA DE ANÁLISE AGRÍCOLA - MÓDULO QUANTITATIVO\n")
  cat("====================================================\n\n")
  
  # Executa análise
  results <- analyze_agricultural_data()
  
  if (!is.null(results)) {
    # Salva resultados
    save_analysis_results(results)
    
    # Disponibiliza dados globalmente para uso em outros scripts
    assign("agricultural_results", results, envir = .GlobalEnv)
    
    cat("🎉 ANÁLISE CONCLUÍDA COM SUCESSO!\n")
    cat("📈 Execute graficos.R para gerar visualizações\n")
    cat("📋 Execute relatorio.Rmd para gerar relatório completo\n\n")
  } else {
    cat("❌ Análise não pôde ser concluída\n")
    cat("💡 Dica: Certifique-se de ter dados no banco e execute export_csv.py\n")
  }
}

# Executa se script for chamado diretamente
if (!interactive()) {
  main()
}
