#!/usr/bin/env python3
"""
Sistema de Gestão de Produção Agrícola
Interface CLI para cadastro e consulta de dados de produção
"""

import sys
from datetime import datetime
import db


def print_menu():
    """Exibe o menu principal do sistema"""
    print("\n" + "=" * 50)
    print("🌾 SISTEMA DE GESTÃO DE PRODUÇÃO AGRÍCOLA 🌾")
    print("=" * 50)
    print("1. 📝 Cadastrar nova produção")
    print("2. 📋 Listar todas as produções")
    print("3. 🔍 Buscar produção por ID")
    print("4. ✏️  Atualizar produção")
    print("5. 🗑️  Deletar produção")
    print("6. 📊 Exportar dados para CSV")
    print("7. 📈 Gerar relatórios (R)")
    print("0. 🚪 Sair")
    print("=" * 50)


def get_date_input(prompt):
    """Solicita entrada de data do usuário com validação"""
    while True:
        date_str = input(
            f"{prompt} (YYYY-MM-DD) ou pressione Enter para pular: "
        ).strip()
        if not date_str:
            return None
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("❌ Formato de data inválido! Use YYYY-MM-DD (ex: 2024-03-15)")


def get_float_input(prompt, allow_empty=False, min_value=0):
    """Solicita entrada de número decimal com validação"""
    while True:
        value_str = input(prompt).strip()
        if allow_empty and not value_str:
            return 0.0
        try:
            value = float(value_str)
            if value < min_value:
                print(f"❌ Valor deve ser maior ou igual a {min_value}")
                continue
            return value
        except ValueError:
            print("❌ Valor inválido! Digite um número válido.")


def cadastrar_producao():
    """Cadastra uma nova produção"""
    print("\n📝 CADASTRAR NOVA PRODUÇÃO")
    print("-" * 30)

    # Coleta dados básicos
    product_name = input("Nome do produto: ").strip()
    if not product_name:
        print("❌ Nome do produto é obrigatório!")
        return

    quantity = get_float_input("Quantidade produzida: ", min_value=0.01)
    cost_price = get_float_input("Custo de produção (R$): ", allow_empty=True)
    sale_price = get_float_input("Preço de venda (R$): ", allow_empty=True)

    # Coleta datas
    planting_date = get_date_input("Data de plantio")
    harvest_date = get_date_input("Data de colheita")

    # Status da produção
    print("\nStatus da produção:")
    print("1. PLANTED (Plantado)")
    print("2. HARVESTED (Colhido)")
    print("3. SOLD (Vendido)")

    while True:
        status_choice = input("Escolha o status (1-3): ").strip()
        status_map = {"1": "PLANTED", "2": "HARVESTED", "3": "SOLD"}
        if status_choice in status_map:
            production_status = status_map[status_choice]
            break
        print("❌ Opção inválida! Escolha 1, 2 ou 3.")

    # Confirma antes de salvar
    print(f"\n📋 CONFIRMAÇÃO DOS DADOS:")
    print(f"Produto: {product_name}")
    print(f"Quantidade: {quantity}")
    print(f"Custo: R$ {cost_price:.2f}")
    print(f"Preço de venda: R$ {sale_price:.2f}")
    print(f"Data de plantio: {planting_date or 'Não informado'}")
    print(f"Data de colheita: {harvest_date or 'Não informado'}")
    print(f"Status: {production_status}")

    confirm = input("\nConfirmar cadastro? (s/N): ").strip().lower()
    if confirm in ["s", "sim", "y", "yes"]:
        if db.create_agricultural_production(
            product_name=product_name,
            quantity=quantity,
            sale_price=sale_price,
            cost_price=cost_price,
            planting_date=planting_date,
            harvest_date=harvest_date,
            production_status=production_status,
        ):
            print("✅ Produção cadastrada com sucesso!")
        else:
            print("❌ Erro ao cadastrar produção!")
    else:
        print("❌ Cadastro cancelado.")


def listar_producoes():
    """Lista todas as produções cadastradas"""
    print("\n📋 TODAS AS PRODUÇÕES")
    print("-" * 50)

    productions = db.read_all_agricultural_production()

    if not productions:
        print("📭 Nenhuma produção encontrada.")
        return

    for prod in productions:
        print(f"\n🆔 ID: {prod['id']}")
        print(f"🌱 Produto: {prod['product_name']}")
        print(f"📦 Quantidade: {prod['quantity']}")
        print(f"💰 Custo: R$ {prod['cost_price']:.2f}")
        print(f"🏷️  Preço venda: R$ {prod['sale_price']:.2f}")

        if prod["sale_price"] > 0 and prod["cost_price"] > 0:
            profit = prod["sale_price"] - prod["cost_price"]
            roi = ((profit / prod["cost_price"]) * 100) if prod["cost_price"] > 0 else 0
            print(f"📈 Lucro: R$ {profit:.2f} (ROI: {roi:.1f}%)")

        print(f"📅 Plantio: {prod['planting_date'] or 'N/A'}")
        print(f"🌾 Colheita: {prod['harvest_date'] or 'N/A'}")
        print(f"📊 Status: {prod['production_status']}")
        print(f"🕐 Cadastrado: {prod['created_at']}")
        print("-" * 30)


def buscar_producao():
    """Busca uma produção por ID"""
    print("\n🔍 BUSCAR PRODUÇÃO")
    print("-" * 20)

    try:
        prod_id = int(input("Digite o ID da produção: "))
        production = db.read_agricultural_production_by_id(prod_id)

        if production:
            print(f"\n✅ Produção encontrada:")
            print(f"🆔 ID: {production['id']}")
            print(f"🌱 Produto: {production['product_name']}")
            print(f"📦 Quantidade: {production['quantity']}")
            print(f"💰 Custo: R$ {production['cost_price']:.2f}")
            print(f"🏷️  Preço venda: R$ {production['sale_price']:.2f}")
            print(f"📅 Plantio: {production['planting_date'] or 'N/A'}")
            print(f"🌾 Colheita: {production['harvest_date'] or 'N/A'}")
            print(f"📊 Status: {production['production_status']}")
        else:
            print("❌ Produção não encontrada!")

    except ValueError:
        print("❌ ID inválido! Digite um número.")


def atualizar_producao():
    """Atualiza uma produção existente"""
    print("\n✏️ ATUALIZAR PRODUÇÃO")
    print("-" * 25)

    try:
        prod_id = int(input("Digite o ID da produção para atualizar: "))

        # Primeiro verifica se existe
        existing = db.read_agricultural_production_by_id(prod_id)
        if not existing:
            print("❌ Produção não encontrada!")
            return

        print(f"\n📋 Dados atuais da produção ID {prod_id}:")
        print(f"Produto: {existing['product_name']}")
        print(f"Quantidade: {existing['quantity']}")
        print(f"Status: {existing['production_status']}")

        print("\n📝 Digite os novos dados (pressione Enter para manter o valor atual):")

        # Coleta novos dados
        new_name = input(f"Novo nome [{existing['product_name']}]: ").strip()
        product_name = new_name if new_name else existing["product_name"]

        quantity_input = input(f"Nova quantidade [{existing['quantity']}]: ").strip()
        quantity = float(quantity_input) if quantity_input else existing["quantity"]

        cost_input = input(f"Novo custo [{existing['cost_price']}]: ").strip()
        cost_price = float(cost_input) if cost_input else existing["cost_price"]

        sale_input = input(f"Novo preço [{existing['sale_price']}]: ").strip()
        sale_price = float(sale_input) if sale_input else existing["sale_price"]

        # Status
        print(f"\nStatus atual: {existing['production_status']}")
        print("1. PLANTED  2. HARVESTED  3. SOLD")
        status_input = input("Novo status (1-3) ou Enter para manter: ").strip()

        status_map = {"1": "PLANTED", "2": "HARVESTED", "3": "SOLD"}
        production_status = status_map.get(status_input, existing["production_status"])

        if db.update_agricultural_production(
            prod_id, product_name, quantity, sale_price, cost_price, production_status
        ):
            print("✅ Produção atualizada com sucesso!")
        else:
            print("❌ Erro ao atualizar produção!")

    except ValueError:
        print("❌ Valores inválidos!")


def deletar_producao():
    """Deleta uma produção"""
    print("\n🗑️ DELETAR PRODUÇÃO")
    print("-" * 20)

    try:
        prod_id = int(input("Digite o ID da produção para deletar: "))

        # Mostra os dados antes de deletar
        production = db.read_agricultural_production_by_id(prod_id)
        if not production:
            print("❌ Produção não encontrada!")
            return

        print(f"\n⚠️  Dados da produção a ser deletada:")
        print(f"ID: {production['id']}")
        print(f"Produto: {production['product_name']}")
        print(f"Quantidade: {production['quantity']}")

        confirm = input("\n❗ Tem certeza que deseja deletar? (s/N): ").strip().lower()
        if confirm in ["s", "sim", "y", "yes"]:
            if db.delete_agricultural_production(prod_id):
                print("✅ Produção deletada com sucesso!")
            else:
                print("❌ Erro ao deletar produção!")
        else:
            print("❌ Operação cancelada.")

    except ValueError:
        print("❌ ID inválido! Digite um número.")


def exportar_csv():
    """Exporta dados para CSV"""
    print("\n📊 EXPORTAR DADOS PARA CSV")
    print("-" * 30)

    try:
        import export_csv

        if export_csv.export_to_csv():
            print("✅ Dados exportados com sucesso!")
            print("📁 Arquivo salvo em: ../data/agricultural_data.csv")
        else:
            print("❌ Erro ao exportar dados!")
    except ImportError:
        print("❌ Módulo export_csv não encontrado!")
    except Exception as e:
        print(f"❌ Erro: {e}")


def gerar_relatorios():
    """Gera relatórios em R"""
    print("\n📈 GERAR RELATÓRIOS")
    print("-" * 20)

    import os
    import subprocess

    r_path = "../r"

    print("Opções de relatório:")
    print("1. 📊 Análise quantitativa")
    print("2. 📈 Gráficos e visualizações")
    print("3. 📋 Relatório completo (PDF)")

    choice = input("\nEscolha uma opção (1-3): ").strip()

    try:
        if choice == "1":
            print("🔄 Executando análise quantitativa...")
            subprocess.run(["Rscript", f"{r_path}/analise.r"], check=True)
            print("✅ Análise concluída!")

        elif choice == "2":
            print("🔄 Gerando gráficos...")
            subprocess.run(["Rscript", f"{r_path}/graficos.r"], check=True)
            print("✅ Gráficos gerados!")

        elif choice == "3":
            print("🔄 Gerando relatório completo...")
            subprocess.run(
                ["Rscript", "-e", f"rmarkdown::render('{r_path}/relatorio.Rmd')"],
                check=True,
            )
            print("✅ Relatório PDF gerado!")

        else:
            print("❌ Opção inválida!")

    except subprocess.CalledProcessError:
        print("❌ Erro ao executar script R. Verifique se o R está instalado.")
    except FileNotFoundError:
        print("❌ Comando R não encontrado. Instale o R e adicione ao PATH.")


def main():
    """Função principal do programa"""
    print("🌾 Iniciando Sistema de Gestão Agrícola...")

    # Testa conexão com banco
    connection = db.get_connection()
    if not connection:
        print("❌ Erro: Não foi possível conectar ao banco de dados!")
        print("Verifique as configurações em db.py")
        sys.exit(1)
    connection.close()
    print("✅ Conexão com banco de dados estabelecida!")

    while True:
        try:
            print_menu()
            choice = input("\nEscolha uma opção: ").strip()

            if choice == "1":
                cadastrar_producao()
            elif choice == "2":
                listar_producoes()
            elif choice == "3":
                buscar_producao()
            elif choice == "4":
                atualizar_producao()
            elif choice == "5":
                deletar_producao()
            elif choice == "6":
                exportar_csv()
            elif choice == "7":
                gerar_relatorios()
            elif choice == "0":
                print("\n👋 Obrigado por usar o Sistema de Gestão Agrícola!")
                print("🌱 Até a próxima!")
                break
            else:
                print("❌ Opção inválida! Escolha um número de 0 a 7.")

        except KeyboardInterrupt:
            print("\n\n👋 Sistema encerrado pelo usuário.")
            break
        except Exception as e:
            print(f"\n❌ Erro inesperado: {e}")
            print("Tente novamente ou entre em contato com o suporte.")


if __name__ == "__main__":
    main()
