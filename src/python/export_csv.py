#!/usr/bin/env python3
"""
Módulo para exportar dados da produção agrícola para formato CSV
Para análise posterior em R
"""

import csv
import os
from datetime import datetime
from typing import List, Dict
import db


def ensure_data_directory():
    """Cria diretório data se não existir"""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        print(f"✅ Diretório criado: {data_dir}")
    return data_dir


def format_date_for_csv(date_obj):
    """Formata data para string no formato CSV"""
    if date_obj is None:
        return ""
    if isinstance(date_obj, str):
        return date_obj
    return date_obj.strftime("%Y-%m-%d")


def calculate_metrics(record: Dict) -> Dict:
    """Calcula métricas adicionais para cada registro"""
    metrics = {}

    # ROI (Return on Investment)
    if record["cost_price"] > 0 and record["sale_price"] > 0:
        profit = record["sale_price"] - record["cost_price"]
        roi = (profit / record["cost_price"]) * 100
        metrics["profit"] = round(profit, 2)
        metrics["roi_percent"] = round(roi, 2)
    else:
        metrics["profit"] = 0
        metrics["roi_percent"] = 0

    # Eficiência de produção (quantidade por real investido)
    if record["cost_price"] > 0:
        efficiency = record["quantity"] / record["cost_price"]
        metrics["production_efficiency"] = round(efficiency, 4)
    else:
        metrics["production_efficiency"] = 0

    # Revenue per unit
    if record["quantity"] > 0 and record["sale_price"] > 0:
        revenue_per_unit = record["sale_price"] / record["quantity"]
        metrics["revenue_per_unit"] = round(revenue_per_unit, 4)
    else:
        metrics["revenue_per_unit"] = 0

    # Cost per unit
    if record["quantity"] > 0 and record["cost_price"] > 0:
        cost_per_unit = record["cost_price"] / record["quantity"]
        metrics["cost_per_unit"] = round(cost_per_unit, 4)
    else:
        metrics["cost_per_unit"] = 0

    # Período de crescimento (dias entre plantio e colheita)
    if record.get("planting_date") and record.get("harvest_date"):
        try:
            if isinstance(record["planting_date"], str):
                planting = datetime.strptime(record["planting_date"], "%Y-%m-%d")
            else:
                planting = record["planting_date"]

            if isinstance(record["harvest_date"], str):
                harvest = datetime.strptime(record["harvest_date"], "%Y-%m-%d")
            else:
                harvest = record["harvest_date"]

            growth_days = (harvest - planting).days
            metrics["growth_period_days"] = growth_days
        except:
            metrics["growth_period_days"] = 0
    else:
        metrics["growth_period_days"] = 0

    return metrics


def export_to_csv(filename: str = None) -> bool:
    """
    Exporta todos os dados de produção agrícola para um arquivo CSV

    Args:
        filename: Nome do arquivo CSV (opcional)

    Returns:
        bool: True se exportação foi bem-sucedida, False caso contrário
    """
    try:
        # Busca todos os dados
        productions = db.read_all_agricultural_production()

        if not productions:
            print("❌ Nenhum dado encontrado para exportar!")
            return False

        # Cria diretório se necessário
        data_dir = ensure_data_directory()

        # Define nome do arquivo
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"agricultural_data_{timestamp}.csv"

        filepath = os.path.join(data_dir, filename)

        # Cabeçalhos do CSV
        headers = [
            "id",
            "product_name",
            "quantity",
            "sale_price",
            "cost_price",
            "planting_date",
            "harvest_date",
            "production_status",
            "created_at",
            "updated_at",
            # Métricas calculadas
            "profit",
            "roi_percent",
            "production_efficiency",
            "revenue_per_unit",
            "cost_per_unit",
            "growth_period_days",
        ]

        # Escreve dados no CSV
        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=headers)
            writer.writeheader()

            for record in productions:
                # Formata datas
                record["planting_date"] = format_date_for_csv(record["planting_date"])
                record["harvest_date"] = format_date_for_csv(record["harvest_date"])
                record["created_at"] = format_date_for_csv(record["created_at"])
                record["updated_at"] = format_date_for_csv(record["updated_at"])

                # Adiciona métricas calculadas
                metrics = calculate_metrics(record)
                record.update(metrics)

                writer.writerow(record)

        print(f"✅ Dados exportados com sucesso!")
        print(f"📁 Arquivo: {filepath}")
        print(f"📊 Total de registros: {len(productions)}")

        return True

    except Exception as e:
        print(f"❌ Erro ao exportar dados: {e}")
        return False


def export_summary_csv() -> bool:
    """
    Exporta um resumo dos dados por produto

    Returns:
        bool: True se exportação foi bem-sucedida
    """
    try:
        productions = db.read_all_agricultural_production()

        if not productions:
            print("❌ Nenhum dado encontrado para exportar!")
            return False

        data_dir = ensure_data_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"agricultural_summary_{timestamp}.csv"
        filepath = os.path.join(data_dir, filename)

        # Agrupa dados por produto
        product_summary = {}

        for record in productions:
            product = record["product_name"]

            if product not in product_summary:
                product_summary[product] = {
                    "product_name": product,
                    "total_quantity": 0,
                    "total_cost": 0,
                    "total_revenue": 0,
                    "count_planted": 0,
                    "count_harvested": 0,
                    "count_sold": 0,
                    "avg_growth_period": 0,
                    "total_growth_periods": 0,
                    "growth_period_count": 0,
                }

            summary = product_summary[product]
            summary["total_quantity"] += record["quantity"]
            summary["total_cost"] += record["cost_price"]
            summary["total_revenue"] += record["sale_price"]

            # Conta status
            status = record["production_status"]
            if status == "PLANTED":
                summary["count_planted"] += 1
            elif status == "HARVESTED":
                summary["count_harvested"] += 1
            elif status == "SOLD":
                summary["count_sold"] += 1

            # Calcula período de crescimento médio
            metrics = calculate_metrics(record)
            if metrics["growth_period_days"] > 0:
                summary["total_growth_periods"] += metrics["growth_period_days"]
                summary["growth_period_count"] += 1

        # Finaliza cálculos
        for product, summary in product_summary.items():
            if summary["growth_period_count"] > 0:
                summary["avg_growth_period"] = round(
                    summary["total_growth_periods"] / summary["growth_period_count"], 1
                )

            # Calcula métricas totais
            summary["total_profit"] = summary["total_revenue"] - summary["total_cost"]

            if summary["total_cost"] > 0:
                summary["total_roi_percent"] = round(
                    (summary["total_profit"] / summary["total_cost"]) * 100, 2
                )
            else:
                summary["total_roi_percent"] = 0

        # Headers para resumo
        summary_headers = [
            "product_name",
            "total_quantity",
            "total_cost",
            "total_revenue",
            "total_profit",
            "total_roi_percent",
            "count_planted",
            "count_harvested",
            "count_sold",
            "avg_growth_period",
        ]

        # Escreve resumo
        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=summary_headers)
            writer.writeheader()

            for summary in product_summary.values():
                # Remove campos auxiliares
                summary.pop("total_growth_periods", None)
                summary.pop("growth_period_count", None)
                writer.writerow(summary)

        print(f"✅ Resumo exportado com sucesso!")
        print(f"📁 Arquivo: {filepath}")
        print(f"📊 Produtos únicos: {len(product_summary)}")

        return True

    except Exception as e:
        print(f"❌ Erro ao exportar resumo: {e}")
        return False


def export_monthly_analysis() -> bool:
    """
    Exporta análise mensal dos dados

    Returns:
        bool: True se exportação foi bem-sucedida
    """
    try:
        productions = db.read_all_agricultural_production()

        if not productions:
            print("❌ Nenhum dados encontrado para exportar!")
            return False

        data_dir = ensure_data_directory()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"monthly_analysis_{timestamp}.csv"
        filepath = os.path.join(data_dir, filename)

        # Agrupa por mês de colheita
        monthly_data = {}

        for record in productions:
            harvest_date = record.get("harvest_date")
            if not harvest_date:
                continue

            # Extrai ano e mês
            if isinstance(harvest_date, str):
                if harvest_date:
                    try:
                        date_obj = datetime.strptime(harvest_date, "%Y-%m-%d")
                        month_key = date_obj.strftime("%Y-%m")
                    except:
                        continue
                else:
                    continue
            else:
                month_key = harvest_date.strftime("%Y-%m")

            if month_key not in monthly_data:
                monthly_data[month_key] = {
                    "year_month": month_key,
                    "total_quantity": 0,
                    "total_cost": 0,
                    "total_revenue": 0,
                    "production_count": 0,
                }

            monthly = monthly_data[month_key]
            monthly["total_quantity"] += record["quantity"]
            monthly["total_cost"] += record["cost_price"]
            monthly["total_revenue"] += record["sale_price"]
            monthly["production_count"] += 1

        # Calcula métricas mensais
        for month_key, monthly in monthly_data.items():
            monthly["total_profit"] = monthly["total_revenue"] - monthly["total_cost"]

            if monthly["total_cost"] > 0:
                monthly["roi_percent"] = round(
                    (monthly["total_profit"] / monthly["total_cost"]) * 100, 2
                )
                monthly["efficiency"] = round(
                    monthly["total_quantity"] / monthly["total_cost"], 4
                )
            else:
                monthly["roi_percent"] = 0
                monthly["efficiency"] = 0

            if monthly["production_count"] > 0:
                monthly["avg_quantity_per_production"] = round(
                    monthly["total_quantity"] / monthly["production_count"], 2
                )
            else:
                monthly["avg_quantity_per_production"] = 0

        # Headers mensais
        monthly_headers = [
            "year_month",
            "production_count",
            "total_quantity",
            "total_cost",
            "total_revenue",
            "total_profit",
            "roi_percent",
            "efficiency",
            "avg_quantity_per_production",
        ]

        # Escreve dados mensais
        with open(filepath, "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=monthly_headers)
            writer.writeheader()

            # Ordena por mês
            for month_key in sorted(monthly_data.keys()):
                writer.writerow(monthly_data[month_key])

        print(f"✅ Análise mensal exportada com sucesso!")
        print(f"📁 Arquivo: {filepath}")
        print(f"📊 Meses analisados: {len(monthly_data)}")

        return True

    except Exception as e:
        print(f"❌ Erro ao exportar análise mensal: {e}")
        return False


def main():
    """Função principal para testes"""
    print("🌾 SISTEMA DE EXPORTAÇÃO CSV")
    print("=" * 40)

    print("\n1. Exportando dados completos...")
    export_to_csv()

    print("\n2. Exportando resumo por produto...")
    export_summary_csv()

    print("\n3. Exportando análise mensal...")
    export_monthly_analysis()

    print("\n✅ Todas as exportações concluídas!")


if __name__ == "__main__":
    main()
