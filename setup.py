#!/usr/bin/env python3
"""
Script de configuração e teste do Sistema de Gestão Agrícola
Usado para criar dados de exemplo e testar o sistema
"""

import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "src", "python"))

import db
from datetime import datetime, timedelta
import random


def create_sample_data():
    """Cria dados de exemplo para testar o sistema"""
    print("🌱 CRIANDO DADOS DE EXEMPLO")
    print("=" * 40)

    # Lista de produtos agrícolas comuns
    products = [
        "Tomate",
        "Alface",
        "Cenoura",
        "Milho",
        "Feijão",
        "Batata",
        "Cebola",
        "Pimentão",
        "Abobrinha",
        "Brócolis",
    ]

    sample_data = []
    base_date = datetime(2024, 1, 15)

    for i, product in enumerate(products):
        # Gera múltiplas produções para cada produto
        for cycle in range(1, random.randint(2, 4)):
            planting_date = base_date + timedelta(days=i * 30 + cycle * 45)
            harvest_date = planting_date + timedelta(days=random.randint(60, 120))

            # Parâmetros baseados no produto
            base_quantity = random.uniform(100, 500)
            base_cost = random.uniform(50, 200)
            profit_margin = random.uniform(0.2, 0.8)  # 20% a 80% de lucro

            quantity = round(base_quantity * random.uniform(0.8, 1.2), 2)
            cost_price = round(base_cost * random.uniform(0.9, 1.1), 2)
            sale_price = round(cost_price * (1 + profit_margin), 2)

            # Status baseado na data
            days_since_harvest = (datetime.now() - harvest_date).days
            if days_since_harvest > 30:
                status = "SOLD"
            elif days_since_harvest > 0:
                status = "HARVESTED"
            else:
                status = "PLANTED"

            sample_data.append(
                {
                    "product_name": product,
                    "quantity": quantity,
                    "sale_price": sale_price if status == "SOLD" else 0,
                    "cost_price": cost_price,
                    "planting_date": planting_date.strftime("%Y-%m-%d"),
                    "harvest_date": (
                        harvest_date.strftime("%Y-%m-%d")
                        if status != "PLANTED"
                        else None
                    ),
                    "production_status": status,
                }
            )

    # Insere dados no banco
    success_count = 0
    for data in sample_data:
        if db.create_agricultural_production(**data):
            success_count += 1
        else:
            print(f"❌ Falha ao inserir: {data['product_name']}")

    print(f"✅ Dados criados: {success_count}/{len(sample_data)} registros")
    return success_count > 0


def test_database_connection():
    """Testa a conexão com o banco de dados"""
    print("🔌 TESTANDO CONEXÃO COM BANCO")
    print("=" * 35)

    connection = db.get_connection()
    if connection:
        print("✅ Conexão estabelecida com sucesso!")

        # Testa operações básicas
        try:
            cursor = connection.cursor()
            cursor.execute("SELECT COUNT(*) FROM agricultural_production")
            count = cursor.fetchone()[0]
            print(f"📊 Registros existentes: {count}")
            cursor.close()
            connection.close()
            return True
        except Exception as e:
            print(f"❌ Erro ao consultar dados: {e}")
            return False
    else:
        print("❌ Falha na conexão!")
        print("💡 Verifique as configurações em db.py")
        return False


def run_export_test():
    """Testa a exportação CSV"""
    print("\n📊 TESTANDO EXPORTAÇÃO CSV")
    print("=" * 30)

    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), "src", "python"))
        import export_csv

        if export_csv.export_to_csv("test_export.csv"):
            print("✅ Exportação CSV bem-sucedida!")
            return True
        else:
            print("❌ Falha na exportação CSV")
            return False
    except Exception as e:
        print(f"❌ Erro na exportação: {e}")
        return False


def setup_directories():
    """Cria diretórios necessários"""
    print("\n📁 CONFIGURANDO DIRETÓRIOS")
    print("=" * 30)

    directories = ["data", "plots", "results"]

    for dir_name in directories:
        dir_path = os.path.join(os.path.dirname(__file__), dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"✅ Criado: {dir_name}/")
        else:
            print(f"📁 Já existe: {dir_name}/")

    return True


def main():
    """Função principal do setup"""
    print("🌾 SETUP DO SISTEMA DE GESTÃO AGRÍCOLA")
    print("=" * 45)
    print()

    # 1. Configurar diretórios
    setup_directories()

    # 2. Testar conexão
    if not test_database_connection():
        print("\n❌ SETUP INTERROMPIDO - Problema na conexão com banco!")
        sys.exit(1)

    # 3. Verificar se há dados
    connection = db.get_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM agricultural_production")
    existing_records = cursor.fetchone()[0]
    cursor.close()
    connection.close()

    if existing_records == 0:
        print(f"\n💡 Banco de dados vazio ({existing_records} registros)")
        create_sample = input("Deseja criar dados de exemplo? (s/N): ").strip().lower()

        if create_sample in ["s", "sim", "y", "yes"]:
            if create_sample_data():
                print("\n✅ Dados de exemplo criados com sucesso!")
            else:
                print("\n❌ Falha ao criar dados de exemplo")
        else:
            print("\n⚠️ Continuando sem dados de exemplo")
    else:
        print(f"\n📊 Banco contém {existing_records} registros existentes")

    # 4. Testar exportação
    run_export_test()

    # 5. Instruções finais
    print("\n🎉 SETUP CONCLUÍDO!")
    print("=" * 20)
    print()
    print("📝 Como usar o sistema:")
    print("1. Execute 'python src/python/app.py' para interface CLI")
    print("2. Use a opção 6 no menu para exportar dados")
    print("3. Execute scripts R para análises:")
    print("   - Rscript src/r/analise.r")
    print("   - Rscript src/r/graficos.r")
    print("4. Gere relatório: Rscript -e \"rmarkdown::render('src/r/relatorio.Rmd')\"")
    print()
    print("📚 Estrutura do projeto:")
    print("├── src/python/     → Scripts Python (app.py, db.py, export_csv.py)")
    print("├── src/r/          → Scripts R (analise.r, graficos.r, relatorio.Rmd)")
    print("├── data/           → Arquivos CSV exportados")
    print("├── plots/          → Gráficos gerados")
    print("└── results/        → Relatórios e análises")
    print()
    print("🚀 Sistema pronto para uso!")


if __name__ == "__main__":
    main()
