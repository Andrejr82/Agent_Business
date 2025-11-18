"""
Sistema de Alertas Automáticos - Setor de Beleza
=================================================

Sistema inteligente que monitora métricas críticas e gera alertas automáticos:
- Ruptura de estoque
- Margem baixa
- Estoque excessivo
- Produtos sem venda
- Produtos de alto valor parados

Autor: Agente BI Caçulinha
Data: 2024
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SistemaAlertas:
    """
    Sistema de alertas automáticos para monitoramento de negócios
    """

    # Níveis de severidade
    SEVERIDADE_CRITICA = 'CRÍTICA'
    SEVERIDADE_ALTA = 'ALTA'
    SEVERIDADE_MEDIA = 'MÉDIA'
    SEVERIDADE_BAIXA = 'BAIXA'

    # Tipos de alerta
    TIPO_RUPTURA = 'RUPTURA_ESTOQUE'
    TIPO_MARGEM_BAIXA = 'MARGEM_BAIXA'
    TIPO_ESTOQUE_EXCESSIVO = 'ESTOQUE_EXCESSIVO'
    TIPO_SEM_VENDAS = 'SEM_VENDAS'
    TIPO_ALTO_VALOR_PARADO = 'ALTO_VALOR_PARADO'
    TIPO_MARGEM_NEGATIVA = 'MARGEM_NEGATIVA'

    def __init__(self, df: pd.DataFrame):
        """
        Inicializa o sistema de alertas

        Args:
            df: DataFrame com dados dos produtos
        """
        self.df = df.copy()
        self.alertas: List[Dict[str, Any]] = []
        self.timestamp = datetime.now()

    def verificar_ruptura_estoque(
        self,
        threshold: int = 0,
        margem_minima_pct: float = 20.0
    ) -> List[Dict]:
        """
        Alerta de produtos em ruptura de estoque

        Args:
            threshold: Nível de estoque considerado ruptura
            margem_minima_pct: Margem mínima para considerar crítico

        Returns:
            Lista de alertas gerados
        """
        if 'SALDO' not in self.df.columns:
            logger.warning("Coluna SALDO não encontrada")
            return []

        produtos_ruptura = self.df[self.df['SALDO'] <= threshold].copy()

        if len(produtos_ruptura) == 0:
            return []

        # Calcular impacto
        if 'VLR ESTOQUE VENDA' in produtos_ruptura.columns:
            valor_perdido = produtos_ruptura['VLR ESTOQUE VENDA'].sum()
        else:
            valor_perdido = 0

        # Produtos de alta margem em ruptura são CRÍTICOS
        if 'LUCRO TOTAL %' in produtos_ruptura.columns:
            alta_margem_ruptura = produtos_ruptura[
                produtos_ruptura['LUCRO TOTAL %'] >= margem_minima_pct
            ]
            severidade = self.SEVERIDADE_CRITICA if len(alta_margem_ruptura) > 0 else self.SEVERIDADE_ALTA
        else:
            severidade = self.SEVERIDADE_ALTA

        # Top 10 produtos em ruptura por valor
        if 'VLR ESTOQUE VENDA' in produtos_ruptura.columns:
            top_produtos = produtos_ruptura.nlargest(10, 'VLR ESTOQUE VENDA')
        else:
            top_produtos = produtos_ruptura.head(10)

        alerta = {
            'tipo': self.TIPO_RUPTURA,
            'severidade': severidade,
            'quantidade': len(produtos_ruptura),
            'titulo': f"⚠️ {len(produtos_ruptura)} produtos em RUPTURA de estoque",
            'mensagem': (
                f"Há {len(produtos_ruptura)} produtos com estoque zerado ou negativo. "
                f"Valor potencial em risco: R$ {valor_perdido:,.2f}"
            ),
            'impacto_financeiro': valor_perdido,
            'produtos': top_produtos[[
                col for col in ['ITEM', 'DESCRIÇÃO', 'SALDO', 'LUCRO TOTAL %', 'GRUPO']
                if col in top_produtos.columns
            ]].to_dict('records'),
            'acao_recomendada': "Reposição urgente de estoque",
            'timestamp': self.timestamp
        }

        self.alertas.append(alerta)
        return [alerta]

    def verificar_margem_baixa(
        self,
        margem_minima: float = 15.0,
        valor_minimo: float = 1000.0
    ) -> List[Dict]:
        """
        Alerta de produtos com margem abaixo do mínimo aceitável

        Args:
            margem_minima: Margem mínima aceitável (%)
            valor_minimo: Valor mínimo de estoque para considerar

        Returns:
            Lista de alertas gerados
        """
        if 'LUCRO TOTAL %' not in self.df.columns:
            logger.warning("Coluna LUCRO TOTAL % não encontrada")
            return []

        # Produtos com margem baixa
        condicoes = self.df['LUCRO TOTAL %'] < margem_minima

        # Filtrar apenas produtos com valor significativo
        if 'VLR ESTOQUE VENDA' in self.df.columns:
            condicoes &= (self.df['VLR ESTOQUE VENDA'] >= valor_minimo)

        produtos_margem_baixa = self.df[condicoes].copy()

        if len(produtos_margem_baixa) == 0:
            return []

        # Calcular impacto
        valor_total = produtos_margem_baixa['VLR ESTOQUE VENDA'].sum() if 'VLR ESTOQUE VENDA' in produtos_margem_baixa.columns else 0
        margem_media = produtos_margem_baixa['LUCRO TOTAL %'].mean()

        # Top 10 produtos por valor
        if 'VLR ESTOQUE VENDA' in produtos_margem_baixa.columns:
            top_produtos = produtos_margem_baixa.nlargest(10, 'VLR ESTOQUE VENDA')
        else:
            top_produtos = produtos_margem_baixa.head(10)

        alerta = {
            'tipo': self.TIPO_MARGEM_BAIXA,
            'severidade': self.SEVERIDADE_MEDIA,
            'quantidade': len(produtos_margem_baixa),
            'titulo': f"📉 {len(produtos_margem_baixa)} produtos com margem < {margem_minima}%",
            'mensagem': (
                f"Há {len(produtos_margem_baixa)} produtos com margem abaixo de {margem_minima}%. "
                f"Margem média: {margem_media:.1f}%. Valor total: R$ {valor_total:,.2f}"
            ),
            'impacto_financeiro': valor_total,
            'produtos': top_produtos[[
                col for col in ['ITEM', 'DESCRIÇÃO', 'LUCRO TOTAL %', 'VENDA UNIT R$', 'CUSTO UNIT R$']
                if col in top_produtos.columns
            ]].to_dict('records'),
            'acao_recomendada': "Revisar precificação ou renegociar custo com fornecedor",
            'timestamp': self.timestamp
        }

        self.alertas.append(alerta)
        return [alerta]

    def verificar_estoque_excessivo(
        self,
        dias_cobertura_max: int = 90,
        valor_minimo: float = 500.0
    ) -> List[Dict]:
        """
        Alerta de produtos com estoque excessivo (muitos dias de cobertura)

        Args:
            dias_cobertura_max: Dias máximos aceitáveis de cobertura
            valor_minimo: Valor mínimo de estoque para considerar

        Returns:
            Lista de alertas gerados
        """
        if 'DIAS_COBERTURA' not in self.df.columns:
            logger.warning("Coluna DIAS_COBERTURA não encontrada")
            return []

        # Produtos com estoque excessivo (capital parado)
        condicoes = (
            (self.df['DIAS_COBERTURA'] > dias_cobertura_max) &
            (self.df['DIAS_COBERTURA'] != np.inf)  # Excluir produtos sem vendas
        )

        # Filtrar por valor
        if 'VLR ESTOQUE VENDA' in self.df.columns:
            condicoes &= (self.df['VLR ESTOQUE VENDA'] >= valor_minimo)

        produtos_excesso = self.df[condicoes].copy()

        if len(produtos_excesso) == 0:
            return []

        # Calcular capital parado
        capital_parado = produtos_excesso['VLR ESTOQUE VENDA'].sum() if 'VLR ESTOQUE VENDA' in produtos_excesso.columns else 0
        dias_media = produtos_excesso['DIAS_COBERTURA'].mean()

        # Top 10 produtos por valor
        if 'VLR ESTOQUE VENDA' in produtos_excesso.columns:
            top_produtos = produtos_excesso.nlargest(10, 'VLR ESTOQUE VENDA')
        else:
            top_produtos = produtos_excesso.head(10)

        alerta = {
            'tipo': self.TIPO_ESTOQUE_EXCESSIVO,
            'severidade': self.SEVERIDADE_MEDIA,
            'quantidade': len(produtos_excesso),
            'titulo': f"📦 {len(produtos_excesso)} produtos com estoque > {dias_cobertura_max} dias",
            'mensagem': (
                f"Há {len(produtos_excesso)} produtos com estoque excessivo (média: {dias_media:.0f} dias). "
                f"Capital parado: R$ {capital_parado:,.2f}"
            ),
            'impacto_financeiro': capital_parado,
            'produtos': top_produtos[[
                col for col in ['ITEM', 'DESCRIÇÃO', 'SALDO', 'DIAS_COBERTURA', 'VLR ESTOQUE VENDA']
                if col in top_produtos.columns
            ]].to_dict('records'),
            'acao_recomendada': "Considerar promoção ou reduzir pedidos futuros",
            'timestamp': self.timestamp
        }

        self.alertas.append(alerta)
        return [alerta]

    def verificar_produtos_sem_venda(
        self,
        meses_sem_venda: int = 3,
        valor_minimo: float = 200.0
    ) -> List[Dict]:
        """
        Alerta de produtos sem venda nos últimos X meses

        Args:
            meses_sem_venda: Número de meses consecutivos sem venda
            valor_minimo: Valor mínimo de estoque para considerar

        Returns:
            Lista de alertas gerados
        """
        # Verificar se temos colunas de vendas mensais
        meses_disponiveis = []
        for mes in ['DEZ', 'NOV', 'OUT', 'SET', 'AGO', 'JUL']:
            col = f'VENDA QTD {mes}'
            if col in self.df.columns:
                meses_disponiveis.append(col)
            if len(meses_disponiveis) >= meses_sem_venda:
                break

        if len(meses_disponiveis) < meses_sem_venda:
            logger.warning(f"Colunas de vendas mensais insuficientes: {len(meses_disponiveis)}")
            return []

        # Calcular vendas nos últimos X meses
        self.df['VENDAS_ULTIMOS_MESES'] = self.df[meses_disponiveis[:meses_sem_venda]].sum(axis=1)

        # Produtos sem venda MAS com estoque
        condicoes = (
            (self.df['VENDAS_ULTIMOS_MESES'] == 0) &
            (self.df['SALDO'] > 0) if 'SALDO' in self.df.columns else (self.df['VENDAS_ULTIMOS_MESES'] == 0)
        )

        # Filtrar por valor
        if 'VLR ESTOQUE VENDA' in self.df.columns:
            condicoes &= (self.df['VLR ESTOQUE VENDA'] >= valor_minimo)

        produtos_sem_venda = self.df[condicoes].copy()

        if len(produtos_sem_venda) == 0:
            return []

        # Calcular valor imobilizado
        valor_imobilizado = produtos_sem_venda['VLR ESTOQUE VENDA'].sum() if 'VLR ESTOQUE VENDA' in produtos_sem_venda.columns else 0

        # Top 10 produtos por valor
        if 'VLR ESTOQUE VENDA' in produtos_sem_venda.columns:
            top_produtos = produtos_sem_venda.nlargest(10, 'VLR ESTOQUE VENDA')
        else:
            top_produtos = produtos_sem_venda.head(10)

        alerta = {
            'tipo': self.TIPO_SEM_VENDAS,
            'severidade': self.SEVERIDADE_BAIXA,
            'quantidade': len(produtos_sem_venda),
            'titulo': f"🛑 {len(produtos_sem_venda)} produtos SEM vendas em {meses_sem_venda} meses",
            'mensagem': (
                f"Há {len(produtos_sem_venda)} produtos sem venda nos últimos {meses_sem_venda} meses. "
                f"Valor imobilizado: R$ {valor_imobilizado:,.2f}"
            ),
            'impacto_financeiro': valor_imobilizado,
            'produtos': top_produtos[[
                col for col in ['ITEM', 'DESCRIÇÃO', 'SALDO', 'VLR ESTOQUE VENDA', 'GRUPO']
                if col in top_produtos.columns
            ]].to_dict('records'),
            'acao_recomendada': "Avaliar descontinuação ou promoção agressiva",
            'timestamp': self.timestamp
        }

        self.alertas.append(alerta)
        return [alerta]

    def verificar_margem_negativa(self) -> List[Dict]:
        """
        Alerta CRÍTICO de produtos com margem negativa (venda abaixo do custo)

        Returns:
            Lista de alertas gerados
        """
        if 'LUCRO TOTAL %' not in self.df.columns:
            logger.warning("Coluna LUCRO TOTAL % não encontrada")
            return []

        produtos_margem_negativa = self.df[self.df['LUCRO TOTAL %'] < 0].copy()

        if len(produtos_margem_negativa) == 0:
            return []

        # Calcular prejuízo potencial
        prejuizo = abs(produtos_margem_negativa['LUCRO R$'].sum()) if 'LUCRO R$' in produtos_margem_negativa.columns else 0

        alerta = {
            'tipo': self.TIPO_MARGEM_NEGATIVA,
            'severidade': self.SEVERIDADE_CRITICA,
            'quantidade': len(produtos_margem_negativa),
            'titulo': f"🚨 {len(produtos_margem_negativa)} produtos com MARGEM NEGATIVA",
            'mensagem': (
                f"CRÍTICO: {len(produtos_margem_negativa)} produtos estão sendo vendidos abaixo do custo! "
                f"Prejuízo estimado: R$ {prejuizo:,.2f}"
            ),
            'impacto_financeiro': -prejuizo,
            'produtos': produtos_margem_negativa[[
                col for col in ['ITEM', 'DESCRIÇÃO', 'LUCRO TOTAL %', 'VENDA UNIT R$', 'CUSTO UNIT R$']
                if col in produtos_margem_negativa.columns
            ]].to_dict('records'),
            'acao_recomendada': "URGENTE: Corrigir precificação imediatamente",
            'timestamp': self.timestamp
        }

        self.alertas.append(alerta)
        return [alerta]

    def executar_todas_verificacoes(self) -> List[Dict]:
        """
        Executa todas as verificações de alertas

        Returns:
            Lista completa de alertas gerados
        """
        logger.info("Executando todas as verificações de alertas...")

        # Executar verificações
        self.verificar_margem_negativa()  # Primeira (mais crítica)
        self.verificar_ruptura_estoque()
        self.verificar_margem_baixa()
        self.verificar_estoque_excessivo()
        self.verificar_produtos_sem_venda()

        logger.info(f"Total de alertas gerados: {len(self.alertas)}")
        return self.alertas

    def obter_alertas_prioritarios(self, limite: int = 5) -> List[Dict]:
        """
        Retorna os alertas mais prioritários

        Args:
            limite: Número máximo de alertas a retornar

        Returns:
            Lista de alertas ordenados por prioridade
        """
        if not self.alertas:
            self.executar_todas_verificacoes()

        # Ordenar por severidade e impacto financeiro
        ordem_severidade = {
            self.SEVERIDADE_CRITICA: 0,
            self.SEVERIDADE_ALTA: 1,
            self.SEVERIDADE_MEDIA: 2,
            self.SEVERIDADE_BAIXA: 3
        }

        alertas_ordenados = sorted(
            self.alertas,
            key=lambda x: (
                ordem_severidade.get(x['severidade'], 99),
                -abs(x.get('impacto_financeiro', 0))
            )
        )

        return alertas_ordenados[:limite]

    def gerar_relatorio_alertas(self) -> pd.DataFrame:
        """
        Gera relatório consolidado de todos os alertas

        Returns:
            DataFrame com resumo dos alertas
        """
        if not self.alertas:
            self.executar_todas_verificacoes()

        if not self.alertas:
            return pd.DataFrame()

        df_alertas = pd.DataFrame([
            {
                'Tipo': a['tipo'],
                'Severidade': a['severidade'],
                'Título': a['titulo'],
                'Quantidade': a['quantidade'],
                'Impacto (R$)': a.get('impacto_financeiro', 0),
                'Ação': a.get('acao_recomendada', '')
            }
            for a in self.alertas
        ])

        return df_alertas

    def exportar_alertas_json(self) -> Dict[str, Any]:
        """
        Exporta alertas em formato JSON

        Returns:
            Dicionário com todos os alertas
        """
        return {
            'timestamp': self.timestamp.isoformat(),
            'total_alertas': len(self.alertas),
            'alertas': self.alertas
        }


class AlertasPrioritarios:
    """
    Classe auxiliar para exibir alertas prioritários no Streamlit
    """

    @staticmethod
    def exibir_alertas(alertas: List[Dict]):
        """
        Exibe alertas no Streamlit com formatação apropriada

        Args:
            alertas: Lista de alertas a exibir
        """
        import streamlit as st

        if not alertas:
            st.success("✅ Nenhum alerta crítico no momento")
            return

        st.warning(f"### ⚠️ {len(alertas)} Alertas Importantes")

        for i, alerta in enumerate(alertas, 1):
            # Escolher ícone e cor por severidade
            icone_map = {
                SistemaAlertas.SEVERIDADE_CRITICA: '🚨',
                SistemaAlertas.SEVERIDADE_ALTA: '⚠️',
                SistemaAlertas.SEVERIDADE_MEDIA: '📊',
                SistemaAlertas.SEVERIDADE_BAIXA: 'ℹ️'
            }

            icone = icone_map.get(alerta['severidade'], '📌')

            # Expandir alertas críticos e de alta severidade por padrão
            expanded = alerta['severidade'] in [
                SistemaAlertas.SEVERIDADE_CRITICA,
                SistemaAlertas.SEVERIDADE_ALTA
            ]

            with st.expander(
                f"{icone} **[{alerta['severidade']}]** {alerta['titulo']}",
                expanded=expanded
            ):
                # Mensagem principal
                st.markdown(alerta['mensagem'])

                # Impacto financeiro
                if alerta.get('impacto_financeiro'):
                    st.metric(
                        "Impacto Financeiro",
                        f"R$ {abs(alerta['impacto_financeiro']):,.2f}",
                        delta=None
                    )

                # Ação recomendada
                if alerta.get('acao_recomendada'):
                    st.info(f"**💡 Ação Recomendada:** {alerta['acao_recomendada']}")

                # Produtos afetados
                if alerta.get('produtos') and len(alerta['produtos']) > 0:
                    st.markdown("**Produtos Afetados (Top 10):**")
                    df_produtos = pd.DataFrame(alerta['produtos'])
                    st.dataframe(df_produtos, use_container_width=True, hide_index=True)


# Exemplo de uso
if __name__ == '__main__':
    print("Sistema de Alertas Automáticos - Setor de Beleza")
    print("="*50)
    print("\nUso:")
    print("  from core.alertas import SistemaAlertas, AlertasPrioritarios")
    print()
    print("  sistema = SistemaAlertas(df)")
    print("  alertas = sistema.executar_todas_verificacoes()")
    print("  AlertasPrioritarios.exibir_alertas(alertas)")
