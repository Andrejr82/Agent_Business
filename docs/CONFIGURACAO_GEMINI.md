# 🚀 Configuração do Google Gemini API

## 📋 Resumo

O projeto Caçulinha BI agora suporta múltiplos provedores de LLM (Large Language Models). Neste guia, você aprenderá a configurar e usar o **Google Gemini** como provedor LLM principal.

---

## 🔧 Pré-requisitos

1. **Conta Google** - Necessária para acessar Google AI Studio
2. **Chave API do Gemini** - Gratuita na maioria dos casos
3. **Python 3.9+** - Versão recomendada
4. **Acesso ao projeto** - Arquivo `.env` pronto

---

## 📝 Passo 1: Obter Chave API do Gemini

### 1.1 Acessar Google AI Studio

1. Visite: **https://aistudio.google.com/app/apikey**
2. Faça login com sua conta Google
3. Clique em "Create API Key" → "Create API key in new project"

### 1.2 Copiar a Chave

- A chave será exibida em tela (ex: `AIza...`)
- ⚠️ **NÃO compartilhe** esta chave
- Guarde-a com segurança

---

## ⚙️ Passo 2: Configurar o Projeto

### 2.1 Atualizar Arquivo `.env`

Edite o arquivo `.env` na raiz do projeto:

```env
# ===========================
# LLM Provider Selection
# ===========================

# Selecione o provedor (gemini)
LLM_PROVIDER=gemini

# ===========================
# Gemini Configuration
# ===========================

GEMINI_API_KEY=sua-chave-api-aqui
GEMINI_MODEL_NAME=gemini-pro
```

### 2.2 Instalar Dependências

```bash
# Se ainda não instalou
pip install -r requirements.txt

# Ou instale apenas o Gemini
pip install google-generativeai>=0.7.0
```

---

## 🧪 Passo 3: Testar a Configuração

### 3.1 Verificar Disponibilidade

Execute este script Python:

```python
from core.llm_factory import LLMFactory

# Verificar provedores disponíveis
providers = LLMFactory.get_available_providers()
print("Provedores disponíveis:", providers)

# Tentar obter adaptador
try:
    adapter = LLMFactory.get_adapter()
    print(f"✅ Adaptador inicializado: {type(adapter).__name__}")
except Exception as e:
    print(f"❌ Erro: {e}")
```

### 3.2 Teste Simples

```python
from core.llm_factory import LLMFactory

adapter = LLMFactory.get_adapter()

messages = [
    {"role": "user", "content": "Olá! Quem você é?"}
]

response = adapter.get_completion(messages)
print(response)
```

---

## 🚀 Iniciar a Aplicação

### Com Streamlit:

```bash
streamlit run streamlit_app.py
```

### Com FastAPI:

```bash
python core/main.py
# ou
uvicorn core.main:app --reload
```

---

## 📊 Modelos Disponíveis

| Modelo | Descrição | Gratuito |
|--------|-----------|----------|
| `gemini-pro` | Modelo versátil de propósito geral | ✅ Sim |
| `gemini-pro-vision` | Com suporte a imagens | ✅ Sim |
| `gemini-1.5-pro` | Modelo mais avançado | ⚠️ Limitado |

**Altere em `.env`:**

```env
GEMINI_MODEL_NAME=gemini-pro-vision
```

---

## 🔄 Alternar Entre Provedores

### De OpenAI para Gemini:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=sua-chave-api-aqui
```

---

## ⚠️ Solução de Problemas

### ❌ Erro: "GEMINI_API_KEY não configurada"

**Solução:**
1. Verifique se `.env` existe na raiz do projeto
2. Confirme que `GEMINI_API_KEY` está preenchida (não vazia)
3. Reinicie a aplicação

### ❌ Erro: "google-generativeai não está instalado"

**Solução:**
```bash
pip install google-generativeai>=0.7.0
```

### ❌ Erro: "API Key inválida ou expirada"

**Solução:**
1. Visite https://aistudio.google.com/app/apikey
2. Regenere a chave
3. Atualize em `.env`

### ❌ Aplicação carregando lentamente

**Possível causa:** Primeiro uso do Gemini (modelo sendo baixado)

**Solução:**
- Aguarde a primeira inicialização
- Use `GEMINI_MODEL_NAME=gemini-pro` (padrão, mais rápido)

---

## 📈 Limites e Quotas

### Gemini API (Gratuito):

- **Requisições por minuto (RPM):** 60
- **Tokens por minuto (TPM):** 1.000.000 (1M)
- **Requisições por dia:** Ilimitado

### Para Produção:

1. Considere plano pago para maior quota
2. Implemente rate limiting na aplicação
3. Monitore uso em https://console.cloud.google.com

---

## 🔐 Segurança

### ✅ Boas Práticas:

- ✅ Nunca commite `.env` com chaves reais
- ✅ Use `.env.example` como template
- ✅ Armazene chaves em secrets manager (prod)
- ✅ Rode aplicação com permissões mínimas

### 📁 Exemplo `.gitignore`:

```
.env
.env.local
*.pem
*.key
```

---

## 📚 Referências

- [Google AI Studio](https://aistudio.google.com)
- [Documentação Gemini API](https://ai.google.dev/tutorials)
- [Google Generative AI Python SDK](https://github.com/google/generative-ai-python)

---

## 💡 Dicas Úteis

### 1. Usar Fallback Automático

Se quiser fallback automático (Gemini):

```python
# Em core/llm_factory.py, o factory já implementa isso
adapter = LLMFactory.get_adapter()
# Tenta Gemini primeiro
```

### 2. Monitorar Uso

```python
from core.config.config import Config

print(f"Provider: {Config().LLM_PROVIDER}")
print(f"Modelo: {Config().GEMINI_MODEL_NAME}")
```

### 3. Testar com Curl

```bash
# Se implementar endpoint FastAPI
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Olá", "provider": "gemini"}'
```

---

## ✅ Checklist de Configuração

- [ ] Chave API obtida em https://aistudio.google.com/app/apikey
- [ ] `.env` atualizado com `GEMINI_API_KEY`
- [ ] `LLM_PROVIDER=gemini` configurado
- [ ] `google-generativeai` instalado (`pip install -r requirements.txt`)
- [ ] Aplicação testada e funcionando
- [ ] Logging visualizado (DEBUG mode para mais detalhe)
- [ ] `.env` não commitado no Git

---

**Status:** ✅ Gemini configurado e pronto para uso!