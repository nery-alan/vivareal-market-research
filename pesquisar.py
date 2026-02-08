#!/usr/bin/env python3
"""
Script Interativo de Pesquisa Imobiliária - VivaReal
Perguntas: Compra/Venda, Tamanho, Endereço
"""

import os
import sys
import json
import subprocess
from pathlib import Path

# Mapas de regiões
REGIOES_ZONAS = {
    # Zona Sul
    "interlagos": "zona-sul",
    "vila-mariana": "zona-sul",
    "moema": "zona-sul",
    "brooklin": "zona-sul",
    "campo-belo": "zona-sul",
    "jabaquara": "zona-sul",
    "santo-amaro": "zona-sul",
    "morumbi": "zona-sul",
    "socorro": "zona-sul",
    "cidade-ademar": "zona-sul",

    # Zona Norte
    "freguesia-do-o": "zona-norte",
    "santana": "zona-norte",
    "tucuruvi": "zona-norte",
    "vila-maria": "zona-norte",
    "vila-guilherme": "zona-norte",
    "casa-verde": "zona-norte",
    "cachoeirinha": "zona-norte",

    # Zona Oeste
    "pinheiros": "zona-oeste",
    "perdizes": "zona-oeste",
    "lapa": "zona-oeste",
    "vila-madalena": "zona-oeste",
    "alto-de-pinheiros": "zona-oeste",
    "butanta": "zona-oeste",

    # Zona Leste
    "tatuape": "zona-leste",
    "mooca": "zona-leste",
    "vila-prudente": "zona-leste",
    "penha": "zona-leste",
    "aricanduva": "zona-leste",
    "sao-mateus": "zona-leste",
    "itaquera": "zona-leste",
}

def normalizar_regiao(regiao: str) -> str:
    """Normaliza nome da região para slug."""
    # Remove acentos e caracteres especiais
    regiao = regiao.lower().strip()
    regiao = regiao.replace(" ", "-")
    regiao = regiao.replace("á", "a").replace("é", "e").replace("í", "i")
    regiao = regiao.replace("ó", "o").replace("ú", "u").replace("ã", "a")
    regiao = regiao.replace("õ", "o").replace("ç", "c")
    return regiao

def banner():
    """Mostra banner do sistema."""
    print("\n" + "="*60)
    print("🏢  PESQUISA DE MERCADO IMOBILIÁRIO - VIVAREAL")
    print("="*60)
    print("\nFramework WAT: Workflows, Agents, Tools")
    print()

def perguntar():
    """Faz perguntas interativas ao usuário."""
    print("📝 Configure sua pesquisa:\n")

    # 1. Compra ou Venda?
    print("1️⃣  Tipo de Transação:")
    print("   [1] Compra (venda)")
    print("   [2] Aluguel")
    tipo = input("\n   Escolha (1 ou 2, padrão: 1): ").strip() or "1"
    transacao = "venda" if tipo == "1" else "aluguel"
    print(f"   ✅ Selecionado: {transacao.upper()}\n")

    # 2. Tipo (Residencial/Comercial)
    print("2️⃣  Tipo de Negócio:")
    print("   [1] Residencial")
    print("   [2] Comercial")
    tipo_negocio_opt = input("\n   Escolha (1 ou 2, padrão: 1): ").strip() or "1"

    tipo_negocio = "residencial" if tipo_negocio_opt == "1" else "comercial"
    print(f"   ✅ Selecionado: {tipo_negocio.upper()}\n")

    # 3. Tipologia de Imóvel
    print("3️⃣  Tipologia do Imóvel:")
    print("   [1] Apartamento")
    print("   [2] Casa")
    print("   [3] Casa de Condomínio")
    print("   [4] Kitnet")
    tipo_imovel_opt = input("\n   Escolha (1-4, padrão: 1): ").strip() or "1"

    tipos_map = {
        "1": "apartamento",
        "2": "casa",
        "3": "casa-de-condominio",
        "4": "kitnet"
    }
    tipo_imovel = tipos_map.get(tipo_imovel_opt, "apartamento")
    print(f"   ✅ Selecionado: {tipo_imovel.upper()}\n")

    # 4. Tamanho
    print("4️⃣  Tamanho do Imóvel:")
    min_area = input("   Área mínima (m²): ").strip()
    max_area = input("   Área máxima (m²): ").strip()

    try:
        min_area = int(min_area) if min_area else 30
        max_area = int(max_area) if max_area else 50
    except ValueError:
        print("   ⚠️  Valores inválidos. Usando padrão: 30-50 m²")
        min_area, max_area = 30, 50

    print(f"   ✅ Tamanho: {min_area}-{max_area} m²\n")

    # 5. Endereço (Região)
    print("5️⃣  Região de Busca:")
    print("   Exemplos: Interlagos, Vila Mariana, Pinheiros, Santana")
    print("   (Digite o nome do bairro)")

    regiao_input = input("\n   Região: ").strip()

    if not regiao_input:
        print("   ❌ Região é obrigatória!")
        sys.exit(1)

    regiao_slug = normalizar_regiao(regiao_input)

    # Tentar detectar zona
    zona = REGIOES_ZONAS.get(regiao_slug)

    if not zona:
        print(f"\n   ⚠️  Região '{regiao_slug}' não encontrada no mapa.")
        print("   Qual zona? (zona-norte, zona-sul, zona-oeste, zona-leste, centro)")
        zona = input("   Zona: ").strip().lower() or "zona-sul"

    print(f"   ✅ Região: {regiao_slug} ({zona})\n")

    # 6. Número de Páginas
    print("6️⃣  Quantidade de Páginas para Crawl:")
    print("   Sugestão: 5-10 páginas (~100-200 anúncios)")
    max_pages = input("\n   Páginas (padrão: 10): ").strip()

    try:
        max_pages = int(max_pages) if max_pages else 10
    except ValueError:
        max_pages = 10

    print(f"   ✅ Páginas: {max_pages}\n")

    return {
        "transacao": transacao,
        "tipo_negocio": tipo_negocio,
        "tipo_imovel": tipo_imovel,
        "regiao": regiao_slug,
        "zona": zona,
        "min_area": min_area,
        "max_area": max_area,
        "max_pages": max_pages
    }

def confirmar(config: dict) -> bool:
    """Mostra resumo e pede confirmação."""
    print("\n" + "="*60)
    print("📋 RESUMO DA PESQUISA")
    print("="*60)
    print(f"""
   Transação:     {config['transacao'].upper()}
   Tipo:          {config['tipo_negocio'].upper()}
   Tipologia:     {config['tipo_imovel'].upper()}
   Região:        {config['regiao']} ({config['zona']})
   Tamanho:       {config['min_area']}-{config['max_area']} m²
   Páginas:       {config['max_pages']}
    """)

    confirma = input("Confirma e inicia crawl? (S/n): ").strip().lower()
    return confirma != 'n'

def executar_crawl(config: dict):
    """Executa o crawl com as configurações."""
    print("\n" + "="*60)
    print("🚀 INICIANDO CRAWL")
    print("="*60 + "\n")

    # Executar crawl_custom.sh
    cmd = [
        "./crawl_custom.sh",
        config['regiao'],
        str(config['min_area']),
        str(config['max_area']),
        config['zona'],
        str(config['max_pages']),
        config['tipo_negocio'],
        config['tipo_imovel']
    ]

    print(f"💻 Comando: {' '.join(cmd)}\n")

    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Erro no crawl: {e}")
        sys.exit(1)

def processar_dados(config: dict):
    """Processa os dados crawleados."""
    print("\n" + "="*60)
    print("🔍 PROCESSANDO DADOS")
    print("="*60 + "\n")

    # Consolidar JSONs
    print("📊 Consolidando anúncios...")

    script = f"""
import json
from pathlib import Path

all_listings = []
unique_links = set()

for json_file in Path('data/processed').glob('temp_*/listings.json'):
    with open(json_file) as f:
        listings = json.load(f)
        for listing in listings:
            if listing['link'] not in unique_links:
                all_listings.append(listing)
                unique_links.add(listing['link'])

print(f'✅ Total: {{len(all_listings)}} anúncios únicos')

with open('data/processed/listings.json', 'w') as f:
    json.dump(all_listings, f, indent=2, ensure_ascii=False)
"""

    subprocess.run(["python3", "-c", script], check=True)

    # Gerar Excel com parâmetros estruturados
    print("\n📈 Gerando relatório Excel...\n")
    subprocess.run([
        "python3", "tools/generate_report.py",
        "--min-count", "1",
        "--region", config['regiao'],
        "--min-area", str(config['min_area']),
        "--max-area", str(config['max_area'])
    ], check=True)

    # Gerar Mapa com parâmetros estruturados
    print("\n🗺️  Gerando mapa interativo...\n")
    subprocess.run([
        "python3", "tools/generate_map.py",
        "--input", "data/processed/listings_with_addresses.json",
        "--region", config['regiao'],
        "--min-area", str(config['min_area']),
        "--max-area", str(config['max_area'])
    ], check=True)

def main():
    """Função principal."""
    banner()

    # Verificar API key
    if not Path(".env").exists():
        print("❌ Erro: Arquivo .env não encontrado!")
        print("\n💡 Configure primeiro:")
        print("   echo 'FIRECRAWL_API_KEY=sua_key' > .env")
        sys.exit(1)

    # Perguntas
    config = perguntar()

    # Confirmar
    if not confirmar(config):
        print("\n❌ Operação cancelada pelo usuário.")
        sys.exit(0)

    # Executar
    executar_crawl(config)

    # Processar primeiro arquivo para teste
    print("\n📄 Processando páginas...")
    for md_file in Path("data/raw").glob("page_*.md"):
        output_dir = Path(f"data/processed/temp_{md_file.stem}")
        subprocess.run([
            "python3", "tools/parse_markdown.py",
            "--input", str(md_file),
            "--min-area", str(config['min_area']),
            "--max-area", str(config['max_area']),
            "--output-dir", str(output_dir)
        ], capture_output=True)

    # Consolidar e gerar Excel
    processar_dados(config)

    # Detectar pasta criada
    from datetime import datetime
    date_str = datetime.now().strftime("%Y%m%d")
    folder_name = f"{config['regiao']}-{config['min_area']}-{config['max_area']}-{date_str}"

    print("\n" + "="*60)
    print("✅ PESQUISA CONCLUÍDA!")
    print("="*60)
    print(f"\n📁 Pasta criada: reports/{folder_name}/")
    print(f"   📊 relatorio.xlsx")
    print(f"   🗺️  mapa.html")
    print("\n💡 Para abrir:")
    print(f"   open reports/{folder_name}/relatorio.xlsx")
    print(f"   open reports/{folder_name}/mapa.html")
    print()

if __name__ == "__main__":
    main()
