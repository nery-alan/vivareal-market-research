# 🚀 Como Enviar para o GitHub

## 📋 Passo a Passo Completo

### Opção 1: Criar Novo Repositório no GitHub (Recomendado)

#### 1. Criar Repositório no GitHub

1. Acesse: https://github.com/new
2. Preencha:
   - **Repository name**: `vivareal-market-research` (ou nome de sua escolha)
   - **Description**: "Agentic workflow for real estate market research using WAT framework"
   - **Visibility**: Escolha Public ou Private
   - **⚠️ IMPORTANTE**: NÃO marque "Add README" (já temos)
   - **⚠️ IMPORTANTE**: NÃO marque "Add .gitignore" (já temos)
   - **⚠️ IMPORTANTE**: NÃO marque "Choose a license" (adicione depois se quiser)
3. Clique em **"Create repository"**

#### 2. Conectar Repositório Local ao GitHub

Copie e execute os comandos abaixo (substitua `SEU_USUARIO` pelo seu username do GitHub):

```bash
# Adicionar remote (substitua SEU_USUARIO)
git remote add origin https://github.com/SEU_USUARIO/vivareal-market-research.git

# Verificar remote
git remote -v

# Renomear branch para main (se necessário)
git branch -M main

# Fazer push inicial
git push -u origin main
```

**Exemplo**:
```bash
# Se seu username for "joaosilva"
git remote add origin https://github.com/joaosilva/vivareal-market-research.git
git push -u origin main
```

#### 3. Autenticação

Quando fizer o push, o GitHub vai pedir autenticação:

**Opção A: Personal Access Token (Recomendado)**
1. Acesse: https://github.com/settings/tokens
2. Clique em "Generate new token" → "Generate new token (classic)"
3. Configure:
   - Note: "Agentic Workflows Push"
   - Expiration: 90 days (ou escolha)
   - Scopes: Marque **"repo"** (full control)
4. Clique em "Generate token"
5. **COPIE O TOKEN** (você não verá novamente!)
6. Quando o git pedir senha, cole o token

**Opção B: SSH (Mais Seguro)**
```bash
# Gerar chave SSH
ssh-keygen -t ed25519 -C "seu_email@example.com"

# Copiar chave pública
cat ~/.ssh/id_ed25519.pub

# Adicionar em: https://github.com/settings/keys
```

Depois use SSH URL:
```bash
git remote set-url origin git@github.com:SEU_USUARIO/vivareal-market-research.git
```

---

### Opção 2: Conectar a Repositório Existente

Se você já tem um repositório criado:

```bash
# Adicionar remote
git remote add origin https://github.com/SEU_USUARIO/NOME_DO_REPO.git

# Verificar
git remote -v

# Push
git push -u origin main
```

---

## 🔍 Verificar Sucesso

Após o push, verifique:

1. **Localmente**:
```bash
git remote -v
# Deve mostrar:
# origin  https://github.com/SEU_USUARIO/vivareal-market-research.git (fetch)
# origin  https://github.com/SEU_USUARIO/vivareal-market-research.git (push)

git log --oneline
# Deve mostrar os 4 commits
```

2. **No GitHub**:
   - Acesse: `https://github.com/SEU_USUARIO/vivareal-market-research`
   - Verifique se aparece:
     - ✅ README.md (documentação)
     - ✅ 4 commits
     - ✅ Estrutura de pastas (workflows/, tools/, etc.)

---

## 📝 Comandos Úteis Futuros

### Fazer Novos Commits e Push

```bash
# 1. Fazer mudanças nos arquivos...

# 2. Adicionar arquivos
git add .

# 3. Commit
git commit -m "Descrição da mudança"

# 4. Push para GitHub
git push
```

### Verificar Status

```bash
# Ver mudanças locais
git status

# Ver histórico
git log --oneline

# Ver diferenças
git diff
```

### Atualizar do GitHub (se trabalhar de outro lugar)

```bash
git pull
```

---

## 🔒 Segurança - Dados Sensíveis

**⚠️ IMPORTANTE**: Antes de fazer push, verifique que dados sensíveis estão protegidos:

```bash
# Verificar .gitignore
cat .gitignore

# Verificar se .env está ignorado (SIM, está!)
git check-ignore .env
# Deve retornar: .env

# Verificar arquivos que serão enviados
git ls-files
```

**Arquivos que NÃO vão para o GitHub** (protegidos pelo .gitignore):
- ✅ `.env` (API keys)
- ✅ `data/raw/*.html` (dados brutos)
- ✅ `data/processed/*.json` (dados processados)
- ✅ `reports/*.xlsx` (relatórios gerados)

**Arquivos que VÃO para o GitHub**:
- ✅ Código fonte (`.py`, `.md`)
- ✅ Configurações (`.gitignore`, `requirements.txt`)
- ✅ Documentação
- ✅ Estrutura de diretórios (pastas vazias com `.gitkeep`)

---

## 🎯 Exemplo Completo

```bash
# 1. Criar repo no GitHub chamado "vivareal-market-research"

# 2. Conectar (substitua SEU_USUARIO)
git remote add origin https://github.com/SEU_USUARIO/vivareal-market-research.git

# 3. Verificar
git remote -v

# 4. Push
git push -u origin main

# 5. Digite seu username do GitHub quando solicitado
# 6. Cole o Personal Access Token quando pedir senha

# ✅ Sucesso! Acesse:
# https://github.com/SEU_USUARIO/vivareal-market-research
```

---

## 🐛 Troubleshooting

### Erro: "remote origin already exists"
```bash
# Remover remote existente
git remote remove origin

# Adicionar novamente
git remote add origin https://github.com/SEU_USUARIO/vivareal-market-research.git
```

### Erro: "Authentication failed"
- Use Personal Access Token, não senha do GitHub
- Token deve ter permissão "repo"
- Gere novo em: https://github.com/settings/tokens

### Erro: "Permission denied (publickey)"
- Configure SSH: https://docs.github.com/en/authentication/connecting-to-github-with-ssh
- Ou use HTTPS ao invés de SSH

### Erro: "refusing to merge unrelated histories"
```bash
# Se o repo remoto tem conteúdo diferente
git pull origin main --allow-unrelated-histories
git push -u origin main
```

---

## 📚 Recursos

- **GitHub Docs**: https://docs.github.com
- **Git Cheat Sheet**: https://education.github.com/git-cheat-sheet-education.pdf
- **Personal Access Tokens**: https://github.com/settings/tokens
- **SSH Keys**: https://github.com/settings/keys

---

## 🎉 Pronto!

Depois do push, você terá:
- ✅ Código versionado no GitHub
- ✅ Backup seguro na nuvem
- ✅ Possibilidade de colaborar
- ✅ Histórico de commits público/privado
- ✅ README bonito renderizado

**Seu projeto estará em**:
```
https://github.com/SEU_USUARIO/vivareal-market-research
```

Compartilhe o link! 🚀
