#!/usr/bin/env python3
"""
Tool: Address Extractor
Extrai endereços completos das páginas individuais dos anúncios.
"""

import os
import re
import json
import time
import requests
from pathlib import Path
from typing import List, Dict, Optional
import sys
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))
from firecrawl_integration import FirecrawlCrawler

class AddressExtractor:
    """Extrai endereços de anúncios individuais."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        self.crawler = FirecrawlCrawler(api_key=self.api_key)

    def clean_text(self, text: str) -> str:
        """Remove caracteres indesejados do texto."""
        if not text:
            return text

        # Remover markdown links
        text = re.sub(r'\]\(https?://[^\)]+\)', '', text)
        text = re.sub(r'\[|\]', '', text)

        # Remover aspas extras e caracteres especiais
        text = text.replace('")', '').replace('") -', '-')
        text = text.strip()

        return text

    def extract_address_from_markdown(self, markdown: str, listing_url: str) -> Optional[Dict]:
        """
        Extrai endereço do markdown da página individual.

        Padrões comuns no VivaReal:
        - "Rua Nome da Rua - Bairro, São Paulo - SP"
        - "Avenida Nome - Bairro, São Paulo - SP"
        """
        # Procurar por padrões de endereço
        patterns = [
            r'((?:Rua|Avenida|Alameda|Travessa|Praça)\s+[^,\n\]]+)\s*-\s*([^,\n\]]+),\s*São Paulo\s*-\s*SP',
            r'((?:Rua|Avenida|Alameda|Travessa|Praça)\s+[^-\n\]]+)\s*-\s*([^,\n\]]+)',
            r'Endereço[:\s]+((?:Rua|Avenida|Alameda)\s+[^,\n\]]+)',
        ]

        for pattern in patterns:
            match = re.search(pattern, markdown, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 2:
                    street = self.clean_text(match.group(1))
                    neighborhood = self.clean_text(match.group(2))
                    full_address = f"{street} - {neighborhood}, São Paulo - SP"
                else:
                    full_address = self.clean_text(match.group(1))

                return {
                    "full_address": full_address,
                    "street": street if len(match.groups()) >= 1 else None,
                    "neighborhood": neighborhood if len(match.groups()) >= 2 else None
                }

        # Fallback: tentar extrair bairro da URL
        url_match = re.search(r'/([a-z-]+)-zona-[a-z]+', listing_url)
        if url_match:
            neighborhood = url_match.group(1).replace('-', ' ').title()
            return {
                "full_address": f"{neighborhood}, São Paulo - SP",
                "street": None,
                "neighborhood": neighborhood
            }

        return None

    def geocode_address(self, address: str) -> Optional[Dict[str, float]]:
        """
        Converte endereço em coordenadas usando Google Geocoding API.

        Requer GOOGLE_MAPS_API_KEY no .env
        """
        google_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

        # Tentar Google Maps API primeiro (mais preciso para Brasil)
        if google_api_key and google_api_key != "your_google_maps_api_key_here":
            try:
                url = "https://maps.googleapis.com/maps/api/geocode/json"
                params = {
                    "address": address,
                    "key": google_api_key,
                    "region": "br"  # Priorizar Brasil
                }

                response = requests.get(url, params=params, timeout=10)
                response.raise_for_status()

                data = response.json()
                if data.get("status") == "OK" and data.get("results"):
                    location = data["results"][0]["geometry"]["location"]
                    return {
                        "lat": float(location["lat"]),
                        "lng": float(location["lng"])
                    }
                elif data.get("status") != "OK":
                    print(f"   ⚠️  Google Geocoding: {data.get('status')}")

            except Exception as e:
                print(f"   ⚠️  Erro Google Geocoding: {e}")

        # Fallback: Nominatim (OpenStreetMap) - gratuito mas menos preciso
        try:
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                "q": address,
                "format": "json",
                "limit": 1,
                "countrycodes": "br"
            }
            headers = {
                "User-Agent": "VivaRealMarketResearch/1.0"
            }

            response = requests.get(url, params=params, headers=headers, timeout=10)
            response.raise_for_status()

            data = response.json()
            if data and len(data) > 0:
                return {
                    "lat": float(data[0]["lat"]),
                    "lng": float(data[0]["lon"])
                }

        except Exception as e:
            print(f"   ⚠️  Erro Nominatim: {e}")

        return None

    def extract_addresses_from_listings(self, listings: List[Dict],
                                       delay: int = 3) -> List[Dict]:
        """
        Extrai endereços de uma lista de anúncios.

        Args:
            listings: Lista de anúncios com campo 'link'
            delay: Delay entre requests (segundos)

        Returns:
            Lista de anúncios enriquecidos com endereço e coordenadas
        """
        print(f"\n📍 Extraindo Endereços Reais\n")
        print(f"   Total de anúncios: {len(listings)}")
        print(f"   Delay entre requests: {delay}s\n")

        enriched_listings = []

        for i, listing in enumerate(listings, 1):
            print(f"[{i}/{len(listings)}] Processando...")

            # Fazer scrape da página individual
            result = self.crawler.scrape_url(listing['link'], formats=['markdown'])

            if not result.get('success'):
                print(f"   ❌ Erro no scrape: {result.get('error')}")
                enriched_listings.append(listing)
                continue

            markdown = result.get('data', {}).get('markdown', '')

            # Extrair endereço
            address_info = self.extract_address_from_markdown(markdown, listing['link'])

            if address_info:
                full_address = address_info['full_address']
                print(f"   ✅ Endereço: {full_address}")

                # Geocoding
                coords = self.geocode_address(full_address)

                if coords:
                    print(f"   📍 Coordenadas: {coords['lat']:.6f}, {coords['lng']:.6f}")
                else:
                    print(f"   ⚠️  Geocoding falhou, usando coordenadas aproximadas")
                    coords = None

                # Adicionar informações ao listing
                listing_enriched = listing.copy()
                listing_enriched['address'] = address_info
                listing_enriched['coordinates'] = coords

                enriched_listings.append(listing_enriched)

                # Delay para não sobrecarregar
                if i < len(listings):
                    time.sleep(delay)
            else:
                print(f"   ⚠️  Endereço não encontrado")
                enriched_listings.append(listing)

        print(f"\n✅ Processamento concluído!")
        with_address = sum(1 for l in enriched_listings if 'address' in l)
        with_coords = sum(1 for l in enriched_listings if l.get('coordinates'))
        print(f"   Com endereço: {with_address}/{len(enriched_listings)}")
        print(f"   Com coordenadas: {with_coords}/{len(enriched_listings)}")

        return enriched_listings


def main():
    """CLI."""
    import argparse

    parser = argparse.ArgumentParser(description="Extrair endereços de anúncios")
    parser.add_argument("--input", default="data/processed/listings.json")
    parser.add_argument("--output", default="data/processed/listings_with_addresses.json")
    parser.add_argument("--delay", type=int, default=3, help="Delay entre requests (s)")

    args = parser.parse_args()

    # Carregar anúncios
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"❌ Arquivo não encontrado: {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        listings = json.load(f)

    print(f"📂 Carregados {len(listings)} anúncios")

    # Extrair endereços
    extractor = AddressExtractor()
    enriched = extractor.extract_addresses_from_listings(listings, delay=args.delay)

    # Salvar
    output_path = Path(args.output)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enriched, f, indent=2, ensure_ascii=False)

    print(f"\n💾 Salvo em: {output_path}")


if __name__ == "__main__":
    main()
