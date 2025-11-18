# 🚀 Guia de Deploy no Streamlit Cloud

## 📋 Pré-requisitos

- [x] Conta no GitHub
- [x] Conta no Streamlit Cloud (https://streamlit.io/cloud)
- [x] Chave de API do Google Gemini
- [x] Repositório Git configurado

---

## 🎯 PASSO A PASSO COMPLETO

### PASSO 1: Preparar Repositório Git

#### 1.1 Verificar arquivos necessários

```bash
# Verificar se existem:
ls -la requirements.txt
ls -la streamlit_app.py
ls -la .streamlit/config.toml
```

✅ **Todos os arquivos necessários já estão prontos!**

#### 1.2 Criar/atualizar .gitignore

```bash
# Verificar .gitignore
cat .gitignore
```

Se não existir, criar com:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
.venv/
venv/
ENV/

# Streamlit
.streamlit/secrets.toml

# Dados sensíveis
.env
*.db
*.sqlite

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Cache
.ruff_cache/
.pytest_cache/
```

#### 1.3 Commitar e fazer push

```bash
# Adicionar todos os arquivos
git add .

# Commit
git commit -m "feat: Preparar para deploy no Streamlit Cloud com melhorias de beleza"

# Push para GitHub
git push origin master
```

---

### PASSO 2: Configurar Streamlit Cloud

#### 2.1 Acessar Streamlit Cloud

1. Ir para: https://streamlit.io/cloud
2. Fazer login com GitHub
3. Click em "**New app**"

#### 2.2 Configurar App

**Configurações básicas:**
- **Repository:** `seu-usuario/agente-bi-caculinha-refatoracao-jules`
- **Branch:** `master` (ou `main`)
- **Main file path:** `streamlit_app.py`
- **App URL:** `agente-beleza-bi` (ou nome de sua escolha)

#### 2.3 Configurar Secrets

Click em "**Advanced settings**" → "**Secrets**"

Cole o conteúdo abaixo (substituindo pelos valores reais):

```toml
# Secrets do Streamlit Cloud
GEMINI_API_KEY = "SUA_CHAVE_GEMINI_REAL"
GEMINI_MODEL_NAME = "gemini-2.0-flash-lite"

# Opcional: SQL Server
DB_SERVER = ""
DB_DATABASE = ""
DB_USER = ""
DB_PASSWORD = ""
DB_PORT = "1433"
DB_DRIVER = "ODBC Driver 17 for SQL Server"

# App
DEBUG = "false"
SECRET_KEY = "gere_uma_chave_aleatoria_aqui"
DEMO_MODE = "false"

# LangSmith (opcional)
LANGCHAIN_TRACING_V2 = "false"
LANGCHAIN_API_KEY = ""
LANGCHAIN_PROJECT = "caculinha-bi-project"
```

**Como gerar SECRET_KEY:**
```python
import secrets
print(secrets.token_hex(32))
```

#### 2.4 Configurar Plano

**IMPORTANTE:** Escolher plano adequado:

| Plano | Custo | RAM | CPU | Recomendação |
|-------|-------|-----|-----|--------------|
| Community | $0 | 1GB | Compartilhado | ⚠️ Apenas testes |
| **Starter** | **$20/mês** | **2GB** | **Dedicado** | ✅ **RECOMENDADO** |
| Team | $60/mês | 4GB | Dedicado | Para equipes |

**Por que Starter?**
- ✅ RAM suficiente para Parquet (698 produtos)
- ✅ Performance adequada
- ✅ App sempre online (não hiberna)
- ✅ Suporte técnico

#### 2.5 Deploy!

1. Click em "**Deploy!**"
2. Aguardar 2-5 minutos
3. App estará disponível em: `https://agente-beleza-bi.streamlit.app`

---

### PASSO 3: Configuração Pós-Deploy

#### 3.1 Limpar Dados (Primeira vez)

Após deploy, rodar script de limpeza:

**Opção A: Via interface**
1. Acessar app
2. Fazer login (usar credenciais definidas)
3. Ir em configurações e rodar limpeza

**Opção B: Via terminal local e upload**
```bash
# Localmente
python scripts/limpar_dados_beleza.py

# Fazer commit do arquivo limpo
git add data/parquet/Filial_Madureira_LIMPO.parquet
git commit -m "chore: Adicionar dados limpos"
git push

# Streamlit Cloud irá atualizar automaticamente
```

#### 3.2 Configurar Usuários

Criar usuários de teste no sistema de autenticação:

```python
# Em um script ou via interface admin
from core.database import sqlserver_auth
sqlserver_auth.criar_usuario("cliente", "senha_segura", "user")
```

#### 3.3 Testar Funcionalidades

- [ ] Login funciona
- [ ] Dashboard carrega
- [ ] Filtros funcionam
- [ ] Gráficos renderizam
- [ ] Alertas aparecem
- [ ] Chat responde

---

### PASSO 4: Monitoramento e Manutenção

#### 4.1 Logs

Acessar logs em tempo real:
1. Streamlit Cloud Dashboard
2. Click no app
3. Abrir "**Logs**"

#### 4.2 Métricas de Uso

Streamlit Cloud fornece:
- Número de visualizações
- Tempo de sessão médio
- Uptime

#### 4.3 Atualizações

Para atualizar o app:

```bash
# Fazer mudanças localmente
# ...

# Commit e push
git add .
git commit -m "feat: Nova funcionalidade X"
git push

# Streamlit Cloud atualiza automaticamente!
```

#### 4.4 Reboot Manual

Se necessário reiniciar:
1. Streamlit Cloud Dashboard
2. Click no app
3. Menu (⋮) → "**Reboot app**"

---

## 🔧 Troubleshooting

### Problema: App não inicia

**Solução:**
1. Verificar logs
2. Checar se secrets estão configurados
3. Verificar requirements.txt

### Problema: "Module not found"

**Solução:**
```bash
# Adicionar módulo faltante em requirements.txt
echo "modulo-faltante==versao" >> requirements.txt
git commit -am "fix: Adicionar dependência"
git push
```

### Problema: Performance lenta

**Solução:**
1. Verificar se arquivo limpo está sendo usado
2. Conferir cache @st.cache_data
3. Considerar upgrade para plano Team

### Problema: App "hiberna" (Community Plan)

**Solução:**
- Upgrade para Starter ($20/mês)
- Ou aceitar que hiberna após inatividade

### Problema: Secrets não funcionam

**Solução:**
1. Ir em App settings → Secrets
2. Verificar formatação TOML
3. Salvar e rebootar app

---

## 📊 Custos Mensais Estimados

```
Streamlit Cloud Starter:  $20.00
Google Gemini API:        $ 5-15 (média $10)
────────────────────────────────────
TOTAL:                    $30.00/mês
```

**Comparado com:**
- Render + Postgres: $7-35/mês (mas requer mais configuração)
- Heroku: $25-50/mês
- AWS/GCP: $50-100/mês (requer DevOps)

---

## ✅ Checklist Final de Deploy

### Antes do Deploy
- [x] Arquivo limpo gerado (`Filial_Madureira_LIMPO.parquet`)
- [x] requirements.txt atualizado
- [x] .streamlit/config.toml criado
- [x] .gitignore configurado
- [x] Código testado localmente

### Durante o Deploy
- [ ] Repositório no GitHub
- [ ] App criado no Streamlit Cloud
- [ ] Secrets configurados
- [ ] Plano Starter selecionado
- [ ] Deploy bem-sucedido

### Após o Deploy
- [ ] App acessível via URL
- [ ] Login funciona
- [ ] Dashboards carregam
- [ ] Performance < 5s
- [ ] Cliente testou e aprovou

---

## 🎓 Recursos Adicionais

**Documentação Oficial:**
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Deploy Guide](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app)
- [Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management)

**Vídeos Tutoriais:**
- [Deploying to Streamlit Cloud](https://www.youtube.com/watch?v=HKoOBiAaHGg)

**Comunidade:**
- [Streamlit Forum](https://discuss.streamlit.io/)
- [GitHub Issues](https://github.com/streamlit/streamlit/issues)

---

## 🆘 Suporte

**Para problemas técnicos:**
1. Ver logs no Streamlit Cloud
2. Consultar `CLAUDE.md` para arquitetura
3. Consultar `PLANO_MELHORIAS_BELEZA.md` para funcionalidades
4. Abrir issue no GitHub (se repositório público)

**Contato Streamlit:**
- Email: support@streamlit.io
- Forum: https://discuss.streamlit.io/

---

## 🚀 Próximos Passos Após Deploy

1. **Compartilhar URL com cliente**
2. **Treinar cliente** no uso (ver documentação)
3. **Monitorar uso** primeiros dias
4. **Coletar feedback**
5. **Iterar melhorias** conforme necessário

**URL do App:**
```
https://[seu-app-name].streamlit.app
```

Compartilhe esta URL com seu cliente do setor de beleza! 💄✨
