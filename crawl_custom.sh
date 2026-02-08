#!/bin/bash
# Script para crawl customizado do VivaReal

# Configuração
REGION="${1:-interlagos}"
MIN_AREA="${2:-30}"
MAX_AREA="${3:-40}"
ZONE="${4:-zona-sul}"
MAX_PAGES="${5:-10}"
TIPO_NEGOCIO="${6:-residencial}"
TIPO_IMOVEL="${7:-apartamento}"

echo "🔍 Configuração do Crawl:"
echo "   Região: $REGION"
echo "   Área: $MIN_AREA-$MAX_AREA m²"
echo "   Zona: $ZONE"
echo "   Tipo: $TIPO_NEGOCIO"
echo "   Tipologia: $TIPO_IMOVEL"
echo "   Páginas: $MAX_PAGES"
echo ""

# Exportar API key
export FIRECRAWL_API_KEY=$(grep FIRECRAWL_API_KEY .env | cut -d'=' -f2)

# Criar script Python temporário
cat > /tmp/crawl_vivareal_custom.py << 'PYTHON_SCRIPT'
import os
import sys
import json
sys.path.insert(0, 'tools')
from firecrawl_integration import FirecrawlCrawler
from pathlib import Path

region = sys.argv[1]
min_area = int(sys.argv[2])
max_area = int(sys.argv[3])
zone = sys.argv[4]
max_pages = int(sys.argv[5])
tipo_negocio = sys.argv[6] if len(sys.argv) > 6 else "residencial"
tipo_imovel = sys.argv[7] if len(sys.argv) > 7 else "apartamento"

crawler = FirecrawlCrawler()
output_dir = Path("data/raw")

# URL base
base_url = f"https://www.vivareal.com.br/venda/sp/sao-paulo/{zone}/{region}/{tipo_imovel}_{tipo_negocio}/?tipos={tipo_imovel}&areaUtil={min_area}-{max_area}"

print(f"\n🚀 Iniciando Crawl\n")
saved_files = []

for page_num in range(1, max_pages + 1):
    url = base_url if page_num == 1 else f"{base_url}&pagina={page_num}"

    print(f"📄 Página {page_num}/{max_pages}")
    result = crawler.scrape_url(url, formats=['markdown'])

    if result.get('success'):
        markdown = result.get('data', {}).get('markdown', '')

        if markdown:
            # Salvar Markdown
            md_file = output_dir / f"page_{page_num:03d}.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(markdown)
            print(f"   ✅ Salvo: {md_file} ({len(markdown)} chars)")
            saved_files.append(str(md_file))
        else:
            print(f"   ⚠️  Markdown vazio")
    else:
        print(f"   ❌ Erro: {result.get('error')}")

print(f"\n✅ Crawl concluído! {len(saved_files)} páginas salvas")

# Salvar metadata
metadata = {
    "region": region,
    "zone": zone,
    "min_area": min_area,
    "max_area": max_area,
    "pages_crawled": len(saved_files),
    "files": saved_files
}

with open(output_dir / "crawl_metadata.json", 'w') as f:
    json.dump(metadata, f, indent=2)
PYTHON_SCRIPT

# Executar crawl
python3 /tmp/crawl_vivareal_custom.py "$REGION" "$MIN_AREA" "$MAX_AREA" "$ZONE" "$MAX_PAGES" "$TIPO_NEGOCIO" "$TIPO_IMOVEL"

echo ""
echo "📊 Próximos passos:"
echo "   1. python3 tools/parse_markdown.py --input data/raw/page_001.md --min-area $MIN_AREA --max-area $MAX_AREA"
echo "   2. python3 tools/generate_report.py"
echo "   3. open reports/vivareal_*.xlsx"
