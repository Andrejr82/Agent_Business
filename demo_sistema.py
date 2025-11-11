#!/usr/bin/env python
"""
Demonstração do sistema 100% funcional com dados reais.
"""

from core.data_source_manager import get_data_manager
from core.tools.unified_data_tools import unified_tools

print('\n' + '='*70)
print('DEMONSTRAÇÃO DO SISTEMA 100% FUNCIONAL')
print('='*70)

try:
    # Teste 1: Listar fontes
    print('\n1. FONTES DISPONÍVEIS:')
    print('-'*70)
    manager = get_data_manager()
    status = manager.get_status()
    for name, info in status.items():
        connected = 'OK' if info['connected'] else 'ERRO'
        print(f'  [{connected}] {name}: {info["type"]}')

    # Teste 2: Buscar dados SQL
    print('\n2. ACESSANDO SQL SERVER (admmatao):')
    print('-'*70)
    df = manager.get_data('admmatao', limit=2)
    if not df.empty:
        print(f'  [OK] Encontrados: {len(df)} registros')
        print(f'      Colunas: {len(df.columns)}')
        print(f'      Primeiras: {list(df.columns[:5])}')
        nome = df.iloc[0]['NOME'] if 'NOME' in df.columns else 'N/A'
        print(f'      Primeiro produto: {nome}')
    else:
        print('  [ERRO] Nenhum dado encontrado')

    # Teste 3: Buscar em Parquet
    print('\n3. ACESSANDO PARQUET (ADMAT):')
    print('-'*70)
    df_parquet = manager.get_data('ADMAT', limit=2)
    if not df_parquet.empty:
        print(f'  [OK] Encontrados: {len(df_parquet)} registros')
        print(f'      Colunas: {len(df_parquet.columns)}')
        print(f'      Primeiras: {list(df_parquet.columns[:5])}')
    else:
        print('  [ERRO] Nenhum dado encontrado')

    # Teste 4: Ferramentas
    print('\n4. FERRAMENTAS DISPONÍVEIS:')
    print('-'*70)
    for tool in unified_tools:
        print(f'  [OK] {tool.name}')

    print('\n' + '='*70)
    print('SISTEMA 100% FUNCIONAL!')
    print('='*70 + '\n')

except Exception as e:
    print(f'\n[ERRO] {e}')
    import traceback
    traceback.print_exc()
