# ============================================================================
# SISTEMA DE GESTÃO DE PRODUÇÃO AGRÍCOLA - GRÁFICOS E VISUALIZAÇÕES
# Geração de gráficos baseados na análise quantitativa
# ============================================================================

# Carregamento das bibliotecas necessárias
suppressPackageStartupMessages({
  if (!require(ggplot2)) install.packages("ggplot2", quiet = TRUE)
  if (!require(dplyr)) install.packages("dplyr", quiet = TRUE)
  if (!require(readr)) install.packages("readr", quiet = TRUE)
  if (!require(lubridate)) install.packages("lubridate", quiet = TRUE)
  if (!require(scales)) install.packages("scales", quiet = TRUE)
  if (!require(gridExtra)) install.packages("gridExtra", quiet = TRUE)
  if (!require(RColorBrewer)) install.packages("RColorBrewer", quiet = TRUE)
  
  library(ggplot2)
  library(dplyr)
  library(readr)
  library(lubridate)
  library(scales)
  library(gridExtra)
  library(RColorBrewer)
})

# Função para configurar tema dos gráficos
setup_theme <- function() {
  theme_minimal() +
    theme(
      plot.title = element_text(size = 14, face = "bold", hjust = 0.5),
      plot.subtitle = element_text(size = 12, hjust = 0.5),
      axis.text = element_text(size = 10),
      axis.title = element_text(size = 11, face = "bold"),
      legend.title = element_text(size = 11, face = "bold"),
      legend.text = element_text(size = 10),
      panel.grid.minor = element_blank(),
      strip.text = element_text(size = 11, face = "bold")
    )
}

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
    
    cat("✅ Dados carregados:", nrow(data), "registros\n\n")
    return(data)
  }, error = function(e) {
    cat("❌ Erro ao carregar dados:", e$message, "\n")
    return(NULL)
  })
}

# 1. Gráfico de ROI por Produto
create_roi_chart <- function(data) {
  product_roi <- data %>%
    filter(cost_price > 0, sale_price > 0) %>%
    group_by(product_name) %>%
    summarise(
      roi_medio = mean(roi_percent, na.rm = TRUE),
      lucro_total = sum(profit, na.rm = TRUE),
      investimento_total = sum(cost_price, na.rm = TRUE),
      .groups = 'drop'
    ) %>%
    arrange(desc(roi_medio)) %>%
    head(10)  # Top 10 produtos
  
  if (nrow(product_roi) == 0) {
    return(NULL)
  }
  
  ggplot(product_roi, aes(x = reorder(product_name, roi_medio), y = roi_medio)) +
    geom_col(fill = "#2E8B57", alpha = 0.8) +
    geom_text(aes(label = paste0(round(roi_medio, 1), "%")), 
              hjust = -0.1, size = 3.5, fontface = "bold") +
    coord_flip() +
    labs(
      title = "📈 ROI por Produto",
      subtitle = "Retorno sobre Investimento (%)",
      x = "Produto",
      y = "ROI (%)"
    ) +
    setup_theme() +
    scale_y_continuous(labels = percent_format(scale = 1))
}

# 2. Gráfico de Evolução Temporal das Vendas
create_temporal_chart <- function(data) {
  temporal_data <- data %>%
    filter(!is.na(harvest_date), sale_price > 0) %>%
    mutate(
      year_month = floor_date(harvest_date, "month")
    ) %>%
    group_by(year_month) %>%
    summarise(
      receita_mensal = sum(sale_price, na.rm = TRUE),
      custo_mensal = sum(cost_price, na.rm = TRUE),
      lucro_mensal = receita_mensal - custo_mensal,
      quantidade_mensal = sum(quantity, na.rm = TRUE),
      .groups = 'drop'
    ) %>%
    arrange(year_month)
  
  if (nrow(temporal_data) == 0) {
    return(NULL)
  }
  
  # Gráfico de linha para receita e custo
  p1 <- ggplot(temporal_data, aes(x = year_month)) +
    geom_line(aes(y = receita_mensal, color = "Receita"), size = 1.2) +
    geom_line(aes(y = custo_mensal, color = "Custo"), size = 1.2) +
    geom_point(aes(y = receita_mensal, color = "Receita"), size = 2) +
    geom_point(aes(y = custo_mensal, color = "Custo"), size = 2) +
    labs(
      title = "💰 Evolução de Receita e Custo",
      subtitle = "Valores mensais em R$",
      x = "Mês",
      y = "Valor (R$)",
      color = "Tipo"
    ) +
    setup_theme() +
    scale_color_manual(values = c("Receita" = "#2E8B57", "Custo" = "#DC143C")) +
    scale_y_continuous(labels = label_number(prefix = "R$ ", big.mark = ".")) +
    scale_x_date(date_labels = "%b %Y", date_breaks = "1 month") +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
  
  return(p1)
}

# 3. Gráfico de Eficiência de Produção
create_efficiency_chart <- function(data) {
  efficiency_data <- data %>%
    filter(cost_price > 0) %>%
    group_by(product_name) %>%
    summarise(
      eficiencia_media = mean(production_efficiency, na.rm = TRUE),
      quantidade_total = sum(quantity, na.rm = TRUE),
      investimento_total = sum(cost_price, na.rm = TRUE),
      .groups = 'drop'
    ) %>%
    arrange(desc(eficiencia_media)) %>%
    head(8)
  
  if (nrow(efficiency_data) == 0) {
    return(NULL)
  }
  
  ggplot(efficiency_data, aes(x = reorder(product_name, eficiencia_media), 
                             y = eficiencia_media)) +
    geom_col(fill = "#4682B4", alpha = 0.8) +
    geom_text(aes(label = round(eficiencia_media, 2)), 
              hjust = -0.1, size = 3.5, fontface = "bold") +
    coord_flip() +
    labs(
      title = "⚡ Eficiência de Produção",
      subtitle = "Quantidade produzida por R$ investido",
      x = "Produto",
      y = "Eficiência (unidades/R$)"
    ) +
    setup_theme()
}

# 4. Gráfico de Status de Produção
create_status_chart <- function(data) {
  status_data <- data %>%
    count(production_status) %>%
    mutate(
      percentage = n / sum(n) * 100,
      status_label = case_when(
        production_status == "PLANTED" ~ "🌱 Plantado",
        production_status == "HARVESTED" ~ "🌾 Colhido",
        production_status == "SOLD" ~ "💰 Vendido",
        TRUE ~ production_status
      )
    )
  
  if (nrow(status_data) == 0) {
    return(NULL)
  }
  
  colors <- c("#90EE90", "#FFD700", "#32CD32")
  
  ggplot(status_data, aes(x = "", y = percentage, fill = status_label)) +
    geom_col(width = 1) +
    coord_polar("y", start = 0) +
    geom_text(aes(label = paste0(round(percentage, 1), "%\n(", n, ")")), 
              position = position_stack(vjust = 0.5), 
              size = 4, fontface = "bold") +
    labs(
      title = "📊 Status das Produções",
      subtitle = "Distribuição por fase do ciclo",
      fill = "Status"
    ) +
    setup_theme() +
    scale_fill_manual(values = colors) +
    theme(
      axis.text = element_blank(),
      axis.title = element_blank(),
      panel.grid = element_blank()
    )
}

# 5. Gráfico de Correlação Investimento x Retorno
create_correlation_chart <- function(data) {
  correlation_data <- data %>%
    filter(cost_price > 0, sale_price > 0) %>%
    select(product_name, cost_price, sale_price, profit, quantity)
  
  if (nrow(correlation_data) == 0) {
    return(NULL)
  }
  
  ggplot(correlation_data, aes(x = cost_price, y = sale_price)) +
    geom_point(aes(size = quantity, color = product_name), alpha = 0.7) +
    geom_smooth(method = "lm", se = TRUE, color = "#DC143C", linetype = "dashed") +
    labs(
      title = "🎯 Correlação: Investimento x Retorno",
      subtitle = "Tamanho do ponto = quantidade produzida",
      x = "Custo de Produção (R$)",
      y = "Preço de Venda (R$)",
      color = "Produto",
      size = "Quantidade"
    ) +
    setup_theme() +
    scale_x_continuous(labels = label_number(prefix = "R$ ", big.mark = ".")) +
    scale_y_continuous(labels = label_number(prefix = "R$ ", big.mark = ".")) +
    guides(color = guide_legend(override.aes = list(size = 3)))
}

# 6. Gráfico de Ciclo de Produção
create_cycle_chart <- function(data) {
  cycle_data <- data %>%
    filter(!is.na(planting_date), !is.na(harvest_date)) %>%
    mutate(
      cycle_days = as.numeric(harvest_date - planting_date)
    ) %>%
    filter(cycle_days > 0) %>%
    group_by(product_name) %>%
    summarise(
      ciclo_medio = mean(cycle_days, na.rm = TRUE),
      roi_medio = mean(roi_percent, na.rm = TRUE),
      .groups = 'drop'
    ) %>%
    arrange(ciclo_medio)
  
  if (nrow(cycle_data) == 0) {
    return(NULL)
  }
  
  ggplot(cycle_data, aes(x = ciclo_medio, y = roi_medio)) +
    geom_point(aes(color = product_name), size = 4, alpha = 0.8) +
    geom_text(aes(label = product_name), 
              vjust = -1, hjust = 0.5, size = 3, fontface = "bold") +
    labs(
      title = "🕐 Ciclo de Produção x ROI",
      subtitle = "Tempo de cultivo versus retorno financeiro",
      x = "Ciclo Médio (dias)",
      y = "ROI Médio (%)"
    ) +
    setup_theme() +
    scale_y_continuous(labels = percent_format(scale = 1)) +
    theme(legend.position = "none")
}

# 7. Gráfico de Top Produtos por Lucro
create_profit_chart <- function(data) {
  profit_data <- data %>%
    filter(profit > 0) %>%
    group_by(product_name) %>%
    summarise(
      lucro_total = sum(profit, na.rm = TRUE),
      lucro_medio = mean(profit, na.rm = TRUE),
      quantidade_vendas = n(),
      .groups = 'drop'
    ) %>%
    arrange(desc(lucro_total)) %>%
    head(8)
  
  if (nrow(profit_data) == 0) {
    return(NULL)
  }
  
  ggplot(profit_data, aes(x = reorder(product_name, lucro_total), 
                         y = lucro_total)) +
    geom_col(fill = "#FF6347", alpha = 0.8) +
    geom_text(aes(label = paste0("R$ ", format(lucro_total, big.mark = ".", nsmall = 0))), 
              hjust = -0.1, size = 3.5, fontface = "bold") +
    coord_flip() +
    labs(
      title = "💎 Top Produtos por Lucro Total",
      subtitle = "Soma de todos os lucros por produto",
      x = "Produto",
      y = "Lucro Total (R$)"
    ) +
    setup_theme() +
    scale_y_continuous(labels = label_number(prefix = "R$ ", big.mark = "."))
}

# Função principal para gerar todos os gráficos
generate_all_charts <- function() {
  cat("📈 INICIANDO GERAÇÃO DE GRÁFICOS\n")
  cat("===============================\n\n")
  
  # Carrega dados
  data <- load_data()
  if (is.null(data)) {
    cat("❌ Não foi possível carregar os dados!\n")
    return(FALSE)
  }
  
  # Cria diretório para gráficos
  plots_dir <- "../plots"
  if (!dir.exists(plots_dir)) {
    dir.create(plots_dir, recursive = TRUE)
    cat("📁 Diretório criado:", plots_dir, "\n")
  }
  
  timestamp <- format(Sys.time(), "%Y%m%d_%H%M%S")
  
  # Lista de gráficos para gerar
  charts <- list(
    list(func = create_roi_chart, name = "roi_por_produto", title = "ROI por Produto"),
    list(func = create_temporal_chart, name = "evolucao_temporal", title = "Evolução Temporal"),
    list(func = create_efficiency_chart, name = "eficiencia_producao", title = "Eficiência de Produção"),
    list(func = create_status_chart, name = "status_producao", title = "Status das Produções"),
    list(func = create_correlation_chart, name = "correlacao_investimento", title = "Correlação Investimento x Retorno"),
    list(func = create_cycle_chart, name = "ciclo_producao", title = "Ciclo de Produção"),
    list(func = create_profit_chart, name = "lucro_por_produto", title = "Lucro por Produto")
  )
  
  # Gera cada gráfico
  generated_charts <- list()
  
  for (chart_info in charts) {
    cat("📊 Gerando:", chart_info$title, "...")
    
    tryCatch({
      chart <- chart_info$func(data)
      
      if (!is.null(chart)) {
        filename <- file.path(plots_dir, paste0(chart_info$name, "_", timestamp, ".png"))
        
        ggsave(filename, chart, width = 12, height = 8, dpi = 300, bg = "white")
        
        generated_charts[[chart_info$name]] <- chart
        cat(" ✅\n")
      } else {
        cat(" ❌ (dados insuficientes)\n")
      }
    }, error = function(e) {
      cat(" ❌ Erro:", e$message, "\n")
    })
  }
  
  # Cria dashboard combinado
  if (length(generated_charts) >= 4) {
    cat("\n📋 Gerando dashboard combinado...")
    
    tryCatch({
      # Seleciona 4 gráficos principais para o dashboard
      main_charts <- generated_charts[c("roi_por_produto", "evolucao_temporal", 
                                       "eficiencia_producao", "status_producao")]
      main_charts <- main_charts[!sapply(main_charts, is.null)]
      
      if (length(main_charts) >= 2) {
        dashboard <- do.call(grid.arrange, c(main_charts, ncol = 2))
        
        dashboard_file <- file.path(plots_dir, paste0("dashboard_", timestamp, ".png"))
        ggsave(dashboard_file, dashboard, width = 16, height = 12, dpi = 300, bg = "white")
        
        cat(" ✅\n")
        cat("📊 Dashboard salvo em:", basename(dashboard_file), "\n")
      }
    }, error = function(e) {
      cat(" ❌ Erro no dashboard:", e$message, "\n")
    })
  }
  
  cat("\n✅ GERAÇÃO DE GRÁFICOS CONCLUÍDA!\n")
  cat("📁 Gráficos salvos em:", plots_dir, "\n")
  cat("📈 Total de gráficos gerados:", length(generated_charts), "\n\n")
  
  return(TRUE)
}

# Função para exibir gráficos no R
display_charts <- function() {
  data <- load_data()
  if (is.null(data)) {
    return(FALSE)
  }
  
  cat("🖥️ EXIBINDO GRÁFICOS NA TELA\n")
  cat("============================\n\n")
  
  # Exibe gráficos um por um
  charts <- list(
    create_roi_chart(data),
    create_temporal_chart(data),
    create_efficiency_chart(data),
    create_status_chart(data)
  )
  
  for (i in seq_along(charts)) {
    if (!is.null(charts[[i]])) {
      print(charts[[i]])
      if (i < length(charts)) {
        readline(prompt = "Pressione Enter para o próximo gráfico...")
      }
    }
  }
  
  return(TRUE)
}

# EXECUÇÃO PRINCIPAL
main <- function() {
  cat("🌾 SISTEMA DE GRÁFICOS AGRÍCOLAS\n")
  cat("================================\n\n")
  
  # Gera e salva todos os gráficos
  success <- generate_all_charts()
  
  if (success) {
    cat("🎉 VISUALIZAÇÕES CRIADAS COM SUCESSO!\n")
    cat("💡 Dica: Abra os arquivos PNG para ver os gráficos\n")
    cat("📋 Execute relatorio.Rmd para relatório completo com gráficos integrados\n\n")
  } else {
    cat("❌ Falha na geração dos gráficos\n")
    cat("💡 Certifique-se de ter dados exportados do banco\n")
  }
}

# Executa se script for chamado diretamente
if (!interactive()) {
  main()
}
