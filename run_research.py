#!/usr/bin/env python3
"""
Agentic Workflow: Pesquisa de Mercado Imobiliário VivaReal
Orquestra o processo completo: Crawl → Parse → Report

Framework WAT (Workflows, Agents, Tools):
- Workflow: Definido em workflows/real_estate_research.md
- Agent: Este script (coordena execução)
- Tools: crawl_vivareal.py, parse_listings.py, generate_report.py
"""

import sys
from pathlib import Path

# Adicionar diretório tools ao path
sys.path.insert(0, str(Path(__file__).parent / "tools"))

from crawl_vivareal import VivaRealCrawler
from parse_listings import VivaRealParser
from generate_report import ReportGenerator

class MarketResearchAgent:
    """
    Agent: Orquestra o workflow de pesquisa de mercado.
    """

    def __init__(self, config: dict):
        self.config = config
        self.crawler = VivaRealCrawler(output_dir="data/raw")
        self.parser = VivaRealParser(input_dir="data/raw", output_dir="data/processed")
        self.reporter = ReportGenerator(
            input_file="data/processed/listings.json",
            output_dir="reports"
        )

    def run(self):
        """
        Executa workflow completo seguindo o processo definido.

        Fases:
        1. Coleta (Crawl)
        2. Extração (Parse)
        3. Análise (Report)
        """
        print("\n" + "="*60)
        print("🏢 PESQUISA DE MERCADO IMOBILIÁRIO - VIVAREAL")
        print("="*60)
        print(f"\n📍 Região: {self.config['region']}")
        print(f"📏 Área: {self.config['min_area']}-{self.config['max_area']} m²")
        print(f"🎯 Meta: {self.config['min_count']} anúncios")
        print("\n" + "="*60 + "\n")

        try:
            # FASE 1: COLETA
            print("\n┌─────────────────────────────────────────┐")
            print("│  FASE 1: COLETA DE DADOS (CRAWLING)    │")
            print("└─────────────────────────────────────────┘\n")

            crawled_files = self.crawler.crawl(
                region=self.config['region'],
                min_area=self.config['min_area'],
                max_area=self.config['max_area'],
                max_pages=self.config.get('max_pages', 10),
                delay=self.config.get('delay', 2)
            )

            if not crawled_files:
                raise Exception("❌ Nenhuma página foi coletada no crawl")

            # FASE 2: EXTRAÇÃO
            print("\n┌─────────────────────────────────────────┐")
            print("│  FASE 2: EXTRAÇÃO DE DADOS (PARSING)   │")
            print("└─────────────────────────────────────────┘\n")

            listings = self.parser.parse_all(
                min_area=self.config['min_area'],
                max_area=self.config['max_area']
            )

            if not listings:
                raise Exception("❌ Nenhum anúncio válido foi extraído")

            if len(listings) < self.config['min_count']:
                print(f"\n⚠️  AVISO: Apenas {len(listings)} anúncios encontrados")
                print(f"   Meta: {self.config['min_count']}")
                print(f"   Sugestão: Aumentar max_pages ou expandir filtros\n")

            # FASE 3: ANÁLISE E RELATÓRIO
            print("\n┌─────────────────────────────────────────┐")
            print("│  FASE 3: ANÁLISE E GERAÇÃO DE EXCEL    │")
            print("└─────────────────────────────────────────┘\n")

            excel_path = self.reporter.generate_report(
                min_count=self.config.get('min_count', 100)
            )

            # SUCESSO
            print("\n" + "="*60)
            print("✅ WORKFLOW CONCLUÍDO COM SUCESSO!")
            print("="*60)
            print(f"\n📊 Relatório gerado: {excel_path.absolute()}")
            print(f"📈 Total de anúncios: {len(listings)}")
            print("\n💡 Próximos passos:")
            print(f"   1. Abrir Excel: open {excel_path}")
            print(f"   2. Analisar dados e insights")
            print(f"   3. Refinar busca se necessário\n")

            return excel_path

        except Exception as e:
            print(f"\n❌ ERRO NO WORKFLOW: {e}")
            print("\n🔧 Troubleshooting:")
            print("   1. Verificar conexão com internet")
            print("   2. Checar se site está acessível")
            print("   3. Revisar logs acima para detalhes")
            print("   4. Ajustar parâmetros de busca\n")
            raise


def main():
    """CLI para execução do workflow."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Pesquisa de Mercado Imobiliário - VivaReal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Busca padrão (Freguesia do Ó, 40-45m²)
  python run_research.py

  # Busca customizada
  python run_research.py --region "vila-mariana" --min-area 50 --max-area 60

  # Mais páginas para coletar mais anúncios
  python run_research.py --max-pages 20

Framework WAT:
  Workflow: workflows/real_estate_research.md
  Tools: tools/*.py
  Agent: Este script
        """
    )

    parser.add_argument(
        "--region",
        default="freguesia-do-o",
        help="Região para busca (slug do VivaReal)"
    )
    parser.add_argument(
        "--min-area",
        type=int,
        default=40,
        help="Área mínima em m²"
    )
    parser.add_argument(
        "--max-area",
        type=int,
        default=45,
        help="Área máxima em m²"
    )
    parser.add_argument(
        "--min-count",
        type=int,
        default=100,
        help="Quantidade mínima de anúncios desejada"
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="Máximo de páginas para crawl"
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=2,
        help="Delay entre requests em segundos"
    )

    args = parser.parse_args()

    # Configuração do workflow
    config = {
        "region": args.region,
        "min_area": args.min_area,
        "max_area": args.max_area,
        "min_count": args.min_count,
        "max_pages": args.max_pages,
        "delay": args.delay
    }

    # Executar
    agent = MarketResearchAgent(config)

    try:
        agent.run()
        sys.exit(0)
    except Exception as e:
        print(f"\n💥 Falha na execução: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
