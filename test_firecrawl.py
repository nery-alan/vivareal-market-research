#!/usr/bin/env python3
"""
Script de teste para validar integração Firecrawl
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

# Adicionar tools ao path
sys.path.insert(0, str(Path(__file__).parent / "tools"))

from firecrawl_integration import FirecrawlCrawler

def test_firecrawl():
    """Testa integração com Firecrawl."""

    print("🔥 Testando Integração Firecrawl\n")

    # Verificar API key
    api_key = os.getenv("FIRECRAWL_API_KEY")

    if not api_key:
        print("❌ FIRECRAWL_API_KEY não encontrada no .env")
        print("\n💡 Como configurar:")
        print("   1. Acesse: https://firecrawl.dev")
        print("   2. Obtenha sua API key")
        print("   3. Execute: echo 'FIRECRAWL_API_KEY=fc-sua-key' > .env")
        return False

    print(f"✅ API Key encontrada: {api_key[:10]}...")

    # Inicializar crawler
    print("\n📡 Inicializando Firecrawl Crawler...")
    crawler = FirecrawlCrawler(api_key=api_key)

    # Testar com URL simples
    test_url = "https://www.vivareal.com.br"
    print(f"\n🧪 Testando scrape de: {test_url}")

    result = crawler.scrape_url(test_url, formats=["markdown"])

    if result.get("success"):
        print("\n✅ Sucesso! Firecrawl está funcionando!")

        # Mostrar preview
        data = result.get("data", {})
        markdown = data.get("markdown", "")

        if markdown:
            preview = markdown[:200].replace("\n", " ")
            print(f"\n📄 Preview do conteúdo:")
            print(f"   {preview}...")

        print("\n🎉 Integração OK! Pronto para usar no workflow.")
        return True
    else:
        print(f"\n❌ Erro: {result.get('error')}")
        print("\n🔧 Troubleshooting:")
        print("   1. Verifique se a API key está correta")
        print("   2. Confirme que tem créditos no Firecrawl")
        print("   3. Tente gerar nova API key em: https://firecrawl.dev/app")
        return False

def test_vivareal_crawl():
    """Testa crawl real do VivaReal."""

    print("\n" + "="*60)
    print("🏢 Teste de Crawl Real - VivaReal")
    print("="*60 + "\n")

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("⚠️  Configure FIRECRAWL_API_KEY primeiro")
        return False

    crawler = FirecrawlCrawler(api_key=api_key)

    # Fazer crawl de 2 páginas para teste
    print("📍 Região: Freguesia do Ó")
    print("📏 Área: 40-45 m²")
    print("📄 Páginas: 2 (teste)")
    print()

    files = crawler.crawl_vivareal(
        region="freguesia-do-o",
        min_area=40,
        max_area=45,
        max_pages=2
    )

    if files:
        print(f"\n✅ Crawl concluído! {len(files)} páginas salvas")
        print("\n📂 Arquivos gerados:")
        for f in files:
            print(f"   - {f}")

        print("\n🔄 Próximos passos:")
        print("   1. python tools/parse_listings.py")
        print("   2. python tools/generate_report.py")

        return True
    else:
        print("\n❌ Nenhuma página foi salva")
        return False

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Testar Firecrawl")
    parser.add_argument(
        "--full-test",
        action="store_true",
        help="Fazer teste completo com crawl do VivaReal"
    )

    args = parser.parse_args()

    # Teste básico
    success = test_firecrawl()

    # Teste completo (opcional)
    if success and args.full_test:
        input("\n⏸️  Pressione ENTER para fazer crawl real do VivaReal...")
        test_vivareal_crawl()
    elif success:
        print("\n💡 Para fazer crawl real do VivaReal:")
        print("   python test_firecrawl.py --full-test")
