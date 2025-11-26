
# Script de Configuração Automática do Projeto
# Autor: Agente BI

Write-Host "🚀 Iniciando configuração do Agente BI..." -ForegroundColor Cyan

# 1. Resolver conflitos do Git e Enviar Correção
Write-Host "`n🔧 Corrigindo estado do Git e enviando fix para Cloud..." -ForegroundColor Yellow
try {
    # Descarta alterações locais conflitantes (assume que o repo tem a verdade)
    git checkout HEAD .streamlit/secrets.toml.example core/agents/tool_agent.py core/config/config.py 2>$null
    
    # Adiciona a correção do __init__.py
    git add core/agents/__init__.py
    
    # Tenta comitar (pode falhar se não houver mudanças, o que é ok)
    git commit -m "fix: remove eager import of ToolAgent to prevent startup crash" 2>$null
    
    # Envia para o GitHub
    git push origin master
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Correção enviada para o Streamlit Cloud com sucesso!" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Aviso: Falha ao enviar para o GitHub. Verifique as permissões." -ForegroundColor Red
    }
} catch {
    Write-Host "⚠️ Erro ao manipular Git: $_" -ForegroundColor Red
}

# 2. Configurar Ambiente Virtual Local
Write-Host "`n📦 Configurando ambiente virtual (.venv)..." -ForegroundColor Yellow

# Tentar matar processos Python que possam estar travando a pasta
Write-Host "   Finalizando TODOS os processos Python..."
taskkill /F /IM python.exe /T 2>$null
Start-Sleep -Seconds 2

if (Test-Path ".venv") {
    Write-Host "   Removendo .venv antigo..."
    try {
        Remove-Item -Recurse -Force .venv -ErrorAction Stop
    } catch {
        Write-Host "❌ ERRO: Não foi possível apagar a pasta .venv." -ForegroundColor Red
        Write-Host "   Motivo: O arquivo 'python.exe' ainda está em uso pelo sistema."
        Write-Host "   SOLUÇÃO: Feche e abra novamente o VS Code para liberar o arquivo."
        exit
    }
}

Write-Host "   Criando novo .venv..."
python -m venv .venv

if (-not (Test-Path ".venv")) {
    Write-Host "❌ Erro: Falha ao criar .venv. Verifique se o Python está no PATH." -ForegroundColor Red
    exit
}

# 3. Instalar Dependências
Write-Host "`n⬇️ Instalando dependências (isso pode demorar um pouco)..." -ForegroundColor Yellow
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\pip install -r requirements.txt

if ($LASTEXITCODE -eq 0) {
    Write-Host "`n✅ Instalação concluída com sucesso!" -ForegroundColor Green
    Write-Host "`n🎉 Para iniciar o app, execute:" -ForegroundColor Cyan
    Write-Host ".venv\Scripts\activate" -ForegroundColor White
    Write-Host "streamlit run streamlit_app.py" -ForegroundColor White
} else {
    Write-Host "`n❌ Houve um erro na instalação das dependências." -ForegroundColor Red
}
