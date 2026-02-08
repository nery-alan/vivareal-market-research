#!/usr/bin/env python3
"""
Tool: VivaReal Crawler
Coleta anúncios de apartamentos do VivaReal com filtros específicos.
"""

import requests
import time
import json
from pathlib import Path
from typing import List, Dict
from urllib.parse import urlencode

class VivaRealCrawler:
    def __init__(self, output_dir: str = "data/raw"):
        self.base_url = "https://www.vivareal.com.br"
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        })

    def build_search_url(self,
                         region: str,
                         min_area: int,
                         max_area: int,
                         transaction: str = "venda",
                         property_type: str = "apartamento") -> str:
        """
        Constrói URL de busca do VivaReal.

        Exemplo: /venda/sp/sao-paulo/zona-norte/freguesia-do-o/apartamento_residencial/
                 ?tipos=apartamento&areaUtil=40-45
        """
        # Normalizar região para slug
        region_slug = region.lower().replace(" ", "-")

        # Construir path
        path_parts = [
            transaction,
            "sp",
            "sao-paulo",
            "zona-norte",
            region_slug,
            f"{property_type}_residencial"
        ]

        path = "/" + "/".join(path_parts) + "/"

        # Parâmetros de query
        params = {
            "tipos": property_type,
            "areaUtil": f"{min_area}-{max_area}"
        }

        return self.base_url + path + "?" + urlencode(params)

    def fetch_page(self, url: str, page_num: int = 1) -> Dict:
        """
        Busca uma página de resultados.
        Retorna dict com status, content e metadata.
        """
        try:
            # Adicionar parâmetro de página se necessário
            page_url = url
            if page_num > 1:
                separator = "&" if "?" in url else "?"
                page_url = f"{url}{separator}pagina={page_num}"

            print(f"📡 Fetching: {page_url}")
            response = self.session.get(page_url, timeout=30)
            response.raise_for_status()

            return {
                "success": True,
                "status_code": response.status_code,
                "content": response.text,
                "url": page_url,
                "page_num": page_num
            }

        except requests.RequestException as e:
            print(f"❌ Erro ao buscar página {page_num}: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": page_url,
                "page_num": page_num
            }

    def save_page(self, page_data: Dict) -> Path:
        """Salva conteúdo HTML da página."""
        if not page_data.get("success"):
            return None

        filename = f"page_{page_data['page_num']:03d}.html"
        filepath = self.output_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(page_data['content'])

        print(f"💾 Saved: {filepath}")
        return filepath

    def crawl(self,
              region: str,
              min_area: int,
              max_area: int,
              max_pages: int = 10,
              delay: int = 2) -> List[Path]:
        """
        Executa crawl completo.

        Args:
            region: Nome da região (ex: "freguesia-do-o")
            min_area: Área mínima em m²
            max_area: Área máxima em m²
            max_pages: Número máximo de páginas para crawl
            delay: Delay entre requests (segundos)

        Returns:
            Lista de caminhos dos arquivos salvos
        """
        print(f"\n🚀 Iniciando crawl VivaReal")
        print(f"   Região: {region}")
        print(f"   Área: {min_area}-{max_area} m²")
        print(f"   Páginas máximas: {max_pages}\n")

        # Construir URL base
        base_url = self.build_search_url(region, min_area, max_area)

        saved_files = []

        for page_num in range(1, max_pages + 1):
            # Fetch página
            page_data = self.fetch_page(base_url, page_num)

            if not page_data.get("success"):
                print(f"⚠️  Parando crawl na página {page_num}")
                break

            # Salvar
            filepath = self.save_page(page_data)
            if filepath:
                saved_files.append(filepath)

            # Delay para não sobrecarregar servidor
            if page_num < max_pages:
                time.sleep(delay)

        print(f"\n✅ Crawl concluído! {len(saved_files)} páginas salvas")

        # Salvar metadata
        metadata = {
            "region": region,
            "min_area": min_area,
            "max_area": max_area,
            "pages_crawled": len(saved_files),
            "base_url": base_url,
            "files": [str(f) for f in saved_files]
        }

        metadata_path = self.output_dir / "crawl_metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        print(f"📋 Metadata: {metadata_path}")

        return saved_files


def main():
    """CLI para execução standalone."""
    import argparse

    parser = argparse.ArgumentParser(description="Crawl VivaReal listings")
    parser.add_argument("--region", default="freguesia-do-o", help="Região para busca")
    parser.add_argument("--min-area", type=int, default=40, help="Área mínima (m²)")
    parser.add_argument("--max-area", type=int, default=45, help="Área máxima (m²)")
    parser.add_argument("--max-pages", type=int, default=10, help="Máximo de páginas")
    parser.add_argument("--delay", type=int, default=2, help="Delay entre requests (s)")
    parser.add_argument("--output", default="data/raw", help="Diretório de saída")

    args = parser.parse_args()

    crawler = VivaRealCrawler(output_dir=args.output)
    crawler.crawl(
        region=args.region,
        min_area=args.min_area,
        max_area=args.max_area,
        max_pages=args.max_pages,
        delay=args.delay
    )


if __name__ == "__main__":
    main()
