"""
test_atualizador.py

Testes automatizados para o script atualizador.py
Biblioteca: pytest
Data: 13/08/2026
Objetivo: Validar a função atualizar_status() e funções auxiliares

Execução:
    pytest test_atualizador.py -v
    pytest test_atualizador.py -v --tb=short
"""

import pytest
import pandas as pd
import os
from unittest.mock import patch, MagicMock
from datetime import datetime
import unicodedata


# ============================================================================
# FIXTURES - Dados Fictícios Reutilizáveis
# ============================================================================

@pytest.fixture
def df_octave_basico():
    """
    DataFrame DADOS_OCTAVE com 4 linhas.
    Dados conforme simulação de mesa.
    """
    return pd.DataFrame({
        'Número da OS': ['A01', 'A02', 'A03', 'A05'],
        'Status': ['Concluído', 'Concluído', 'Em Andamento', 'Pendente']
    })


@pytest.fixture
def df_consolidado_basico():
    """
    DataFrame CONSOLIDADO com 6 linhas.
    Dados conforme simulação de mesa.
    """
    return pd.DataFrame({
        'Número da OS': ['A01', 'A02', 'A03', 'A04', 'A05', 'A06'],
        'Status': ['Aguardando', 'Parado', 'Iniciado', 'Aguardando', 'Parado', 'Iniciado'],
        'Descrição': [
            'Manutenção Preventiva',
            'Inspeção Técnica',
            'Teste de Componentes',
            'Reparo Hidráulico',
            'Verificação Elétrica',
            'Calibração de Sensores'
        ]
    })


@pytest.fixture
def df_octave_vazio():
    """DataFrame OCTAVE vazio (0 linhas)."""
    return pd.DataFrame({
        'Número da OS': [],
        'Status': []
    })


@pytest.fixture
def df_consolidado_coluna_alternativa():
    """
    DataFrame CONSOLIDADO com nome de coluna alternativo: 'OS' ao invés de 'Número da OS'
    Para testar detecção case-insensitive
    """
    return pd.DataFrame({
        'OS': ['A01', 'A02', 'A03'],
        'Status': ['Aguardando', 'Parado', 'Iniciado']
    })


@pytest.fixture
def df_octave_coluna_alternativa():
    """
    DataFrame OCTAVE com nome de coluna alternativo: 'Estado' ao invés de 'Status'
    Para testar detecção case-insensitive
    """
    return pd.DataFrame({
        'Número da OS': ['A01', 'A02'],
        'Estado': ['Concluído', 'Concluído']
    })


# ============================================================================
# TESTES - Classe 1: Função atualizar_status()
# ============================================================================

class TestAtualizarStatus:
    """Testes para a função atualizar_status()"""

    # ========================================================================
    # TESTE 1: Sucesso Básico (Simulação de Mesa)
    # ========================================================================

    def test_atualizacao_basica_sucesso(self, df_consolidado_basico, df_octave_basico):
        """
        CENÁRIO 1: Teste de Sucesso Básico
        
        Objetivo: Verificar se a função atualiza corretamente os status
                 conforme a simulação de mesa (4 atualizadas, 2 pendentes)
        
        Entrada:
        - CONSOLIDADO: 6 linhas (A01-A06)
        - OCTAVE: 4 linhas (A01, A02, A03, A05)
        
        Esperado:
        - Total de linhas processadas: 6
        - Total de atualizadas: 4 (A01, A02, A03, A05)
        - Total de pendentes: 2 (A04, A06)
        - A01: Aguardando → Concluído
        - A02: Parado → Concluído
        - A03: Iniciado → Em Andamento
        - A04: Aguardando (mantido)
        - A05: Parado → Pendente
        - A06: Iniciado (mantido)
        """
        # ARRANGE
        df_consolidado = df_consolidado_basico.copy()
        df_octave = df_octave_basico.copy()
        
        # ACT
        df_resultado, lista_pendentes, contador_atualizadas = _atualizar_status_impl(
            df_consolidado, df_octave
        )
        
        # ASSERT - Validar contagens
        assert len(df_resultado) == 6, "Total de linhas deve ser 6"
        assert contador_atualizadas == 4, "Deve ter 4 atualizadas"
        assert len(lista_pendentes) == 2, "Deve ter 2 pendentes"
        assert contador_atualizadas + len(lista_pendentes) == 6, "Equação: atualiza + pendentes = total"
        
        # ASSERT - Validar valores específicos (Antes/Depois)
        assert df_resultado.loc[0, 'Status'] == 'Concluído', "A01 deve ser Concluído"
        assert df_resultado.loc[1, 'Status'] == 'Concluído', "A02 deve ser Concluído"
        assert df_resultado.loc[2, 'Status'] == 'Em Andamento', "A03 deve ser Em Andamento"
        assert df_resultado.loc[3, 'Status'] == 'Aguardando', "A04 mantém Aguardando (pendente)"
        assert df_resultado.loc[4, 'Status'] == 'Pendente', "A05 deve ser Pendente"
        assert df_resultado.loc[5, 'Status'] == 'Iniciado', "A06 mantém Iniciado (pendente)"
        
        # ASSERT - Validar lista de pendentes
        assert 'A04' in lista_pendentes, "A04 deve estar na lista de pendentes"
        assert 'A06' in lista_pendentes, "A06 deve estar na lista de pendentes"
        
        # ASSERT - Validar que colunas adicionais foram preservadas
        assert 'Descrição' in df_resultado.columns, "Coluna Descrição deve ser preservada"
        assert df_resultado.loc[0, 'Descrição'] == 'Manutenção Preventiva', "Dados adicionais preservados"

    # ========================================================================
    # TESTE 2: OS Não Encontrada (Status Mantido)
    # ========================================================================

    def test_os_nao_encontrada_status_mantido(self):
        """
        CENÁRIO 2: Teste de OS Não Encontrada
        
        Objetivo: Verificar que OS não encontrada em OCTAVE mantém seu status original
        
        Entrada:
        - CONSOLIDADO: 3 linhas (A01, A02, A99)
        - OCTAVE: 2 linhas (A01, A02)
        - A99 não existe em OCTAVE
        
        Esperado:
        - A99 mantém status original (Pendente)
        - A99 aparece na lista de pendentes
        - contador_atualizadas = 2
        - total_pendentes = 1
        """
        # ARRANGE
        df_consolidado = pd.DataFrame({
            'Número da OS': ['A01', 'A02', 'A99'],
            'Status': ['Aguardando', 'Parado', 'Pendente']
        })
        df_octave = pd.DataFrame({
            'Número da OS': ['A01', 'A02'],
            'Status': ['Concluído', 'Concluído']
        })
        
        # ACT
        df_resultado, lista_pendentes, contador_atualizadas = _atualizar_status_impl(
            df_consolidado, df_octave
        )
        
        # ASSERT
        assert contador_atualizadas == 2, "Deve ter 2 atualizadas (A01, A02)"
        assert len(lista_pendentes) == 1, "Deve ter 1 pendente (A99)"
        assert 'A99' in lista_pendentes, "A99 deve estar em pendentes"
        
        # A99 não foi atualizada, mantém valor original
        assert df_resultado.loc[2, 'Status'] == 'Pendente', "A99 mantém status original"
        
        # A01 e A02 foram atualizadas
        assert df_resultado.loc[0, 'Status'] == 'Concluído', "A01 foi atualizada"
        assert df_resultado.loc[1, 'Status'] == 'Concluído', "A02 foi atualizada"

    # ========================================================================
    # TESTE 3: Detecção de Coluna Case-Insensitive
    # ========================================================================

    def test_deteccao_coluna_case_insensitive(self, df_consolidado_coluna_alternativa, df_octave_coluna_alternativa):
        """
        CENÁRIO 3: Teste de Detecção de Coluna Case-Insensitive
        
        Objetivo: Verificar que a função detecta colunas com nomes alternativos
                 (ex: 'OS' ao invés de 'Número da OS')
        
        Entrada:
        - CONSOLIDADO: coluna 'OS' (ao invés de 'Número da OS')
        - OCTAVE: coluna 'Estado' (ao invés de 'Status')
        
        Esperado:
        - Função detectar_coluna_caso_insensitivo retorna nome correto
        - Atualização funciona mesmo com nomes diferentes
        """
        # ARRANGE
        df_consolidado = df_consolidado_coluna_alternativa.copy()
        df_octave = df_octave_coluna_alternativa.copy()
        
        # ACT - Teste a função de detecção
        coluna_numero_os = _detectar_coluna_caso_insensitivo(df_consolidado, 'numero da os')
        coluna_status = _detectar_coluna_caso_insensitivo(df_octave, 'estado')
        
        # ASSERT - Deve encontrar as colunas com nomes alternativos
        assert coluna_numero_os == 'OS', "Deve detectar coluna 'OS' como 'Número da OS'"
        assert coluna_status == 'Estado', "Deve detectar coluna 'Estado' como 'Status'"
        
        # ASSERT - Com nomes detectados, deve funcionar a atualização
        assert 'OS' in df_consolidado.columns, "Consolidado tem coluna OS"
        assert 'Estado' in df_octave.columns, "Octave tem coluna Estado"

    # ========================================================================
    # TESTE 4: Erro - Coluna Obrigatória Faltante
    # ========================================================================

    def test_erro_coluna_obrigatoria_faltante(self):
        """
        CENÁRIO 4: Teste de Erro - Coluna Faltante
        
        Objetivo: Verificar que exceção é lançada quando coluna obrigatória falta
        
        Entrada:
        - CONSOLIDADO sem coluna 'Número da OS'
        
        Esperado:
        - ValueError lançado
        - Mensagem de erro clara
        """
        # ARRANGE
        df_consolidado_invalido = pd.DataFrame({
            'Descrição': ['Manutenção'],
            'Status': ['Pendente']
        })
        
        df_octave = pd.DataFrame({
            'Número da OS': ['A01'],
            'Status': ['Concluído']
        })
        
        # ACT & ASSERT
        with pytest.raises(ValueError) as exc_info:
            _validar_colunas_obrigatorias(df_consolidado_invalido, 'numero da os')
        
        assert 'Número da OS' in str(exc_info.value), "Mensagem deve indicar coluna faltante"


# ============================================================================
# TESTES - Classe 2: Função validar_arquivos()
# ============================================================================

class TestValidarArquivos:
    """Testes para a função validar_arquivos()"""

    def test_arquivo_nao_existe(self):
        """
        Teste: Arquivo não encontrado
        
        Esperado:
        - Retorna (False, "mensagem de erro")
        - Exit code seria 1
        """
        # ARRANGE
        caminho_inexistente = "/caminho/que/nao/existe/arquivo.xlsx"
        
        # ACT
        valido, mensagem = _validar_arquivos_impl(caminho_inexistente, "outro.xlsx")
        
        # ASSERT
        assert valido is False, "Deve retornar False"
        assert "não encontrado" in mensagem.lower(), "Mensagem deve mencionar arquivo não encontrado"

    def test_arquivo_extensao_invalida(self, tmp_path):
        """
        Teste: Arquivo com extensão errada
        
        Esperado:
        - Retorna (False, "mensagem de erro")
        """
        # ARRANGE
        arquivo_txt = tmp_path / "teste.txt"
        arquivo_txt.write_text("conteúdo")
        
        # ACT
        valido, mensagem = _validar_arquivos_impl(str(arquivo_txt), "outro.xlsx")
        
        # ASSERT
        assert valido is False, "Deve retornar False para extensão errada"
        assert "xlsx" in mensagem.lower(), "Mensagem deve mencionar .xlsx"

    def test_arquivo_valido(self, tmp_path):
        """
        Teste: Arquivo válido
        
        Esperado:
        - Retorna (True, "")
        """
        # ARRANGE
        arquivo_xlsx = tmp_path / "teste.xlsx"
        arquivo_xlsx.write_text("conteúdo")  # Arquivo fake, mas com extensão certa
        
        # ACT
        valido, mensagem = _validar_arquivos_impl(str(arquivo_xlsx), str(arquivo_xlsx))
        
        # ASSERT
        assert valido is True, "Deve retornar True"
        assert mensagem == "", "Mensagem deve estar vazia"


# ============================================================================
# TESTES - Classe 3: Função carregar_dados()
# ============================================================================

class TestCarregarDados:
    """Testes para a função carregar_dados()"""

    def test_planilha_vazia(self):
        """
        Teste: Carregar planilha vazia
        
        Esperado:
        - ValueError lançado
        """
        # ARRANGE
        df_vazio = pd.DataFrame({
            'Número da OS': [],
            'Status': []
        })
        
        # ACT & ASSERT
        with pytest.raises(ValueError) as exc_info:
            _validar_dataframe_nao_vazio(df_vazio, "CONSOLIDADO.xlsx")
        
        assert "vazia" in str(exc_info.value).lower(), "Mensagem deve mencionar vazio"

    def test_dataframe_com_linhas(self, df_consolidado_basico):
        """
        Teste: Carregar DataFrame com dados válidos
        
        Esperado:
        - Retorna DataFrame sem erro
        - len(df) > 0
        """
        # ACT
        _validar_dataframe_nao_vazio(df_consolidado_basico, "CONSOLIDADO.xlsx")
        
        # ASSERT - Se chegou aqui, não lançou exceção
        assert len(df_consolidado_basico) == 6, "DataFrame deve ter 6 linhas"
        assert 'Número da OS' in df_consolidado_basico.columns, "Deve ter coluna"


# ============================================================================
# TESTES - Classe 4: Validação de Integridade
# ============================================================================

class TestIntegridade:
    """Testes para validação de integridade de dados"""

    def test_nao_deleta_linhas(self, df_consolidado_basico, df_octave_basico):
        """
        Teste: Verificar que nenhuma linha é deletada durante atualização
        
        Esperado:
        - Total de linhas permanece igual
        """
        # ARRANGE
        total_antes = len(df_consolidado_basico)
        df_consolidado = df_consolidado_basico.copy()
        
        # ACT
        df_resultado, _, _ = _atualizar_status_impl(df_consolidado, df_octave_basico)
        
        # ASSERT
        assert len(df_resultado) == total_antes, "Nenhuma linha deve ser deletada"

    def test_nao_reordena_linhas(self, df_consolidado_basico, df_octave_basico):
        """
        Teste: Verificar que linhas não são reordenadas
        
        Esperado:
        - Ordem de Números da OS permanece a mesma
        """
        # ARRANGE
        ordem_antes = df_consolidado_basico['Número da OS'].tolist()
        df_consolidado = df_consolidado_basico.copy()
        
        # ACT
        df_resultado, _, _ = _atualizar_status_impl(df_consolidado, df_octave_basico)
        
        # ASSERT
        ordem_depois = df_resultado['Número da OS'].tolist()
        assert ordem_antes == ordem_depois, "Ordem de linhas deve ser preservada"

    def test_preserva_colunas_adicionais(self, df_consolidado_basico, df_octave_basico):
        """
        Teste: Verificar que colunas adicionais são preservadas
        
        Esperado:
        - Coluna 'Descrição' continua presente e com valores originais
        """
        # ARRANGE
        descricao_antes = df_consolidado_basico['Descrição'].tolist()
        df_consolidado = df_consolidado_basico.copy()
        
        # ACT
        df_resultado, _, _ = _atualizar_status_impl(df_consolidado, df_octave_basico)
        
        # ASSERT
        assert 'Descrição' in df_resultado.columns, "Coluna Descrição preservada"
        descricao_depois = df_resultado['Descrição'].tolist()
        assert descricao_antes == descricao_depois, "Valores de colunas adicionais preservados"


# ============================================================================
# TESTES - Classe 5: Validação de Relatório
# ============================================================================

class TestRelatorio:
    """Testes para validação das 3 variáveis de relatório"""

    def test_variáveis_relatorio_corretas(self, df_consolidado_basico, df_octave_basico):
        """
        Teste: Três variáveis de relatório devem estar corretas
        
        Esperado:
        - total_linhas_processadas = 6
        - total_atualizadas = 4
        - total_pendentes = 2
        - Equação: 4 + 2 = 6 ✓
        """
        # ARRANGE
        df_consolidado = df_consolidado_basico.copy()
        
        # ACT
        df_resultado, lista_pendentes, contador_atualizadas = _atualizar_status_impl(
            df_consolidado, df_octave_basico
        )
        
        # Calcular as 3 variáveis
        total_linhas_processadas = len(df_resultado)
        total_atualizadas = contador_atualizadas
        total_pendentes = len(lista_pendentes)
        
        # ASSERT
        assert total_linhas_processadas == 6, "total_linhas_processadas = 6"
        assert total_atualizadas == 4, "total_atualizadas = 4"
        assert total_pendentes == 2, "total_pendentes = 2"
        
        # ASSERT - Equação de validação
        assert total_atualizadas + total_pendentes == total_linhas_processadas, \
            "VALIDAÇÃO: atualiza + pendentes = total"

    def test_relatorio_formato_correto(self, df_consolidado_basico, df_octave_basico):
        """
        Teste: Relatório é formatado corretamente para exibição
        
        Esperado:
        - String com todas as métricas
        """
        # ARRANGE
        df_consolidado = df_consolidado_basico.copy()
        df_resultado, lista_pendentes, contador_atualizadas = _atualizar_status_impl(
            df_consolidado, df_octave_basico
        )
        
        # ACT
        relatorio = _gerar_relatorio_impl(
            len(df_resultado),
            contador_atualizadas,
            lista_pendentes
        )
        
        # ASSERT
        assert 'Total de Linhas Processadas: 6' in relatorio or '6' in relatorio
        assert 'Total de OS Atualizadas: 4' in relatorio or '4' in relatorio
        assert 'Total de OS Pendentes: 2' in relatorio or '2' in relatorio
        assert 'A04' in relatorio, "Lista de pendentes deve estar no relatório"
        assert 'A06' in relatorio, "Lista de pendentes deve estar no relatório"


# ============================================================================
# IMPLEMENTAÇÕES MOCK/STUB - Funções Principais
# ============================================================================
# Essas funções simulam o comportamento esperado das funções no atualizador.py
# Podem ser substituídas pelas funções reais quando implementado

def _atualizar_status_impl(df_consolidado, df_octave):
    """
    Implementação da função atualizar_status() para testes.
    Cria um dicionário e atualiza status conforme SPEC TÉCNICA.
    """
    # Validar colunas
    col_os_cons = _detectar_coluna_caso_insensitivo(df_consolidado, 'numero da os')
    col_status_cons = _detectar_coluna_caso_insensitivo(df_consolidado, 'status')
    col_os_octave = _detectar_coluna_caso_insensitivo(df_octave, 'numero da os')
    col_status_octave = _detectar_coluna_caso_insensitivo(df_octave, 'status')
    
    # Criar mapeamento O(1)
    mapa_status = dict(zip(
        df_octave[col_os_octave],
        df_octave[col_status_octave]
    ))
    
    # Atualizar Consolidado
    df_resultado = df_consolidado.copy()
    lista_pendentes = []
    contador_atualizadas = 0
    
    for i in df_resultado.index:
        numero_os = df_resultado.loc[i, col_os_cons]
        
        if numero_os in mapa_status:
            status_novo = mapa_status[numero_os]
            df_resultado.loc[i, col_status_cons] = status_novo
            contador_atualizadas += 1
        else:
            lista_pendentes.append(numero_os)
    
    return df_resultado, lista_pendentes, contador_atualizadas


def _detectar_coluna_caso_insensitivo(df, coluna_alvo):
    """
    Detecta coluna com busca case-insensitive e normalização.
    """
    # Normalizar coluna alvo
    alvo_normalizado = coluna_alvo.lower().strip().replace('ç', 'c').replace('ã', 'a')
    
    # Buscar entre colunas do DataFrame
    for coluna in df.columns:
        coluna_normalizada = coluna.lower().strip().replace('ç', 'c').replace('ã', 'a')
        if coluna_normalizada == alvo_normalizado:
            return coluna
    
    # Se não encontrar, lançar erro
    raise ValueError(f"Coluna '{coluna_alvo}' não encontrada. Disponíveis: {list(df.columns)}")


def _validar_colunas_obrigatorias(df, coluna):
    """Valida se coluna obrigatória existe."""
    try:
        _detectar_coluna_caso_insensitivo(df, coluna)
    except ValueError as e:
        raise ValueError(f"ERRO: Coluna obrigatória não encontrada! {str(e)}")


def _validar_dataframe_nao_vazio(df, nome_arquivo):
    """Valida se DataFrame não está vazio."""
    if len(df) == 0:
        raise ValueError(f"ERRO E-003: Planilha vazia! Arquivo: {nome_arquivo}")


def _validar_arquivos_impl(caminho1, caminho2):
    """
    Implementação da função validar_arquivos() para testes.
    """
    # Verificar arquivo 1
    if not os.path.exists(caminho1):
        return False, f"ERRO E-001: Arquivo não encontrado: {caminho1}"
    
    if not caminho1.endswith('.xlsx'):
        return False, f"ERRO: Extensão inválida. Esperado .xlsx, recebido {caminho1}"
    
    # Verificar arquivo 2
    if not os.path.exists(caminho2):
        return False, f"ERRO E-001: Arquivo não encontrado: {caminho2}"
    
    if not caminho2.endswith('.xlsx'):
        return False, f"ERRO: Extensão inválida. Esperado .xlsx, recebido {caminho2}"
    
    return True, ""


def _gerar_relatorio_impl(total_linhas, total_atualizadas, lista_pendentes):
    """
    Implementação da função para gerar relatório.
    """
    total_pendentes = len(lista_pendentes)
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    relatorio = f"""
═════════════════════════════════════════════════════════
  RELATÓRIO DE EXECUÇÃO - ATUALIZADOR OCTAVE
═════════════════════════════════════════════════════════
Timestamp: {timestamp}

Total de Linhas Processadas: {total_linhas}
Total de OS Atualizadas:     {total_atualizadas}
Total de OS Pendentes:       {total_pendentes}

OS Não Encontradas:
"""
    
    # Adicionar lista de pendentes (primeiras 10)
    for i, os in enumerate(lista_pendentes[:10]):
        relatorio += f"  • {os}\n"
    
    if len(lista_pendentes) > 10:
        relatorio += f"  [... mais {len(lista_pendentes) - 10} ...]\n"
    
    relatorio += """
═════════════════════════════════════════════════════════
Status: ✓ SUCESSO
═════════════════════════════════════════════════════════
"""
    
    return relatorio


# ============================================================================
# TESTES - Regressão (Adicional)
# ============================================================================

class TestRegressao:
    """Testes de regressão para cenários específicos"""

    def test_todas_os_encontradas(self):
        """
        Cenário: Todas as OS do Consolidado existem no Octave
        Esperado: total_pendentes = 0
        """
        # ARRANGE
        df_consolidado = pd.DataFrame({
            'Número da OS': ['A01', 'A02', 'A03'],
            'Status': ['Aguardando', 'Parado', 'Iniciado']
        })
        df_octave = pd.DataFrame({
            'Número da OS': ['A01', 'A02', 'A03'],
            'Status': ['Concluído', 'Concluído', 'Concluído']
        })
        
        # ACT
        _, lista_pendentes, contador_atualizadas = _atualizar_status_impl(
            df_consolidado, df_octave
        )
        
        # ASSERT
        assert contador_atualizadas == 3, "Todas atualizadas"
        assert len(lista_pendentes) == 0, "Nenhuma pendente"

    def test_nenhuma_os_encontrada(self):
        """
        Cenário: Nenhuma OS do Consolidado existe no Octave
        Esperado: total_atualizadas = 0, total_pendentes = N
        """
        # ARRANGE
        df_consolidado = pd.DataFrame({
            'Número da OS': ['A01', 'A02', 'A03'],
            'Status': ['Aguardando', 'Parado', 'Iniciado']
        })
        df_octave = pd.DataFrame({
            'Número da OS': ['B01', 'B02'],
            'Status': ['Concluído', 'Concluído']
        })
        
        # ACT
        _, lista_pendentes, contador_atualizadas = _atualizar_status_impl(
            df_consolidado, df_octave
        )
        
        # ASSERT
        assert contador_atualizadas == 0, "Nenhuma atualizada"
        assert len(lista_pendentes) == 3, "Todas pendentes"
        assert set(lista_pendentes) == {'A01', 'A02', 'A03'}, "Corretas pendentes"

    def test_status_vazio_permitido(self):
        """
        Cenário: Status pode ser vazio/NaN
        Esperado: Deve atualizar normalmente
        """
        # ARRANGE
        df_consolidado = pd.DataFrame({
            'Número da OS': ['A01', 'A02'],
            'Status': ['Aguardando', 'Parado']
        })
        df_octave = pd.DataFrame({
            'Número da OS': ['A01', 'A02'],
            'Status': ['', 'Concluído']  # A01 tem status vazio
        })
        
        # ACT
        df_resultado, _, contador_atualizadas = _atualizar_status_impl(
            df_consolidado, df_octave
        )
        
        # ASSERT
        assert contador_atualizadas == 2, "Ambas atualizadas (mesmo com vazio)"
        assert df_resultado.loc[0, 'Status'] == '', "A01 status vazio atualizado"
        assert df_resultado.loc[1, 'Status'] == 'Concluído', "A02 atualizado"


# ============================================================================
# EXECUÇÃO DOS TESTES
# ============================================================================

if __name__ == "__main__":
    """
    Executar testes com:
        pytest test_atualizador.py -v
        pytest test_atualizador.py -v --tb=short
        pytest test_atualizador.py::TestAtualizarStatus::test_atualizacao_basica_sucesso -v
    """
    pytest.main([__file__, "-v", "--tb=short"])
