# Workflow: Pesquisa de Mercado Imobiliário - VivaReal

## Objetivo
Coletar e analisar dados de apartamentos anunciados no VivaReal na região de Freguesia do Ó (SP), gerando um relatório Excel com preços e métricas de mercado.

## Requisitos
- Região: Freguesia do Ó, São Paulo
- Tamanho: 40-45 m²
- Volume mínimo: 100 anúncios
- Output: Excel com [Link, Valor (R$), Tamanho (m²), Valor/m²]

## Processo (WAT Framework)

### Fase 1: Coleta de Dados (Tool: crawl_vivareal.py)
**Entrada**: Parâmetros de busca (região, área)
**Ação**:
1. Acessar VivaReal com filtros específicos
2. Navegar pelas páginas de resultados
3. Salvar HTML/Markdown bruto em `data/raw/`
4. Registrar URLs coletadas

**Saída**: Arquivos brutos de páginas de anúncios
**Verificação**: Pelo menos 100 anúncios salvos

---

### Fase 2: Extração de Dados (Tool: parse_listings.py)
**Entrada**: Arquivos brutos em `data/raw/`
**Ação**:
1. Parsear HTML/Markdown
2. Extrair campos:
   - Link do anúncio
   - Preço total (R$)
   - Área (m²)
   - Localização (validar Freguesia do Ó)
3. Filtrar dados inválidos/incompletos
4. Salvar JSON estruturado em `data/processed/`

**Saída**: `listings.json` com dados limpos
**Verificação**:
- Todos os registros têm preço e área válidos
- Área entre 40-45 m²

---

### Fase 3: Análise e Relatório (Tool: generate_report.py)
**Entrada**: `listings.json`
**Ação**:
1. Calcular `Valor/m²` para cada anúncio
2. Gerar DataFrame pandas
3. Calcular estatísticas:
   - Preço médio e mediano
   - Valor/m² médio
   - Min/Max
4. Exportar para Excel com colunas especificadas

**Saída**: `reports/vivareal_freguesia_do_o.xlsx`
**Verificação**:
- Excel gerado com ≥100 linhas
- Colunas: Link, Valor (R$), Tamanho (m²), Valor/m²
- Sem valores nulos nas colunas principais

---

## Orquestração (Agent)
O script `run_research.py` coordena as três fases sequencialmente:
```bash
python run_research.py --region "freguesia-do-o" --min-area 40 --max-area 45 --min-count 100
```

## Rollback
Em caso de falha:
1. Fase 1: Deletar `data/raw/*` e recrawl
2. Fase 2: Corrigir parser e reprocessar
3. Fase 3: Reexecutar análise (não requer crawl)

## Métricas de Sucesso
- ✅ 100+ anúncios coletados
- ✅ Taxa de parsing >90%
- ✅ Excel gerado sem erros
- ✅ Dados dentro dos filtros (40-45 m²)
