#!/usr/bin/env python3
"""
Tool: Firecrawl Integration
Wrapper para usar Firecrawl API ou MCP para crawling robusto.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Optional
import requests

class FirecrawlCrawler:
    """
    Integração com Firecrawl para bypass de proteções anti-bot.

    Suporta:
    1. Firecrawl API (via API key)
    2. MCP Server (quando disponível)
    3. Fallback para requests simples (limitado)
    """

    def __init__(self, api_key: Optional[str] = None, output_dir: str = "data/raw"):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.base_url = "https://api.firecrawl.dev/v1"

    def scrape_url(self, url: str, formats: List[str] = ["markdown", "html"]) -> Dict:
        """
        Scrape uma URL usando Firecrawl API.

        Args:
            url: URL para scrape
            formats: Formatos desejados (markdown, html, links, etc.)

        Returns:
            Dict com success, data, metadata
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "Firecrawl API key not configured. Set FIRECRAWL_API_KEY env var."
            }

        print(f"🔥 Firecrawl scraping: {url}")

        try:
            response = requests.post(
                f"{self.base_url}/scrape",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "url": url,
                    "formats": formats,
                    "onlyMainContent": False  # Queremos tudo, incluindo sidebar com anúncios
                },
                timeout=60
            )

            response.raise_for_status()
            data = response.json()

            if data.get("success"):
                print(f"   ✅ Scrape concluído")
                return {
                    "success": True,
                    "data": data.get("data", {}),
                    "url": url
                }
            else:
                return {
                    "success": False,
                    "error": data.get("error", "Unknown error"),
                    "url": url
                }

        except requests.RequestException as e:
            print(f"   ❌ Erro: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url
            }

    def crawl_vivareal(self,
                       region: str,
                       min_area: int,
                       max_area: int,
                       max_pages: int = 10) -> List[Path]:
        """
        Crawl VivaReal usando Firecrawl.

        Args:
            region: Região (slug do VivaReal)
            min_area: Área mínima
            max_area: Área máxima
            max_pages: Número de páginas

        Returns:
            Lista de arquivos salvos
        """
        print(f"\n🔥 Firecrawl Crawl - VivaReal")
        print(f"   Região: {region}")
        print(f"   Área: {min_area}-{max_area} m²\n")

        # Construir URL base (mesmo formato do crawler original)
        base_url = (
            f"https://www.vivareal.com.br/venda/sp/sao-paulo/zona-norte/{region}/"
            f"apartamento_residencial/?tipos=apartamento&areaUtil={min_area}-{max_area}"
        )

        saved_files = []

        for page_num in range(1, max_pages + 1):
            # Construir URL da página
            if page_num == 1:
                page_url = base_url
            else:
                page_url = f"{base_url}&pagina={page_num}"

            # Scrape usando Firecrawl
            result = self.scrape_url(page_url, formats=["html", "markdown"])

            if not result.get("success"):
                print(f"⚠️  Falhou na página {page_num}: {result.get('error')}")
                if page_num == 1:
                    # Se primeira página falhar, abortar
                    break
                continue

            # Salvar HTML
            data = result.get("data", {})
            html_content = data.get("html", "")
            markdown_content = data.get("markdown", "")

            if html_content:
                html_file = self.output_dir / f"page_{page_num:03d}.html"
                with open(html_file, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"💾 Saved HTML: {html_file}")
                saved_files.append(html_file)

            if markdown_content:
                md_file = self.output_dir / f"page_{page_num:03d}.md"
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(markdown_content)
                print(f"💾 Saved Markdown: {md_file}")

        print(f"\n✅ Firecrawl concluído! {len(saved_files)} páginas salvas")

        # Salvar metadata
        metadata = {
            "engine": "firecrawl",
            "region": region,
            "min_area": min_area,
            "max_area": max_area,
            "pages_crawled": len(saved_files),
            "files": [str(f) for f in saved_files]
        }

        metadata_path = self.output_dir / "crawl_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        return saved_files


def main():
    """CLI para testar Firecrawl."""
    import argparse

    parser = argparse.ArgumentParser(description="Firecrawl VivaReal Integration")
    parser.add_argument("--api-key", help="Firecrawl API key (ou use FIRECRAWL_API_KEY env)")
    parser.add_argument("--region", default="freguesia-do-o", help="Região")
    parser.add_argument("--min-area", type=int, default=40)
    parser.add_argument("--max-area", type=int, default=45)
    parser.add_argument("--max-pages", type=int, default=10)
    parser.add_argument("--test-url", help="Testar scrape de uma URL específica")

    args = parser.parse_args()

    crawler = FirecrawlCrawler(api_key=args.api_key)

    if args.test_url:
        # Modo de teste
        print(f"🧪 Testando Firecrawl com URL: {args.test_url}\n")
        result = crawler.scrape_url(args.test_url)

        if result.get("success"):
            print("\n✅ Sucesso!")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\n❌ Falha: {result.get('error')}")
    else:
        # Modo de crawl completo
        crawler.crawl_vivareal(
            region=args.region,
            min_area=args.min_area,
            max_area=args.max_area,
            max_pages=args.max_pages
        )


if __name__ == "__main__":
    main()
