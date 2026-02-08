# 🔥 Configuração do Firecrawl

O VivaReal bloqueia requests simples com erro 403 (Forbidden). Para contornar isso, usamos **Firecrawl**.

## Opções de Configuração

### Opção 1: Firecrawl API (Recomendado para Produção)

1. **Obter API Key**:
   - Acesse: https://firecrawl.dev
   - Crie uma conta e gere uma API key

2. **Configurar Variável de Ambiente**:
   ```bash
   # Copiar template
   cp .env.example .env

   # Editar .env e adicionar:
   FIRECRAWL_API_KEY=sua_api_key_aqui
   ```

3. **Testar**:
   ```bash
   python tools/firecrawl_integration.py --test-url "https://www.vivareal.com.br"
   ```

4. **Usar no Workflow**:
   ```bash
   # O run_research.py detectará automaticamente a API key
   python run_research.py --use-firecrawl
   ```

---

### Opção 2: Firecrawl MCP Server (Ideal para Claude Code)

Se você já configurou o Firecrawl MCP:

1. **Verificar Status**:
   ```bash
   # No Claude Code, verifique se o servidor está ativo
   # Você mencionou ter: mcpServer.mcp.config.usrlocal.firecrawl
   ```

2. **Usar via MCP**:
   - O agent Claude pode chamar diretamente o MCP Firecrawl
   - Não requer API key
   - Mais integrado com o fluxo do Claude Code

3. **Documentação**:
   - Firecrawl MCP: https://github.com/anthropics/anthropic-quickstarts/tree/main/mcp/firecrawl

---

### Opção 3: Playwright (Sem Dependência Externa)

Para uso completamente local sem API externa:

1. **Instalar Playwright**:
   ```bash
   pip install playwright
   playwright install chromium
   ```

2. **Implementar crawler com Playwright**:
   - Emula um navegador real
   - Mais lento, mas funciona offline
   - Código em: `tools/playwright_crawler.py` (a implementar)

---

## Testando a Configuração

### Teste 1: Verificar Firecrawl API
```bash
# Se você tem API key configurada
python tools/firecrawl_integration.py --region "freguesia-do-o" --max-pages 2
```

### Teste 2: Workflow Completo
```bash
# Com Firecrawl
python run_research.py --use-firecrawl --max-pages 5

# Sem Firecrawl (vai falhar no VivaReal)
python run_research.py --max-pages 5
```

---

## Troubleshooting

### Erro: "API key not configured"
- Certifique-se que `FIRECRAWL_API_KEY` está no arquivo `.env`
- Ou passe diretamente: `--api-key YOUR_KEY`

### Erro: "Rate limit exceeded"
- Firecrawl tem limites de uso no plano gratuito
- Reduza `--max-pages`
- Ou aguarde reset do rate limit

### Erro: "MCP server not found"
- Verifique configuração MCP em `~/.config/claude/mcp_servers.json`
- Reinicie o servidor MCP
- Veja logs em: `~/.config/claude/logs/`

---

## Próximos Passos

Depois de configurar o Firecrawl:

1. **Rodar Pesquisa Completa**:
   ```bash
   python run_research.py --use-firecrawl --max-pages 15
   ```

2. **Analisar Resultados**:
   ```bash
   open reports/vivareal_freguesia_do_o_*.xlsx
   ```

3. **Automatizar** (opcional):
   - Criar cron job para pesquisas semanais
   - Comparar tendências de preço ao longo do tempo

---

## Custos Estimados

**Firecrawl API**:
- Plano gratuito: ~500 scrapes/mês
- Pro: $49/mês (10,000 scrapes)
- Para 100 anúncios (~10 páginas): ~10 scrapes

**Alternativas Gratuitas**:
- Playwright: Totalmente gratuito, mas mais lento
- MCP local: Gratuito se você gerenciar o servidor

---

**📚 Documentação**:
- Firecrawl: https://docs.firecrawl.dev
- Firecrawl MCP: https://github.com/mendableai/firecrawl-mcp-server
