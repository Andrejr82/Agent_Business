"""
Script de Limpeza de Dados - Setor de Beleza
==============================================

Corrige problemas identificados no arquivo Filial_Madureira.parquet:
1. Encoding UTF-8 incorreto (caracteres �)
2. Coluna LUCRO TOTAL % não numérica
3. Nomes de fabricantes inconsistentes
4. Tipos de dados incorretos
5. Valores nulos e inconsistências

Uso:
    python scripts/limpar_dados_beleza.py

Saída:
    data/parquet/Filial_Madureira_LIMPO.parquet
"""

import sys
import os
from pathlib import Path

# Adicionar raiz do projeto ao path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

import pandas as pd
import numpy as np
from datetime import datetime
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LimpadorDadosBeleza:
    """
    Classe para limpeza e normalização de dados do setor de beleza
    """

    def __init__(self, arquivo_entrada: str):
        """
        Inicializa o limpador

        Args:
            arquivo_entrada: Caminho para o arquivo Parquet original
        """
        self.arquivo_entrada = Path(arquivo_entrada)
        self.df = None
        self.df_original = None
        self.relatorio = {
            'total_linhas_original': 0,
            'total_colunas': 0,
            'problemas_corrigidos': [],
            'linhas_removidas': 0,
            'valores_corrigidos': 0
        }

    def carregar_dados(self) -> bool:
        """
        Carrega dados do Parquet

        Returns:
            bool: True se sucesso, False se erro
        """
        try:
            logger.info(f"Carregando dados de {self.arquivo_entrada}...")

            if not self.arquivo_entrada.exists():
                logger.error(f"Arquivo não encontrado: {self.arquivo_entrada}")
                return False

            self.df = pd.read_parquet(self.arquivo_entrada)
            self.df_original = self.df.copy()

            self.relatorio['total_linhas_original'] = len(self.df)
            self.relatorio['total_colunas'] = len(self.df.columns)

            logger.info(f"✓ Dados carregados: {len(self.df)} linhas, {len(self.df.columns)} colunas")
            return True

        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            return False

    def corrigir_encoding(self):
        """
        Corrige problemas de encoding em colunas de texto
        """
        logger.info("1. Corrigindo encoding UTF-8...")

        colunas_texto = ['DESCRIÇÃO', 'FABRICANTE', 'GRUPO']
        valores_corrigidos = 0

        for col in colunas_texto:
            if col not in self.df.columns:
                continue

            try:
                # Tentar decodificar de latin1 para utf-8
                self.df[col] = self.df[col].apply(
                    lambda x: x.encode('latin1', errors='ignore').decode('utf-8', errors='ignore')
                    if isinstance(x, str) else x
                )
                valores_corrigidos += 1
                logger.info(f"  ✓ Corrigido encoding da coluna: {col}")

            except Exception as e:
                logger.warning(f"  ⚠ Não foi possível corrigir {col}: {e}")

        self.relatorio['problemas_corrigidos'].append(f"Encoding corrigido em {valores_corrigidos} colunas")

    def normalizar_fabricantes(self):
        """
        Normaliza nomes de fabricantes (uppercase, remover espaços extras)
        """
        logger.info("2. Normalizando fabricantes...")

        if 'FABRICANTE' not in self.df.columns:
            logger.warning("  ⚠ Coluna FABRICANTE não encontrada")
            return

        antes = self.df['FABRICANTE'].nunique()

        # Normalizar
        self.df['FABRICANTE'] = (
            self.df['FABRICANTE']
            .astype(str)
            .str.strip()
            .str.upper()
            .replace('NAN', np.nan)
        )

        depois = self.df['FABRICANTE'].nunique()
        reducao = antes - depois

        logger.info(f"  ✓ Fabricantes únicos: {antes} → {depois} (redução de {reducao})")
        self.relatorio['problemas_corrigidos'].append(f"Fabricantes normalizados: {antes} → {depois}")

    def normalizar_grupos(self):
        """
        Normaliza nomes de grupos/categorias
        """
        logger.info("3. Normalizando grupos/categorias...")

        if 'GRUPO' not in self.df.columns:
            logger.warning("  ⚠ Coluna GRUPO não encontrada")
            return

        antes = self.df['GRUPO'].nunique()

        # Normalizar
        self.df['GRUPO'] = (
            self.df['GRUPO']
            .astype(str)
            .str.strip()
            .str.upper()
            .replace('NAN', np.nan)
        )

        depois = self.df['GRUPO'].nunique()
        reducao = antes - depois

        logger.info(f"  ✓ Grupos únicos: {antes} → {depois} (redução de {reducao})")
        self.relatorio['problemas_corrigidos'].append(f"Grupos normalizados: {antes} → {depois}")

    def converter_margem_para_numerico(self):
        """
        Converte coluna LUCRO TOTAL % para numérico puro
        """
        logger.info("4. Convertendo LUCRO TOTAL % para numérico...")

        if 'LUCRO TOTAL %' not in self.df.columns:
            logger.warning("  ⚠ Coluna LUCRO TOTAL % não encontrada")
            return

        try:
            # Remover símbolo %, converter para float
            self.df['LUCRO TOTAL %'] = (
                self.df['LUCRO TOTAL %']
                .astype(str)
                .str.replace('%', '', regex=False)
                .str.replace(',', '.', regex=False)
                .str.strip()
            )

            # Converter para numérico
            self.df['LUCRO TOTAL %'] = pd.to_numeric(
                self.df['LUCRO TOTAL %'],
                errors='coerce'
            )

            # Contar valores inválidos
            invalidos = self.df['LUCRO TOTAL %'].isna().sum()
            validos = len(self.df) - invalidos

            logger.info(f"  ✓ Convertido para numérico: {validos} valores válidos, {invalidos} inválidos")
            self.relatorio['problemas_corrigidos'].append(f"LUCRO TOTAL % convertido: {validos} válidos")

        except Exception as e:
            logger.error(f"  ✗ Erro ao converter margem: {e}")

    def converter_colunas_numericas(self):
        """
        Garante que colunas numéricas estejam no tipo correto
        """
        logger.info("5. Convertendo colunas numéricas...")

        colunas_numericas = [
            'QTD', 'VENDA R$', 'DESC. R$', 'CUSTO R$', 'LUCRO R$',
            'CUSTO UNIT R$', 'VENDA UNIT R$', 'LUCRO UNIT %', 'SALDO',
            'VLR ESTOQUE VENDA', 'VLR ESTOQUE CUSTO', 'QTD ULTIMA COMPRA',
            # Vendas mensais
            'VENDA QTD JAN', 'VENDA QTD FEV', 'VENDA QTD MAR', 'VENDA QTD ABR',
            'VENDA QTD MAI', 'VENDA QTD JUN', 'VENDA QTD JUL', 'VENDA QTD AGO',
            'VENDA QTD SET', 'VENDA QTD OUT', 'VENDA QTD NOV', 'VENDA QTD DEZ'
        ]

        colunas_convertidas = 0

        for col in colunas_numericas:
            if col not in self.df.columns:
                continue

            try:
                self.df[col] = pd.to_numeric(self.df[col], errors='coerce')
                colunas_convertidas += 1
            except Exception as e:
                logger.warning(f"  ⚠ Erro ao converter {col}: {e}")

        logger.info(f"  ✓ {colunas_convertidas} colunas numéricas convertidas")
        self.relatorio['problemas_corrigidos'].append(f"{colunas_convertidas} colunas numéricas convertidas")

    def converter_colunas_data(self):
        """
        Converte colunas de data para datetime
        """
        logger.info("6. Convertendo colunas de data...")

        colunas_data = ['DT CADASTRO', 'DT ULTIMA COMPRA']
        colunas_convertidas = 0

        for col in colunas_data:
            if col not in self.df.columns:
                continue

            try:
                self.df[col] = pd.to_datetime(self.df[col], errors='coerce')
                invalidos = self.df[col].isna().sum()
                validos = len(self.df) - invalidos

                logger.info(f"  ✓ {col}: {validos} datas válidas, {invalidos} inválidas")
                colunas_convertidas += 1

            except Exception as e:
                logger.warning(f"  ⚠ Erro ao converter {col}: {e}")

        self.relatorio['problemas_corrigidos'].append(f"{colunas_convertidas} colunas de data convertidas")

    def remover_duplicatas(self):
        """
        Remove linhas duplicadas baseado em ITEM (código do produto)
        """
        logger.info("7. Removendo duplicatas...")

        if 'ITEM' not in self.df.columns:
            logger.warning("  ⚠ Coluna ITEM não encontrada")
            return

        antes = len(self.df)
        self.df = self.df.drop_duplicates(subset=['ITEM'], keep='first')
        depois = len(self.df)
        removidas = antes - depois

        if removidas > 0:
            logger.warning(f"  ⚠ {removidas} linhas duplicadas removidas")
            self.relatorio['linhas_removidas'] += removidas
        else:
            logger.info(f"  ✓ Nenhuma duplicata encontrada")

        self.relatorio['problemas_corrigidos'].append(f"{removidas} duplicatas removidas")

    def preencher_valores_faltantes(self):
        """
        Preenche valores faltantes com valores padrão inteligentes
        """
        logger.info("8. Preenchendo valores faltantes...")

        preenchimentos = 0

        # Vendas mensais: 0 (não teve venda)
        meses = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
        for mes in meses:
            col = f'VENDA QTD {mes}'
            if col in self.df.columns:
                antes_na = self.df[col].isna().sum()
                self.df[col] = self.df[col].fillna(0)
                preenchimentos += antes_na

        # SALDO: 0 (sem estoque)
        if 'SALDO' in self.df.columns:
            antes_na = self.df['SALDO'].isna().sum()
            self.df['SALDO'] = self.df['SALDO'].fillna(0)
            preenchimentos += antes_na

        # Valores financeiros: 0
        colunas_financeiras = ['VENDA R$', 'CUSTO R$', 'LUCRO R$', 'VLR ESTOQUE VENDA', 'VLR ESTOQUE CUSTO']
        for col in colunas_financeiras:
            if col in self.df.columns:
                antes_na = self.df[col].isna().sum()
                self.df[col] = self.df[col].fillna(0)
                preenchimentos += antes_na

        logger.info(f"  ✓ {preenchimentos} valores faltantes preenchidos")
        self.relatorio['valores_corrigidos'] = preenchimentos

    def adicionar_metricas_calculadas(self):
        """
        Adiciona métricas calculadas úteis para o setor de beleza
        """
        logger.info("9. Adicionando métricas calculadas...")

        metricas_adicionadas = 0

        # 1. Vendas totais (soma de todos os meses)
        if all(f'VENDA QTD {mes}' in self.df.columns for mes in ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']):
            meses = ['JAN', 'FEV', 'MAR', 'ABR', 'MAI', 'JUN', 'JUL', 'AGO', 'SET', 'OUT', 'NOV', 'DEZ']
            colunas_vendas = [f'VENDA QTD {mes}' for mes in meses]
            self.df['VENDAS_TOTAL_ANO'] = self.df[colunas_vendas].sum(axis=1)
            metricas_adicionadas += 1
            logger.info("  ✓ VENDAS_TOTAL_ANO calculada")

        # 2. Média de vendas mensais
        if 'VENDAS_TOTAL_ANO' in self.df.columns:
            self.df['VENDAS_MEDIA_MENSAL'] = self.df['VENDAS_TOTAL_ANO'] / 12
            metricas_adicionadas += 1
            logger.info("  ✓ VENDAS_MEDIA_MENSAL calculada")

        # 3. Dias de cobertura de estoque
        if 'SALDO' in self.df.columns and 'VENDAS_MEDIA_MENSAL' in self.df.columns:
            self.df['DIAS_COBERTURA'] = np.where(
                self.df['VENDAS_MEDIA_MENSAL'] > 0,
                (self.df['SALDO'] / self.df['VENDAS_MEDIA_MENSAL']) * 30,
                np.inf
            )
            metricas_adicionadas += 1
            logger.info("  ✓ DIAS_COBERTURA calculada")

        # 4. Status do produto (em estoque, ruptura, etc.)
        if 'SALDO' in self.df.columns:
            def classificar_estoque(saldo):
                if pd.isna(saldo) or saldo <= 0:
                    return 'RUPTURA'
                elif saldo < 10:
                    return 'ESTOQUE_BAIXO'
                elif saldo < 50:
                    return 'ESTOQUE_NORMAL'
                else:
                    return 'ESTOQUE_ALTO'

            self.df['STATUS_ESTOQUE'] = self.df['SALDO'].apply(classificar_estoque)
            metricas_adicionadas += 1
            logger.info("  ✓ STATUS_ESTOQUE calculado")

        # 5. Classificação de margem
        if 'LUCRO TOTAL %' in self.df.columns:
            def classificar_margem(margem):
                if pd.isna(margem):
                    return 'SEM_DADOS'
                elif margem < 10:
                    return 'MARGEM_BAIXA'
                elif margem < 30:
                    return 'MARGEM_MEDIA'
                else:
                    return 'MARGEM_ALTA'

            self.df['CLASSIFICACAO_MARGEM'] = self.df['LUCRO TOTAL %'].apply(classificar_margem)
            metricas_adicionadas += 1
            logger.info("  ✓ CLASSIFICACAO_MARGEM calculada")

        logger.info(f"  ✓ {metricas_adicionadas} métricas calculadas adicionadas")
        self.relatorio['problemas_corrigidos'].append(f"{metricas_adicionadas} métricas calculadas adicionadas")

    def validar_dados(self):
        """
        Valida qualidade dos dados após limpeza
        """
        logger.info("10. Validando dados limpos...")

        validacoes = []

        # 1. Verificar valores negativos em colunas que não podem ser negativas
        colunas_positivas = ['QTD', 'SALDO', 'VENDA R$', 'CUSTO R$']
        for col in colunas_positivas:
            if col in self.df.columns:
                negativos = (self.df[col] < 0).sum()
                if negativos > 0:
                    validacoes.append(f"⚠ {col}: {negativos} valores negativos encontrados")

        # 2. Verificar consistência entre vendas e estoque
        if 'VENDAS_TOTAL_ANO' in self.df.columns and 'SALDO' in self.df.columns:
            sem_vendas_com_estoque = len(self.df[(self.df['VENDAS_TOTAL_ANO'] == 0) & (self.df['SALDO'] > 0)])
            if sem_vendas_com_estoque > 0:
                validacoes.append(f"ℹ {sem_vendas_com_estoque} produtos sem vendas mas com estoque (produtos novos ou parados)")

        # 3. Verificar qualidade dos dados
        total_valores = len(self.df) * len(self.df.columns)
        valores_nulos = self.df.isna().sum().sum()
        qualidade = ((total_valores - valores_nulos) / total_valores) * 100

        logger.info(f"  ✓ Qualidade dos dados: {qualidade:.2f}%")

        if validacoes:
            for v in validacoes:
                logger.warning(f"  {v}")

    def salvar_dados_limpos(self, arquivo_saida: str = None):
        """
        Salva dados limpos em novo arquivo Parquet

        Args:
            arquivo_saida: Caminho para salvar. Se None, usa padrão.
        """
        logger.info("11. Salvando dados limpos...")

        if arquivo_saida is None:
            arquivo_saida = self.arquivo_entrada.parent / 'Filial_Madureira_LIMPO.parquet'
        else:
            arquivo_saida = Path(arquivo_saida)

        try:
            # Criar diretório se não existir
            arquivo_saida.parent.mkdir(parents=True, exist_ok=True)

            # Salvar
            self.df.to_parquet(arquivo_saida, index=False)
            logger.info(f"  ✓ Dados salvos em: {arquivo_saida}")
            logger.info(f"  ✓ Linhas: {len(self.df)}, Colunas: {len(self.df.columns)}")

            return True

        except Exception as e:
            logger.error(f"  ✗ Erro ao salvar: {e}")
            return False

    def gerar_relatorio(self):
        """
        Gera relatório detalhado da limpeza
        """
        logger.info("\n" + "="*80)
        logger.info("RELATÓRIO DE LIMPEZA DE DADOS")
        logger.info("="*80)
        logger.info(f"Arquivo original: {self.arquivo_entrada}")
        logger.info(f"Total de linhas: {self.relatorio['total_linhas_original']}")
        logger.info(f"Total de colunas: {self.relatorio['total_colunas']}")
        logger.info(f"Linhas removidas: {self.relatorio['linhas_removidas']}")
        logger.info(f"Valores corrigidos: {self.relatorio['valores_corrigidos']}")
        logger.info("\nProblemas corrigidos:")
        for problema in self.relatorio['problemas_corrigidos']:
            logger.info(f"  • {problema}")
        logger.info("="*80 + "\n")

    def executar_limpeza_completa(self, arquivo_saida: str = None) -> bool:
        """
        Executa pipeline completo de limpeza

        Args:
            arquivo_saida: Caminho para salvar dados limpos

        Returns:
            bool: True se sucesso
        """
        logger.info("="*80)
        logger.info("INICIANDO LIMPEZA DE DADOS - SETOR DE BELEZA")
        logger.info("="*80 + "\n")

        # 1. Carregar dados
        if not self.carregar_dados():
            return False

        # 2. Limpeza
        self.corrigir_encoding()
        self.normalizar_fabricantes()
        self.normalizar_grupos()
        self.converter_margem_para_numerico()
        self.converter_colunas_numericas()
        self.converter_colunas_data()
        self.remover_duplicatas()
        self.preencher_valores_faltantes()
        self.adicionar_metricas_calculadas()
        self.validar_dados()

        # 3. Salvar
        if not self.salvar_dados_limpos(arquivo_saida):
            return False

        # 4. Relatório
        self.gerar_relatorio()

        logger.info("✓ Limpeza concluída com sucesso!")
        return True


def main():
    """
    Função principal
    """
    # Caminhos
    arquivo_entrada = project_root / 'data' / 'parquet' / 'Filial_Madureira.parquet'
    arquivo_saida = project_root / 'data' / 'parquet' / 'Filial_Madureira_LIMPO.parquet'

    # Executar limpeza
    limpador = LimpadorDadosBeleza(arquivo_entrada)
    sucesso = limpador.executar_limpeza_completa(arquivo_saida)

    if sucesso:
        print("\n" + "="*80)
        print("✓ DADOS LIMPOS E PRONTOS PARA USO!")
        print("="*80)
        print(f"\nArquivo limpo salvo em:")
        print(f"  {arquivo_saida}")
        print("\nPróximos passos:")
        print("  1. Atualizar DataSourceManager para usar arquivo limpo")
        print("  2. Testar ferramentas com dados corrigidos")
        print("  3. Implementar filtros interativos")
        return 0
    else:
        print("\n✗ Erro durante limpeza de dados")
        return 1


if __name__ == '__main__':
    exit(main())
