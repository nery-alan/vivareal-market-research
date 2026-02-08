#!/usr/bin/env python3
"""
Tool: Markdown Parser
Parser específico para arquivos Markdown do Firecrawl/VivaReal.
"""

import re
import json
from pathlib import Path
from typing import List, Dict, Optional

class MarkdownParser:
    """Parser para extrair anúncios de arquivos Markdown."""

    def __init__(self, input_file: str = "crawl.md", output_dir: str = "data/processed"):
        self.input_file = Path(input_file)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_price(self, text: str) -> Optional[float]:
        """Extrai preço em reais."""
        # Padrão: R$ 699.000 ou R$ 699000
        match = re.search(r'R\$\s*([\d.]+)', text)
        if match:
            price_str = match.group(1).replace('.', '')
            try:
                return float(price_str)
            except ValueError:
                return None
        return None

    def extract_area(self, text: str) -> Optional[float]:
        """Extrai área em m²."""
        # Padrão: "67 m²" ou "67m²" ou "Tamanho do imóvel 67 m²"
        match = re.search(r'(\d+(?:[.,]\d+)?)\s*m[²2]', text, re.IGNORECASE)
        if match:
            area_str = match.group(1).replace(',', '.')
            try:
                return float(area_str)
            except ValueError:
                return None
        return None

    def extract_link(self, text: str) -> Optional[str]:
        """Extrai link do anúncio."""
        # Procura por links do vivareal.com.br/imovel/
        match = re.search(r'https://www\.vivareal\.com\.br/imovel/[^\s\)]+', text)
        if match:
            return match.group(0)

        # Tenta também formato Markdown [text](url)
        match = re.search(r'\]\((https://www\.vivareal\.com\.br/[^\)]+)\)', text)
        if match:
            return match.group(1)

        return None

    def parse_listing_block(self, block: str) -> Optional[Dict]:
        """
        Parseia um bloco de anúncio.

        Estrutura esperada:
        - Link com URL
        - Preço: R$ XXX.XXX
        - Área: XX m²
        """
        # Extrair dados
        link = self.extract_link(block)
        price = self.extract_price(block)
        area = self.extract_area(block)

        # Validar dados mínimos
        if not link or not price or not area:
            return None

        return {
            "link": link,
            "price": price,
            "area": area,
            "price_per_sqm": round(price / area, 2) if area > 0 else None
        }

    def parse_markdown(self, min_area: float = 40, max_area: float = 45) -> List[Dict]:
        """
        Parseia arquivo Markdown completo.

        Estratégia: Dividir em blocos por anúncio e processar cada um.
        """
        print(f"\n🔍 Parsing Markdown: {self.input_file}")
        print(f"   Filtro área: {min_area}-{max_area} m²\n")

        if not self.input_file.exists():
            print(f"❌ Arquivo não encontrado: {self.input_file}")
            return []

        # Ler arquivo
        with open(self.input_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Dividir por anúncios
        # Cada anúncio geralmente começa com "- [" ou tem um padrão de link
        # Vamos dividir em chunks maiores e processar

        listings = []
        lines = content.split('\n')

        current_block = []

        for line in lines:
            # Se linha tem link do vivareal, pode ser início de novo anúncio
            if 'vivareal.com.br/imovel' in line.lower():
                # Processar bloco anterior se existir
                if current_block:
                    block_text = '\n'.join(current_block)
                    listing = self.parse_listing_block(block_text)
                    if listing:
                        listings.append(listing)

                # Iniciar novo bloco
                current_block = [line]
            else:
                # Adicionar linha ao bloco atual
                current_block.append(line)

        # Processar último bloco
        if current_block:
            block_text = '\n'.join(current_block)
            listing = self.parse_listing_block(block_text)
            if listing:
                listings.append(listing)

        print(f"   ✅ Total extraído: {len(listings)} anúncios")

        # Filtrar por área
        filtered_listings = [
            listing for listing in listings
            if min_area <= listing['area'] <= max_area
        ]

        print(f"   ✅ Após filtro ({min_area}-{max_area} m²): {len(filtered_listings)} anúncios")

        # Remover duplicatas por link
        unique_listings = {}
        for listing in filtered_listings:
            unique_listings[listing['link']] = listing

        final_listings = list(unique_listings.values())

        print(f"   ✅ Após remover duplicatas: {len(final_listings)} anúncios")

        # Salvar resultado
        output_path = self.output_dir / "listings.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_listings, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Dados salvos: {output_path}")

        return final_listings


def main():
    """CLI para execução standalone."""
    import argparse

    parser = argparse.ArgumentParser(description="Parse VivaReal Markdown file")
    parser.add_argument("--input", default="crawl.md", help="Arquivo Markdown de entrada")
    parser.add_argument("--output-dir", default="data/processed", help="Diretório de saída")
    parser.add_argument("--min-area", type=float, default=40, help="Área mínima (m²)")
    parser.add_argument("--max-area", type=float, default=45, help="Área máxima (m²)")

    args = parser.parse_args()

    md_parser = MarkdownParser(input_file=args.input, output_dir=args.output_dir)
    listings = md_parser.parse_markdown(min_area=args.min_area, max_area=args.max_area)

    if listings:
        print(f"\n🎉 Sucesso! {len(listings)} anúncios prontos para análise")

        # Mostrar preview
        print("\n📊 Preview dos primeiros 3 anúncios:")
        for i, listing in enumerate(listings[:3], 1):
            print(f"\n{i}. R$ {listing['price']:,.2f} - {listing['area']}m² (R$ {listing['price_per_sqm']}/m²)")
            print(f"   Link: {listing['link'][:80]}...")
    else:
        print("\n⚠️  Nenhum anúncio válido encontrado")


if __name__ == "__main__":
    main()
