#!/bin/bash
# Smoke test para Fase 2 - Headers de Segurança

BASE_URL="${1:-http://127.0.0.1:5004}"

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║         SMOKE TEST - HEADERS DE SEGURANÇA (FASE 2)               ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo
echo "Testando: $BASE_URL"
echo

# Teste 1: Servidor responde
echo "[1/4] Verificando se o servidor está UP..."
if curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/" | grep -q "200\|302\|401"; then
    echo "  ✅ Servidor respondendo"
else
    echo "  ❌ Servidor não responde"
    exit 1
fi

# Teste 2: Headers de segurança
echo "[2/4] Verificando headers de segurança..."
HEADERS=$(curl -sIL "$BASE_URL/login")

if echo "$HEADERS" | grep -q "X-Frame-Options"; then
    echo "  ✅ X-Frame-Options presente"
else
    echo "  ❌ X-Frame-Options ausente"
fi

if echo "$HEADERS" | grep -q "X-Content-Type-Options"; then
    echo "  ✅ X-Content-Type-Options presente"
else
    echo "  ❌ X-Content-Type-Options ausente"
fi

if echo "$HEADERS" | grep -q "Referrer-Policy"; then
    echo "  ✅ Referrer-Policy presente"
else
    echo "  ❌ Referrer-Policy ausente"
fi

if echo "$HEADERS" | grep -q "Content-Security-Policy"; then
    echo "  ✅ Content-Security-Policy presente"
else
    echo "  ❌ Content-Security-Policy ausente"
fi

# Teste 3: Rate Limiting
echo "[3/4] Verificando rate limiting..."
if echo "$HEADERS" | grep -q "X-RateLimit"; then
    echo "  ✅ Rate limiting ativo"
else
    echo "  ⚠️  Rate limiting headers não visíveis (pode estar ativo)"
fi

# Teste 4: CSRF
echo "[4/4] Verificando CSRF protection..."
if curl -s "$BASE_URL/login" | grep -q "csrf_token"; then
    echo "  ✅ CSRF tokens presentes"
else
    echo "  ⚠️  CSRF tokens não visíveis no HTML"
fi

echo
echo "════════════════════════════════════════════════════════════════════"
echo "✨ SMOKE TEST CONCLUÍDO ✨"
echo "════════════════════════════════════════════════════════════════════"
