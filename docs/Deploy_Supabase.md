# 🚀 Guia Completo de Deploy no Supabase + Render

## 📋 Pré-requisitos

- [ ] Conta no [Supabase](https://supabase.com)
- [ ] Conta no [Render](https://render.com) ou [Railway](https://railway.app)
- [ ] Python 3.11+
- [ ] Node.js 18+ (para Supabase CLI)
- [ ] Git configurado

## Parte 1: Configurar Supabase

### 1.1 Criar Projeto no Supabase

```bash
# Instalar Supabase CLI
npm install -g supabase

# Login
supabase login

# Criar projeto (via dashboard ou CLI)
# https://app.supabase.com/
```

### 1.2 Obter Credenciais

No Dashboard do Supabase → Settings → API:
- `SUPABASE_URL`: https://xxxxx.supabase.co
- `SUPABASE_ANON_KEY`: eyJhbGc...
- `SUPABASE_SERVICE_KEY`: eyJhbGc... (usar com cuidado!)

### 1.3 Migrar Dados

```bash
# Instalar dependências
pip install supabase pandas pyarrow python-dotenv

# Configurar .env
cat > .env.supabase << EOF
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-anon-key
SUPABASE_SERVICE_KEY=sua-service-key
GEMINI_API_KEY=sua-chave-gemini
EOF

# Executar migração
python migrate_parquet_to_supabase.py
```

### 1.4 Configurar RLS (Row Level Security)

No SQL Editor do Supabase:

```sql
-- Habilitar RLS
ALTER TABLE filial_madureira ENABLE ROW LEVEL SECURITY;

-- Política: Permitir leitura para usuários autenticados
CREATE POLICY "Leitura autenticada" ON filial_madureira
    FOR SELECT
    USING (auth.role() = 'authenticated');

-- Política: Permitir acesso via service key
CREATE POLICY "Acesso total via service key" ON filial_madureira
    FOR ALL
    USING (auth.jwt()->>'role' = 'service_role');
```

## Parte 2: Adaptar Código Python

### 2.1 Substituir DataSourceManager

No arquivo `core/data_source_manager.py`, **substituir** por:

```python
from supabase_data_adapter import SupabaseDataManager, get_data_manager

# O resto do código já usa get_data_manager()
```

### 2.2 Atualizar Variáveis de Ambiente

```bash
# .env para produção
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-anon-key
SUPABASE_SERVICE_KEY=sua-service-key
GEMINI_API_KEY=sua-chave-gemini
GEMINI_MODEL_NAME=gemini-2.0-flash-lite
FLASK_ENV=production
SECRET_KEY=seu-secret-key-seguro
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=sua-chave-langsmith
```

### 2.3 Testar Localmente

```bash
# Instalar deps
pip install -r requirements_supabase.txt

# Rodar API
python core/api/run_api.py

# Testar endpoint
curl http://localhost:5000/api/status
```

## Parte 3: Deploy no Render

### 3.1 Preparar Repositório Git

```bash
# Criar repositório
git init
git add .
git commit -m "Preparar deploy Supabase + Render"

# Criar repo no GitHub
gh repo create agent-bi --public --source=. --push
```

### 3.2 Deploy no Render

1. Acesse [Render Dashboard](https://dashboard.render.com/)
2. Click **New** → **Web Service**
3. Conecte seu repositório GitHub
4. Configure:
   - **Name**: agent-bi-api
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements_supabase.txt`
   - **Start Command**: `gunicorn core.api.run_api:app --bind 0.0.0.0:$PORT`
   - **Plan**: Starter ($7/mês)

### 3.3 Configurar Variáveis de Ambiente

No Render → Environment:

```
SUPABASE_URL=https://seu-projeto.supabase.co
SUPABASE_KEY=sua-anon-key
SUPABASE_SERVICE_KEY=sua-service-key
GEMINI_API_KEY=sua-chave-gemini
GEMINI_MODEL_NAME=gemini-2.0-flash-lite
FLASK_ENV=production
SECRET_KEY=gerar-chave-aleatoria
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=sua-chave-langsmith
```

### 3.4 Deploy!

Click **Create Web Service** e aguarde ~5min.

URL final: `https://agent-bi-api.onrender.com`

## Parte 4: Frontend (Opcional)

### Opção A: Streamlit no Render

```bash
# Adicionar ao render.yaml
- type: web
  name: agent-bi-frontend
  env: python
  buildCommand: "pip install streamlit supabase"
  startCommand: "streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0"
```

### Opção B: Next.js na Vercel

```bash
# Criar app Next.js
npx create-next-app@latest agent-bi-frontend --typescript --tailwind

# Instalar Supabase client
npm install @supabase/supabase-js

# Deploy
vercel --prod
```

## 🧪 Testar Produção

```bash
# Teste 1: Status
curl https://agent-bi-api.onrender.com/api/status

# Teste 2: Chat
curl -X POST https://agent-bi-api.onrender.com/api/chat \
  -H "Content-Type: application/json" \
  -d '{"query": "Mostre produtos da categoria brinquedos"}'

# Teste 3: Produto específico
curl https://agent-bi-api.onrender.com/api/products/search?q=teste
```

## 🔐 Segurança

### Adicionar Autenticação (Supabase Auth)

```python
from supabase import create_client
from flask import request

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"error": "Token ausente"}), 401
        
        try:
            token = auth_header.replace('Bearer ', '')
            supabase.auth.get_user(token)
            return f(*args, **kwargs)
        except:
            return jsonify({"error": "Token inválido"}), 401
    
    return decorated

@app.route('/api/chat', methods=['POST'])
@require_auth
def chat():
    # ... código existente
```

## 📊 Monitoramento

### Logs no Render

```bash
# Ver logs em tempo real
render logs -s agent-bi-api --tail
```

### Métricas no Supabase

Dashboard → Database → Performance

## 🔄 CI/CD

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
name: Deploy to Render
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Render
        env:
          RENDER_API_KEY: ${{ secrets.RENDER_API_KEY }}
        run: |
          curl -X POST https://api.render.com/v1/services/$SERVICE_ID/deploys \
            -H "Authorization: Bearer $RENDER_API_KEY"
```

## 💰 Custos Estimados

| Serviço | Plano | Custo/mês |
|---------|-------|-----------|
| Supabase | Free/Pro | $0-$25 |
| Render API | Starter | $7 |
| Render Frontend | Free/Starter | $0-$7 |
| **Total** | | **$7-$39/mês** |

## 🆘 Troubleshooting

### Erro: "Conexão recusada"
```bash
# Verificar se Supabase está acessível
ping seu-projeto.supabase.co

# Testar URL diretamente
curl https://seu-projeto.supabase.co/rest/v1/filial_madureira \
  -H "apikey: SUA-ANON-KEY"
```

### Erro: "Module not found"
```bash
# No Render, verificar logs de build
# Adicionar módulo faltante em requirements_supabase.txt
```

### Performance lenta
```sql
-- Adicionar índices no Supabase
CREATE INDEX idx_descricao_gin ON filial_madureira USING gin(to_tsvector('portuguese', descricao));
CREATE INDEX idx_fabricante_btree ON filial_madureira(fabricante);
```

## ✅ Checklist Final

- [ ] Dados migrados para Supabase PostgreSQL
- [ ] RLS configurado no Supabase
- [ ] Código adaptado para Supabase
- [ ] Variáveis de ambiente configuradas
- [ ] Deploy no Render concluído
- [ ] API testada em produção
- [ ] Autenticação implementada
- [ ] Monitoramento configurado
- [ ] Backup configurado (Supabase Storage)

## 🎉 Próximos Passos

1. **Melhorar Performance**: Adicionar Redis cache
2. **Analytics**: Integrar PostHog ou Mixpanel
3. **Frontend**: Criar interface React/Next.js
4. **Webhooks**: Adicionar notificações
5. **API Docs**: Adicionar Swagger/OpenAPI

---

**Documentação:**
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [Render Python Deploy](https://render.com/docs/deploy-flask)
- [LangChain Supabase](https://python.langchain.com/docs/integrations/vectorstores/supabase)
