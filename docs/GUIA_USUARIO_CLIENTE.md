# 💄 Guia do Usuário - Agente BI para Beleza

## 👋 Bem-vindo!

Este guia vai te ensinar a usar seu novo sistema de Business Intelligence para análise de dados do setor de beleza.

---

## 🎯 O Que Este Sistema Faz?

O **Agente BI de Beleza** é seu assistente inteligente para tomar decisões baseadas em dados. Com ele você pode:

✅ Fazer perguntas em linguagem natural sobre seus produtos
✅ Ver dashboards interativos com gráficos
✅ Receber alertas automáticos de problemas
✅ Filtrar dados por categoria, fabricante, margem
✅ Analisar sazonalidade de vendas
✅ Identificar produtos em ruptura

---

## 🚀 Como Começar

### 1. Acessar o Sistema

**URL:** `https://seu-app.streamlit.app` (substituir pela URL real)

### 2. Fazer Login

1. Digite seu **usuário**
2. Digite sua **senha**
3. Click em "**Entrar**"

![Login Screen](https://via.placeholder.com/600x300?text=Tela+de+Login)

### 3. Tela Principal

Após login, você verá:

- **🗨️ Chat com o Agente:** À direita
- **🔍 Filtros:** Na barra lateral esquerda
- **📊 Páginas:** No menu lateral
  - Dashboard
  - Monitoramento
  - Área do Comprador
  - **Dashboard KPIs Beleza** ← NOVO!
  - Gerenciar Catálogo

---

## 💬 Usando o Chat Inteligente

### Como Fazer Perguntas

Digite perguntas em **português natural**, como se estivesse falando com uma pessoa:

#### ✅ Exemplos de Perguntas Boas

**Sobre produtos específicos:**
```
Qual o preço do produto 719445?
Me mostre os dados do item 100
Qual a margem do produto X?
```

**Sobre categorias:**
```
Liste os produtos da categoria ESMALTES
Quantos produtos tenho de MAQUIAGEM?
Quais categorias têm mais estoque?
```

**Gráficos:**
```
Mostre um gráfico de vendas para o produto 610403
Crie um gráfico de pizza das categorias
Quero ver a evolução mensal de vendas
```

**Análises:**
```
Quais produtos têm margem acima de 30%?
Liste os 10 produtos mais vendidos
Mostre produtos em ruptura de estoque
```

#### ❌ Evite Perguntas Assim

```
❌ sql select * from...  (não escreva SQL)
❌ mostre tudo  (seja específico)
❌ ???  (seja claro)
```

### Tempo de Resposta

⏱️ **Esperado:** 2-5 segundos
🐌 **Se demorar mais:** Tente recarregar a página

---

## 📊 Navegando pelo Dashboard de KPIs

### Acessar

1. Menu lateral → **Dashboard KPIs Beleza**

### O Que Você Verá

#### 📈 Cards de KPIs (Topo)

- **Total de Produtos:** Quantos SKUs você tem
- **Valor Estoque:** Quanto vale seu estoque
- **Margem Média:** Lucro médio dos produtos
- **Produtos em Ruptura:** Produtos sem estoque

#### 📑 Abas de Análise

**1. Categorias**
- Top 10 categorias por valor de estoque
- Gráfico de barras colorido por margem
- Tabela detalhada

**2. Margem & Rentabilidade**
- Distribuição de margem (histograma)
- Margem por categoria (box plot)
- Top 5 produtos com maior/menor margem

**3. Sazonalidade**
- Vendas mensais (gráfico de linha)
- Identificação de pico e baixa
- Índice de sazonalidade

**4. Fabricantes**
- Participação no estoque (pizza)
- Quantidade de produtos por fabricante
- Tabela completa

---

## 🔍 Usando Filtros Interativos

### Onde Estão

**Barra lateral esquerda** → Seção "🔍 Filtros de Dados"

### Tipos de Filtros

#### 1. Categorias (GRUPO)

- Click em **📦 Categorias**
- Selecione uma ou mais categorias
- Marque "Mostrar todas" se precisar de mais opções

**Uso:** Ver apenas produtos de ESMALTES, por exemplo

#### 2. Fabricantes

- Click em **🏭 Fabricantes**
- Selecione um ou mais fabricantes
- Mostra top 20 por padrão

**Uso:** Analisar apenas produtos de um fornecedor

#### 3. Margem de Lucro

- Click em **💰 Margem de Lucro**
- Arraste o slider para definir margem mínima

**Uso:** Ver apenas produtos com margem >= 25%

#### 4. Estoque

- Click em **📊 Estoque**
- Defina estoque mínimo e máximo

**Uso:** Ver produtos com estoque entre 10 e 100 unidades

#### 5. Status

- ☑️ **Apenas em estoque:** Mostra só produtos com SALDO > 0
- ☑️ **Apenas com vendas:** Produtos que venderam no ano

### Limpar Filtros

Click no botão **🔄 Limpar Filtros** (barra lateral)

### Análises Rápidas

Botões no topo do dashboard:

- **🔴 Ruptura:** Produtos sem estoque
- **⚠️ Estoque Baixo:** Produtos com pouco estoque
- **💰 Alta Margem:** Produtos lucrativos
- **📉 Baixa Margem:** Produtos com margem abaixo da média
- **🔄 Resetar:** Limpar tudo

---

## ⚠️ Entendendo os Alertas

### O Que São

Alertas automáticos identificam problemas e oportunidades em seus dados.

### Tipos de Alertas

#### 🚨 CRÍTICO (Vermelho)
**Margem Negativa**
- Produtos sendo vendidos abaixo do custo
- **Ação:** Corrigir preço URGENTEMENTE

#### ⚠️ ALTA (Laranja)
**Ruptura de Estoque**
- Produtos sem estoque disponível
- **Ação:** Reposição urgente

**Margem Baixa**
- Produtos com margem < 15%
- **Ação:** Revisar precificação

#### 📊 MÉDIA (Amarelo)
**Estoque Excessivo**
- Produtos com > 90 dias de cobertura
- **Ação:** Considerar promoção

#### ℹ️ BAIXA (Azul)
**Sem Vendas**
- Produtos sem venda em 3+ meses
- **Ação:** Avaliar descontinuação

### Como Ver Alertas

Alertas aparecem automaticamente no Dashboard KPIs quando existirem.

---

## 📈 Interpretando Gráficos

### Gráfico de Barras

**O que mostra:** Comparação entre categorias/produtos

**Como ler:**
- Barras mais altas = maior valor
- Cores diferentes = margem (verde = boa, vermelho = ruim)

**Interação:**
- Passe o mouse para ver valores exatos
- Click na legenda para esconder/mostrar séries

### Gráfico de Pizza

**O que mostra:** Participação percentual

**Como ler:**
- Fatias maiores = maior participação
- Percentuais aparecem em cada fatia

**Interação:**
- Passe o mouse para detalhes
- Click para destacar

### Gráfico de Linha

**O que mostra:** Evolução ao longo do tempo

**Como ler:**
- Linha subindo = crescimento
- Linha descendo = queda
- Linha horizontal cinza = média

**Interação:**
- Zoom: arraste para selecionar área
- Pan: segure e arraste
- Reset: duplo-click

### Box Plot

**O que mostra:** Distribuição de valores

**Como ler:**
- Caixa = 50% dos dados estão aqui
- Linha central = mediana
- "Bigodes" = valores extremos
- Pontos = outliers

---

## 💡 Casos de Uso Comuns

### Caso 1: Identificar Produtos Parados

**Objetivo:** Encontrar produtos com estoque alto mas sem vendas

**Passos:**
1. Ir em **Dashboard KPIs Beleza**
2. Click em botão **🛑 Sem Vendas**
3. Ordenar por valor de estoque
4. Tomar ação: promoção ou descontinuar

### Caso 2: Analisar Categoria Específica

**Objetivo:** Ver performance de Esmaltes

**Passos:**
1. Sidebar → **📦 Categorias**
2. Selecionar "ESMALTES"
3. Ver estatísticas atualizadas
4. Analisar margem, estoque, vendas

### Caso 3: Produtos Lucrativos

**Objetivo:** Identificar produtos com melhor margem

**Passos:**
1. Sidebar → **💰 Margem de Lucro**
2. Slider para 30% ou mais
3. Ver produtos filtrados
4. Dashboard → Aba "Margem" → Top 5

### Caso 4: Planejar Compras

**Objetivo:** Saber o que repor

**Passos:**
1. Dashboard KPIs → Botão **🔴 Ruptura**
2. Ver produtos sem estoque
3. Ordenar por vendas (alta prioridade)
4. Fazer pedido aos fornecedores

### Caso 5: Análise Sazonal

**Objetivo:** Entender quais meses vendem mais

**Passos:**
1. Dashboard KPIs → Aba **Sazonalidade**
2. Ver gráfico de vendas mensais
3. Identificar pico e baixa
4. Planejar estoque para próximo ano

---

## 🔐 Segurança e Boas Práticas

### Senhas

✅ Trocar senha periodicamente
✅ Não compartilhar credenciais
❌ Não anotar senha em papel

### Dados

✅ Fazer backup dos dados regularmente
✅ Revisar alertas diariamente
❌ Não ignorar alertas críticos

### Navegação

✅ Fazer logout ao sair
✅ Não deixar sessão aberta em PC público
✅ Usar filtros para análises específicas

---

## ❓ Perguntas Frequentes (FAQ)

### O sistema está lento, o que fazer?

1. Recarregar a página (F5)
2. Limpar filtros
3. Aguardar até 30s (primeira carga)
4. Se persistir, contatar suporte

### Como atualizar os dados?

Dados são atualizados automaticamente quando você adiciona/modifica produtos no sistema.

### Posso exportar gráficos?

Sim! Passe o mouse sobre o gráfico e click no ícone da câmera 📷

### Posso compartilhar análises?

Sim! Use o botão de compartilhar ou tire screenshot da tela.

### O que fazer se esquecer a senha?

Contatar o administrador do sistema para reset.

### Quantos usuários podem usar?

Ilimitado! Cada pessoa deve ter seu próprio login.

---

## 📞 Suporte e Contato

### Problemas Técnicos

**Email:** suporte@seudominio.com
**Telefone:** (XX) XXXX-XXXX
**Horário:** Segunda a Sexta, 9h-18h

### Feedback e Sugestões

Adoramos ouvir você! Envie sugestões de melhorias para:
**Email:** feedback@seudominio.com

### Treinamento Adicional

Se precisar de treinamento presencial ou online, entre em contato!

---

## 🎓 Glossário de Termos

**SKU:** Stock Keeping Unit - código único de cada produto

**Margem:** Diferença entre preço de venda e custo

**Ruptura:** Quando produto está sem estoque

**Sazonalidade:** Variação de vendas ao longo do ano

**Dashboard:** Painel visual com gráficos e métricas

**KPI:** Key Performance Indicator - indicador chave de performance

**Filtro:** Ferramenta para selecionar dados específicos

**Alerta:** Notificação automática de problema ou oportunidade

---

## 🎉 Conclusão

Parabéns! Agora você sabe usar seu Agente BI de Beleza.

**Dicas Finais:**

1. ✅ Comece simples: faça perguntas básicas
2. ✅ Explore os filtros gradualmente
3. ✅ Revise alertas diariamente
4. ✅ Use gráficos para apresentações
5. ✅ Peça ajuda quando precisar

**Lembre-se:**
> Dados sem ação são apenas números.
> Use insights para tomar decisões!

---

**Versão:** 1.0
**Última atualização:** Novembro 2024
**Desenvolvido especialmente para o setor de beleza** 💄✨
