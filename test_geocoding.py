#!/usr/bin/env python3
"""
Script de teste para validar Google Geocoding API
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

sys.path.insert(0, str(Path(__file__).parent / "tools"))
from extract_addresses import AddressExtractor

def test_geocoding():
    """Testa se o Google Geocoding está funcionando."""

    print("🧪 Teste do Google Geocoding API\n")

    # Verificar API key
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")

    if not api_key or api_key == "sua_google_api_key_aqui":
        print("❌ GOOGLE_MAPS_API_KEY não configurada no .env")
        print("\n💡 Como configurar:")
        print("   1. Edite o arquivo .env")
        print("   2. Substitua 'sua_google_api_key_aqui' pela sua chave real")
        print("   3. Execute este script novamente")
        return False

    print(f"✅ API Key encontrada: {api_key[:20]}...\n")

    # Testar geocoding
    extractor = AddressExtractor()

    test_addresses = [
        "Rua Olívia Guedes Penteado - Interlagos, São Paulo - SP",
        "Rua Aimorés - Interlagos, São Paulo - SP",
        "Avenida Paulista, 1578 - Bela Vista, São Paulo - SP"
    ]

    print("📍 Testando geocoding de endereços reais:\n")

    success_count = 0
    for addr in test_addresses:
        print(f"Testando: {addr}")
        coords = extractor.geocode_address(addr)

        if coords:
            print(f"   ✅ GPS: {coords['lat']:.6f}, {coords['lng']:.6f}")
            success_count += 1
        else:
            print(f"   ❌ Falhou")

        print()

    print(f"{'='*60}")
    print(f"Resultado: {success_count}/{len(test_addresses)} endereços geocodificados")
    print(f"{'='*60}\n")

    if success_count == len(test_addresses):
        print("🎉 Google Geocoding funcionando perfeitamente!")
        print("\n💡 Próximos passos:")
        print("   1. python3 tools/extract_addresses.py --delay 4")
        print("   2. python3 tools/generate_map.py --input data/processed/listings_with_addresses.json")
        print("   3. open reports/mapa_*.html")
        return True
    elif success_count > 0:
        print("⚠️  Parcialmente funcionando. Alguns endereços falharam.")
        return True
    else:
        print("❌ Nenhum endereço foi geocodificado.")
        print("\n🔧 Troubleshooting:")
        print("   1. Verifique se a API key está correta")
        print("   2. Confirme que Geocoding API está habilitada no Google Console")
        print("   3. Verifique se tem créditos/billing configurado")
        return False


if __name__ == "__main__":
    test_geocoding()
