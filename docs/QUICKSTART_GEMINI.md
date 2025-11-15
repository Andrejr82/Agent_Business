# ⚡ Guia Rápido - Gemini LLM Setup

> **TL;DR** (Too Long; Didn't Read): Tudo já está configurado. Teste com `python scripts/test_llm_setup.py` e use!

---

## 🎯 Em 60 Segundos

```bash
# 1. Validar setup (30 segundos)
python scripts/test_llm_setup.py

# 2. Iniciar app (10 segundos)
streamlit run streamlit_app.py

# 3. Testar no chat (20 segundos)
# → Digite: "Olá!"
# → Resposta vem do Gemini ✅
```

**Pronto!** A configuração está funcionando.

---

## ✅ O Que Está Pronto

- ✅ **Adaptador Gemini** - `core/llm_gemini_adapter.py`
- ✅ **Factory LLM** - `core/llm_factory.py`
- ✅ **Configurações** - `core/config/config.py` atualizado
- ✅ **Chaves de API** - `.env` preenchido (Gemini)
- ✅ **Documentação** - 5 documentos completos
- ✅ **Testes** - Script automatizado pronto
- ✅ **Dependências** - `google-generativeai` adicionado

---

## 📋 Variáveis de Ambiente

```env
# Ativo agora
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSyAVslwdt_g_ChwaonlHkCvn_KZ9RmddtYs
```

---

## 🔄 No Código

```python
# Sempre funciona assim (automático)
from core.llm_factory import LLMFactory

adapter = LLMFactory.get_adapter()  # Usa .env (LLM_PROVIDER)
response = adapter.get_completion(messages)
print(response)
```

---

## 🆘 Problemas Comuns

| Problema | Solução |
|----------|---------|
| Teste falha | `python scripts/test_llm_setup.py` para debug |
| Módulo não encontrado | `pip install -r requirements.txt` |
| App lenta | Normal 1ª vez (30-60s) |

---

## 📚 Documentação

**Não sabe por onde começar?**

- 👉 **Rápido:** [RESUMO_VISUAL_GEMINI.txt](RESUMO_VISUAL_GEMINI.txt)
- 👉 **Médio:** [RESUMO_CONFIGURACAO_GEMINI.md](RESUMO_CONFIGURACAO_GEMINI.md)
- 👉 **Completo:** [CONFIGURACAO_GEMINI.md](CONFIGURACAO_GEMINI.md)
- 👉 **Técnico:** [RELATORIO_IMPLEMENTACAO_GEMINI.md](RELATORIO_IMPLEMENTACAO_GEMINI.md)
- 👉 **Índice:** [INDICE_GEMINI.md](INDICE_GEMINI.md)

---

## 🚀 Começar Agora

```bash
# Terminal Windows (PowerShell)
python scripts/test_llm_setup.py
streamlit run streamlit_app.py

# Terminal Mac/Linux
python3 scripts/test_llm_setup.py
streamlit run streamlit_app.py
```

---

## ✨ Próximas Melhorias (Opcional)

- [ ] Cache de respostas
- [ ] Dashboard de monitoramento
- [ ] Mais provedores (DeepSeek, Claude)
- [ ] Rate limiting
- [ ] Métricas

---

**Status:** ✅ **PRONTO PARA USAR**

**Data:** 14 de novembro de 2025