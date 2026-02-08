#!/usr/bin/env python3
"""
Tool: Map Generator
Gera visualização dos anúncios no Google Maps.
"""

import os
import json
import re
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

class MapGenerator:
    """Gerador de mapas HTML com Google Maps."""

    # Coordenadas aproximadas dos bairros de SP
    COORDINATES = {
        "interlagos": {"lat": -23.6797, "lng": -46.6893},
        "socorro": {"lat": -23.6425, "lng": -46.6947},
        "vila-mariana": {"lat": -23.5871, "lng": -46.6364},
        "moema": {"lat": -23.6011, "lng": -46.6664},
        "pinheiros": {"lat": -23.5629, "lng": -46.6979},
        "santana": {"lat": -23.5065, "lng": -46.6290},
        "tatuape": {"lat": -23.5403, "lng": -46.5766},
        "freguesia-do-o": {"lat": -23.4983, "lng": -46.7031},
        "brooklin": {"lat": -23.6069, "lng": -46.6950},
        "campo-belo": {"lat": -23.6155, "lng": -46.6726},
        "perdizes": {"lat": -23.5344, "lng": -46.6718},
        "lapa": {"lat": -23.5279, "lng": -46.7082},
        "mooca": {"lat": -23.5554, "lng": -46.5989},
        "penha": {"lat": -23.5290, "lng": -46.5419},
    }

    def __init__(self, input_file: str = "data/processed/listings.json",
                 output_dir: str = "reports",
                 region: str = None,
                 min_area: int = None,
                 max_area: int = None):
        self.input_file = Path(input_file)
        self.base_output_dir = Path(output_dir)
        self.region = region
        self.min_area = min_area
        self.max_area = max_area

        # Criar pasta estruturada se tiver região e tamanho
        self.output_dir = self._create_structured_folder()
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _create_structured_folder(self) -> Path:
        """Cria pasta estruturada: reports/bairro-tamanho-data/"""
        from datetime import datetime
        import json

        # Se não tiver região, tentar detectar da metadata
        region = self.region
        if not region:
            metadata_file = Path("data/raw/crawl_metadata.json")
            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    region = metadata.get('region', None)

        # Se ainda não tiver, usar base_output_dir
        if not region:
            return self.base_output_dir

        # Criar nome da pasta: bairro-tamanho-data
        date_str = datetime.now().strftime("%Y%m%d")

        if self.min_area and self.max_area:
            folder_name = f"{region}-{self.min_area}-{self.max_area}-{date_str}"
        else:
            folder_name = f"{region}-{date_str}"

        return self.base_output_dir / folder_name

    def extract_region(self, url: str) -> Optional[str]:
        """Extrai região da URL."""
        match = re.search(r'/([a-z-]+)-sao-paulo/', url)
        if match:
            return match.group(1)
        return None

    def get_coordinates(self, region: str) -> Dict[str, float]:
        """Retorna coordenadas do bairro ou coordenadas padrão de SP."""
        if not region:
            return {"lat": -23.5505, "lng": -46.6333}  # Centro de SP

        coords = self.COORDINATES.get(region)
        if coords:
            return coords

        # Coordenadas padrão de SP
        return {"lat": -23.5505, "lng": -46.6333}

    def load_listings(self) -> List[Dict]:
        """Carrega anúncios do JSON."""
        if not self.input_file.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.input_file}")

        with open(self.input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return data

    def generate_map_html(self, listings: List[Dict], region_name: str = "Região") -> Path:
        """Gera arquivo HTML com mapa interativo."""

        # Obter chave do Google Maps do .env
        google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY", "YOUR_API_KEY_HERE")

        # Preparar dados para o mapa
        markers_data = []
        has_real_coords = 0

        for listing in listings:
            # Usar coordenadas reais se disponíveis
            if 'coordinates' in listing and listing['coordinates']:
                coords = listing['coordinates']
                has_real_coords += 1
            else:
                # Fallback para coordenadas aproximadas
                region = self.extract_region(listing['link'])
                coords = self.get_coordinates(region)

                # Adicionar pequena variação aleatória para evitar sobreposição
                import random
                coords['lat'] += random.uniform(-0.005, 0.005)
                coords['lng'] += random.uniform(-0.005, 0.005)

            # Pegar endereço se disponível
            address_info = listing.get('address', {})
            full_address = address_info.get('full_address', 'Endereço não disponível')
            region = address_info.get('neighborhood', self.extract_region(listing['link']) or "Desconhecido")

            marker = {
                "lat": coords['lat'],
                "lng": coords['lng'],
                "price": listing['price'],
                "area": listing['area'],
                "price_per_sqm": listing['price_per_sqm'],
                "link": listing['link'],
                "region": region,
                "address": full_address
            }

            markers_data.append(marker)

        # Calcular centro do mapa (média das coordenadas)
        if markers_data:
            center_lat = sum(m['lat'] for m in markers_data) / len(markers_data)
            center_lng = sum(m['lng'] for m in markers_data) / len(markers_data)
        else:
            center_lat, center_lng = -23.5505, -46.6333

        # Gerar HTML
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Mapa de Imóveis - {region_name}</title>
    <style>
        body {{
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }}
        #map {{
            height: 100vh;
            width: 100%;
        }}
        .info-header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .info-header h1 {{
            margin: 0;
            font-size: 24px;
        }}
        .info-header p {{
            margin: 5px 0 0 0;
            opacity: 0.9;
        }}
        .info-window {{
            max-width: 300px;
        }}
        .info-window h3 {{
            margin: 0 0 10px 0;
            color: #667eea;
        }}
        .info-window p {{
            margin: 5px 0;
            font-size: 14px;
        }}
        .info-window a {{
            display: inline-block;
            margin-top: 10px;
            padding: 8px 16px;
            background: #667eea;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            font-size: 12px;
        }}
        .info-window a:hover {{
            background: #764ba2;
        }}
    </style>
</head>
<body>
    <div class="info-header">
        <h1>🏢 Mapa de Imóveis - {region_name}</h1>
        <p>📊 {len(markers_data)} anúncios | 💰 Clique nos pins para detalhes</p>
    </div>
    <div id="map"></div>

    <script>
        function initMap() {{
            // Configurar mapa
            const map = new google.maps.Map(document.getElementById('map'), {{
                center: {{ lat: {center_lat}, lng: {center_lng} }},
                zoom: 13,
                styles: [
                    {{
                        "featureType": "poi",
                        "elementType": "labels",
                        "stylers": [{{ "visibility": "off" }}]
                    }}
                ]
            }});

            // Dados dos anúncios
            const listings = {json.dumps(markers_data, ensure_ascii=False)};

            // Adicionar marcadores
            listings.forEach((listing, index) => {{
                const marker = new google.maps.Marker({{
                    position: {{ lat: listing.lat, lng: listing.lng }},
                    map: map,
                    title: `R$ ${{listing.price.toLocaleString('pt-BR')}}`,
                    label: {{
                        text: `${{(listing.price / 1000).toFixed(0)}}k`,
                        color: 'white',
                        fontSize: '12px',
                        fontWeight: 'bold'
                    }},
                    icon: {{
                        path: google.maps.SymbolPath.CIRCLE,
                        scale: 15,
                        fillColor: getColorByPrice(listing.price_per_sqm),
                        fillOpacity: 0.8,
                        strokeColor: 'white',
                        strokeWeight: 2
                    }}
                }});

                // Info window
                const infoContent = `
                    <div class="info-window">
                        <h3>R$ ${{listing.price.toLocaleString('pt-BR')}}</h3>
                        <p><strong>📏 Área:</strong> ${{listing.area}} m²</p>
                        <p><strong>💰 Valor/m²:</strong> R$ ${{listing.price_per_sqm.toLocaleString('pt-BR')}}/m²</p>
                        <p><strong>📍 Endereço:</strong> ${{listing.address}}</p>
                        <a href="${{listing.link}}" target="_blank">Ver Anúncio →</a>
                    </div>
                `;

                const infoWindow = new google.maps.InfoWindow({{
                    content: infoContent
                }});

                marker.addListener('click', () => {{
                    infoWindow.open(map, marker);
                }});
            }});

            // Função para colorir pins por preço/m²
            function getColorByPrice(pricePerSqm) {{
                if (pricePerSqm < 7000) return '#4CAF50';      // Verde (barato)
                if (pricePerSqm < 9000) return '#FFC107';      // Amarelo (médio)
                if (pricePerSqm < 11000) return '#FF9800';     // Laranja (caro)
                return '#F44336';                               // Vermelho (muito caro)
            }}
        }}
    </script>

    <!-- Google Maps API -->
    <script src="https://maps.googleapis.com/maps/api/js?key={google_maps_key}&callback=initMap" async defer></script>
</body>
</html>"""

        # Salvar HTML com nome simplificado
        output_file = self.output_dir / "mapa.html"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_file

    def generate(self) -> Path:
        """Gera mapa completo."""
        print("\n🗺️  Gerando Mapa Interativo\n")

        # Carregar dados
        listings = self.load_listings()
        print(f"✅ {len(listings)} anúncios carregados")

        # Detectar região principal
        regions = {}
        for listing in listings:
            region = self.extract_region(listing['link'])
            if region:
                regions[region] = regions.get(region, 0) + 1

        main_region = max(regions, key=regions.get) if regions else "Região"
        print(f"📍 Região principal: {main_region}")

        # Gerar HTML
        map_file = self.generate_map_html(listings, main_region.title())

        print(f"\n✅ Mapa gerado: {map_file}")
        print(f"🌐 Abra em: file://{map_file.absolute()}")

        return map_file


def main():
    """CLI."""
    import argparse

    parser = argparse.ArgumentParser(description="Gerar mapa de anúncios")
    parser.add_argument("--input", default="data/processed/listings.json")
    parser.add_argument("--output-dir", default="reports")
    parser.add_argument("--region", help="Região da pesquisa")
    parser.add_argument("--min-area", type=int, help="Área mínima")
    parser.add_argument("--max-area", type=int, help="Área máxima")

    args = parser.parse_args()

    generator = MapGenerator(
        args.input,
        args.output_dir,
        region=args.region,
        min_area=args.min_area,
        max_area=args.max_area
    )

    try:
        map_file = generator.generate()
        print(f"\n💡 Para abrir:")
        print(f"   open {map_file}")
    except Exception as e:
        print(f"\n❌ Erro: {e}")


if __name__ == "__main__":
    main()
