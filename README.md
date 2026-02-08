# 🏢 Pesquisa de Mercado Imobiliário - VivaReal

Sistema agêntico para coleta e análise automatizada de dados do mercado imobiliário brasileiro usando o framework **WAT (Workflows, Agents, and Tools)**.

## 📋 Objetivo

Realizar pesquisa de mercado de apartamentos anunciados no VivaReal, coletando dados estruturados e gerando relatórios Excel com análises de preços.

### Caso de Uso Atual
- **Região**: Freguesia do Ó, São Paulo
- **Filtro**: Apartamentos de 40-45 m²
- **Meta**: ≥100 anúncios
- **Output**: Excel com: Link, Valor (R$), Tamanho (m²), Valor/m²

---

## 🏗️ Arquitetura WAT

### Workflows (Processos)
Instruções em Markdown que definem o passo a passo lógico:
- [`workflows/real_estate_research.md`](workflows/real_estate_research.md) - Processo completo de pesquisa

### Agents (Orquestração)
Scripts que gerenciam estado e coordenam execução:
- [`run_research.py`](run_research.py) - Agent principal que coordena o workflow

### Tools (Ações Atômicas)
Scripts especializados para tarefas específicas:
- [`tools/crawl_vivareal.py`](tools/crawl_vivareal.py) - Coleta páginas do VivaReal
- [`tools/parse_listings.py`](tools/parse_listings.py) - Extrai dados estruturados
- [`tools/generate_report.py`](tools/generate_report.py) - Gera análise e Excel

---

## 🚀 Quick Start

### 1. Setup do Ambiente

```bash
# Criar ambiente virtual (recomendado)
python3 -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Executar Workflow Completo

```bash
# Busca padrão (Freguesia do Ó, 40-45m²)
python run_research.py

# Busca customizada
python run_research.py --region "vila-mariana" --min-area 50 --max-area 60 --max-pages 15
```

### 3. Verificar Resultados

```bash
# Excel gerado em reports/
open reports/vivareal_freguesia_do_o_*.xlsx
```

---

## 📂 Estrutura do Projeto

```
.
├── workflows/
│   └── real_estate_research.md    # Documentação do processo
├── tools/
│   ├── crawl_vivareal.py          # [Tool] Web crawler
│   ├── parse_listings.py          # [Tool] HTML parser
│   └── generate_report.py         # [Tool] Report generator
├── data/
│   ├── raw/                       # HTMLs coletados
│   └── processed/                 # JSONs estruturados
├── reports/                       # Excel files gerados
├── run_research.py                # [Agent] Orquestrador principal
├── requirements.txt               # Dependências Python
├── claude.md                      # Instruções do framework WAT
└── README.md                      # Esta documentação
```

---

## 🔧 Uso Avançado

### Executar Tools Individualmente

```bash
# 1. Apenas Crawling
python tools/crawl_vivareal.py --region freguesia-do-o --min-area 40 --max-area 45

# 2. Apenas Parsing (requer HTMLs em data/raw/)
python tools/parse_listings.py --min-area 40 --max-area 45

# 3. Apenas Relatório (requer listings.json)
python tools/generate_report.py --min-count 100
```

### Parâmetros Disponíveis

| Parâmetro | Padrão | Descrição |
|-----------|--------|-----------|
| `--region` | `freguesia-do-o` | Slug da região no VivaReal |
| `--min-area` | `40` | Área mínima (m²) |
| `--max-area` | `45` | Área máxima (m²) |
| `--min-count` | `100` | Quantidade mínima de anúncios |
| `--max-pages` | `10` | Máximo de páginas para crawl |
| `--delay` | `2` | Delay entre requests (segundos) |

---

## ✅ Verificação e Testes

### Checklist de Validação

- [ ] Ambiente Python configurado
- [ ] Dependências instaladas
- [ ] Crawl coleta ≥10 páginas sem erro
- [ ] Parser extrai ≥90% dos anúncios
- [ ] Excel gerado com ≥100 linhas
- [ ] Dados dentro dos filtros (40-45m²)

### Troubleshooting

**Erro: "Nenhum anúncio encontrado"**
- Verifique conexão com internet
- Aumente `--max-pages`
- Teste URL manualmente no navegador

**Erro: "Parsing falhou"**
- VivaReal pode ter mudado estrutura HTML
- Cheque logs em `data/raw/` para debug
- Ajuste seletores em `parse_listings.py`

**Excel com poucos registros**
- Aumente `--max-pages` (15-20)
- Expanda faixa de área (`--min-area 35 --max-area 50`)

---

## 🔒 Boas Práticas

### Segurança
- ✅ Sem credenciais no código (use `.env` se necessário)
- ✅ `.gitignore` protege dados sensíveis
- ✅ Delay entre requests para não sobrecarregar servidor

### Reversibilidade
- ✅ Dados brutos salvos em `data/raw/`
- ✅ Reprocessamento sem novo crawl
- ✅ Git para versionamento de código

### Verificação
- ✅ Logs detalhados em cada fase
- ✅ Validação de dados pré-relatório
- ✅ Estatísticas descritivas automáticas

---

## 📊 Output Exemplo

O Excel gerado contém:

| Link | Valor (R$) | Tamanho (m²) | Valor/m² |
|------|-----------|--------------|----------|
| https://... | R$ 280.000,00 | 42 | R$ 6.666,67 |
| https://... | R$ 295.000,00 | 44 | R$ 6.704,55 |
| ... | ... | ... | ... |

Estatísticas incluídas:
- 📈 Preço médio e mediano
- 📏 Área média
- 💰 Valor/m² médio
- 📊 Min/Max

---

## 🤝 Contribuindo

Este projeto segue o framework WAT:

1. **Adicionar novo workflow**: Criar `.md` em `workflows/`
2. **Adicionar nova tool**: Criar script em `tools/`
3. **Modificar agent**: Editar `run_research.py`

Sempre seguir princípios:
- ✅ Modularidade (uma tool = uma responsabilidade)
- ✅ Verificabilidade (testes claros)
- ✅ Reversibilidade (dados brutos preservados)

---

## 📝 Licença e Avisos

- ⚠️ Uso educacional e de pesquisa
- ⚠️ Respeite os Termos de Uso do VivaReal
- ⚠️ Não use para scraping massivo comercial
- ⚠️ Dados podem estar desatualizados

---

## 📚 Referências

- [CLAUDE.md](claude.md) - Framework WAT completo
- [Workflow Documentation](workflows/real_estate_research.md) - Processo detalhado
- VivaReal: https://www.vivareal.com.br

---

**Desenvolvido com 🤖 Framework WAT (Workflows, Agents, and Tools)**
