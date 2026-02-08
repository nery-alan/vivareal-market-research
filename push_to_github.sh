#!/bin/bash
# Script para fazer push para o GitHub
# Uso: ./push_to_github.sh SEU_USUARIO NOME_DO_REPO

if [ $# -lt 2 ]; then
    echo "❌ Uso: ./push_to_github.sh SEU_USUARIO NOME_DO_REPO"
    echo ""
    echo "Exemplo:"
    echo "  ./push_to_github.sh nery-alan vivareal-market-research"
    exit 1
fi

GITHUB_USER=$1
REPO_NAME=$2

echo "🔍 Verificando repositório local..."
git remote -v

if git remote | grep -q "origin"; then
    echo "⚠️  Remote 'origin' já existe. Removendo..."
    git remote remove origin
fi

echo ""
echo "🔗 Conectando ao GitHub..."
echo "   URL: https://github.com/$GITHUB_USER/$REPO_NAME.git"
git remote add origin https://github.com/$GITHUB_USER/$REPO_NAME.git

echo ""
echo "✅ Remote configurado:"
git remote -v

echo ""
echo "📤 Fazendo push para GitHub..."
echo "   Branch: main"
echo ""
git push -u origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Sucesso! Seu projeto está no GitHub:"
    echo "   🔗 https://github.com/$GITHUB_USER/$REPO_NAME"
    echo ""
    echo "📊 Commits enviados:"
    git log --oneline
else
    echo ""
    echo "❌ Erro ao fazer push. Verifique:"
    echo "   1. Repositório foi criado no GitHub?"
    echo "   2. Você tem permissão de push?"
    echo "   3. Token/senha está correto?"
    echo ""
    echo "💡 Dica: Use Personal Access Token como senha"
    echo "   Gere em: https://github.com/settings/tokens"
fi
