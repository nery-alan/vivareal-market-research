#!/usr/bin/env python3
"""
Tool: VivaReal Parser
Extrai dados estruturados de páginas HTML crawleadas do VivaReal.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

class VivaRealParser:
    def __init__(self, input_dir: str = "data/raw", output_dir: str = "data/processed"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_price(self, text: str) -> Optional[float]:
        """Extrai valor em reais de texto."""
        if not text:
            return None

        # Remove tudo exceto dígitos
        digits = re.sub(r'[^\d]', '', text)

        try:
            return float(digits) if digits else None
        except ValueError:
            return None

    def extract_area(self, text: str) -> Optional[float]:
        """Extrai área em m² de texto."""
        if not text:
            return None

        # Procura padrão: número + m² ou m2
        match = re.search(r'(\d+(?:[.,]\d+)?)\s*m[²2]', text.lower())
        if match:
            area_str = match.group(1).replace(',', '.')
            try:
                return float(area_str)
            except ValueError:
                return None

        return None

    def extract_listing(self, card_element) -> Optional[Dict]:
        """
        Extrai dados de um card de anúncio.

        Estrutura típica do VivaReal:
        - Link: <a href="..."> no card principal
        - Preço: class contendo "price" ou texto com R$
        - Área: texto contendo "m²"
        """
        try:
            # Extrair link
            link_elem = card_element.find('a', href=True)
            if not link_elem:
                return None

            link = link_elem.get('href', '')
            if link.startswith('/'):
                link = f"https://www.vivareal.com.br{link}"

            # Extrair preço
            price_text = None
            price_selectors = [
                {'class_': re.compile(r'price', re.I)},
                {'attrs': {'data-type': 'price'}},
                {'string': re.compile(r'R\$', re.I)},
            ]

            for selector in price_selectors:
                price_elem = card_element.find(['p', 'span', 'div'], **selector)
                if price_elem:
                    price_text = price_elem.get_text(strip=True)
                    break

            price = self.extract_price(price_text) if price_text else None

            # Extrair área
            area_text = card_element.get_text()
            area = self.extract_area(area_text)

            # Validar dados mínimos
            if not link or not price or not area:
                return None

            return {
                "link": link,
                "price": price,
                "area": area,
                "price_per_sqm": round(price / area, 2) if area > 0 else None
            }

        except Exception as e:
            print(f"⚠️  Erro ao processar card: {e}")
            return None

    def parse_page(self, html_path: Path) -> List[Dict]:
        """Parseia uma página HTML e extrai todos os anúncios."""
        print(f"📄 Parsing: {html_path.name}")

        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()

        soup = BeautifulSoup(html_content, 'lxml')

        # Tentar identificar cards de anúncios
        # VivaReal geralmente usa classes como "property-card", "result-card", etc.
        card_selectors = [
            {'class_': re.compile(r'property.*card', re.I)},
            {'class_': re.compile(r'result.*card', re.I)},
            {'class_': re.compile(r'listing.*card', re.I)},
            {'attrs': {'data-type': 'property'}},
        ]

        cards = []
        for selector in card_selectors:
            found = soup.find_all(['div', 'article', 'li'], **selector)
            if found:
                cards = found
                print(f"   ✓ Encontrados {len(cards)} cards com seletor: {selector}")
                break

        # Se não encontrou cards específicos, tentar abordagem alternativa
        if not cards:
            # Procurar por links que contenham "/imovel/"
            links = soup.find_all('a', href=re.compile(r'/imovel/'))
            # Pegar parent elements como "cards"
            cards = list(set([link.find_parent(['div', 'article', 'li']) for link in links if link.find_parent(['div', 'article', 'li'])]))
            print(f"   ✓ Encontrados {len(cards)} cards via links")

        # Extrair dados de cada card
        listings = []
        for card in cards:
            listing = self.extract_listing(card)
            if listing:
                listings.append(listing)

        print(f"   ✅ Extraídos {len(listings)} anúncios válidos")
        return listings

    def parse_all(self, min_area: float = 40, max_area: float = 45) -> List[Dict]:
        """
        Parseia todas as páginas HTML no diretório de entrada.

        Args:
            min_area: Filtro de área mínima
            max_area: Filtro de área máxima

        Returns:
            Lista de anúncios filtrados e validados
        """
        print(f"\n🔍 Iniciando parsing de arquivos HTML")
        print(f"   Input dir: {self.input_dir}")
        print(f"   Filtro área: {min_area}-{max_area} m²\n")

        html_files = sorted(self.input_dir.glob("page_*.html"))

        if not html_files:
            print("❌ Nenhum arquivo HTML encontrado!")
            return []

        all_listings = []

        for html_file in html_files:
            page_listings = self.parse_page(html_file)
            all_listings.extend(page_listings)

        # Filtrar por área
        filtered_listings = [
            listing for listing in all_listings
            if min_area <= listing['area'] <= max_area
        ]

        # Remover duplicatas (mesmo link)
        unique_listings = {}
        for listing in filtered_listings:
            unique_listings[listing['link']] = listing

        final_listings = list(unique_listings.values())

        print(f"\n📊 Resumo do Parsing:")
        print(f"   Total extraído: {len(all_listings)}")
        print(f"   Após filtro de área: {len(filtered_listings)}")
        print(f"   Após remoção de duplicatas: {len(final_listings)}")

        # Salvar resultado
        output_path = self.output_dir / "listings.json"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_listings, f, indent=2, ensure_ascii=False)

        print(f"\n✅ Dados salvos: {output_path}")

        return final_listings


def main():
    """CLI para execução standalone."""
    import argparse

    parser = argparse.ArgumentParser(description="Parse VivaReal HTML files")
    parser.add_argument("--input", default="data/raw", help="Diretório de entrada (HTML)")
    parser.add_argument("--output", default="data/processed", help="Diretório de saída (JSON)")
    parser.add_argument("--min-area", type=float, default=40, help="Área mínima (m²)")
    parser.add_argument("--max-area", type=float, default=45, help="Área máxima (m²)")

    args = parser.parse_args()

    parser = VivaRealParser(input_dir=args.input, output_dir=args.output)
    listings = parser.parse_all(min_area=args.min_area, max_area=args.max_area)

    if listings:
        print(f"\n🎉 Sucesso! {len(listings)} anúncios prontos para análise")
    else:
        print("\n⚠️  Nenhum anúncio válido encontrado")


if __name__ == "__main__":
    main()
