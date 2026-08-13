# SPEC TÉCNICA - Automação de Atualização de Preventivas (Octave)

**Versão:** 2.0  
**Data:** 13/08/2026  
**Status:** Especificação para Implementação  
**Tipo:** Engenharia de Software  
**Origem:** PRD v2.0

---

## Visão Geral

Especificação técnica detalhada para desenvolvimento de `atualizador.py`, um script Python que automatiza a sincronização de status de atividades preventivas entre dois arquivos Excel: `DADOS_OCTAVE.xlsx` (origem) e `CONSOLIDADO.xlsx` (destino).

---

## 1. Estrutura de Diretórios

### Árvore de Arquivos

```
00. ATUALIZAR/
├── atualizador.py              # Script principal em Python
├── DADOS_OCTAVE.xlsx           # Arquivo de entrada (dados do Octave)
├── CONSOLIDADO.xlsx            # Arquivo entrada/saída (será sobrescrito)
└── atualizador.exe             # [Gerado após PyInstaller]
```

### Localização e Caminhos

- **Diretório de Trabalho:** `00. ATUALIZAR/` (mesmo nível que os arquivos `.xlsx`)
- **Path Relativo:** O script deve usar `os.path.dirname(os.path.abspath(__file__))` para obter o caminho base
- **Arquivos de Entrada:**
  - `DADOS_OCTAVE.xlsx` → Localização: `./DADOS_OCTAVE.xlsx` (relativo ao script)
  - `CONSOLIDADO.xlsx` → Localização: `./CONSOLIDADO.xlsx` (relativo ao script)
- **Arquivo de Saída:**
  - `CONSOLIDADO.xlsx` → Será **sobrescrito** no mesmo local

### Nota Importante

O script **não** deve criar subdirectórios. Todos os arquivos ficam na mesma pasta raiz `00. ATUALIZAR/`.

---

## 2. Estrutura de Dados (Pandas)

### 2.1 DataFrames Esperados

#### DataFrame 1: `df_consolidado`
**Origem:** `CONSOLIDADO.xlsx`  
**Tipo:** `pandas.DataFrame`  
**Descrição:** Planilha mestra que será atualizada.

| Coluna | Tipo de Dado | Obrigatório | Comportamento |
|--------|--------------|-------------|---------------|
| `Número da OS` | `object` (string) | ✅ SIM | Chave primária, identificador único não-nulo |
| `Status` | `object` (string) | ✅ SIM | Campo alvo para atualização (pode estar vazio) |
| Outras colunas | variável | ❌ NÃO | Preservadas intactas, não sofrem alteração |

**Exemplo de Estrutura:**
```
   Número da OS     Status      Descrição  Data_Criação
0    OS-001001   Pendente   Manutenção...  2026-08-01
1    OS-001002   Concluído  Inspeção...    2026-08-02
2    OS-001003   Aguardando Teste...      2026-08-03
...
N    OS-005000   Parado     Reparo...      2026-08-13
```

---

#### DataFrame 2: `df_octave`
**Origem:** `DADOS_OCTAVE.xlsx`  
**Tipo:** `pandas.DataFrame`  
**Descrição:** Arquivo de origem com dados atualizados do Octave.

| Coluna | Tipo de Dado | Obrigatório | Comportamento |
|--------|--------------|-------------|---------------|
| `Número da OS` | `object` (string) | ✅ SIM | Chave para busca |
| `Status` | `object` (string) | ✅ SIM | Valor que será propagado |
| Outras colunas | variável | ❌ NÃO | Ignoradas, não usadas |

### 2.2 Identificação de Colunas

O script deve ser **flexível** e resistente a variações de nome de coluna. Implementar busca case-insensitive com normalização.

**Para coluna "Número da OS":**
```
Variações aceitas:
  - "Número da OS"
  - "numero da os"
  - "Numero da OS"
  - "Nº da OS"
  - "n° da os"
  - "OS"
  - "Num_OS"
```

**Para coluna "Status":**
```
Variações aceitas:
  - "Status"
  - "status"
  - "Estado"
  - "Situação"
```

**Processo de Detecção:**
1. Normalizar: `coluna.strip().lower().replace("ç", "c").replace("ã", "a")`
2. Buscar correspondência exata (após normalização)
3. Se não encontrar, lançar exceção `ValueError` com mensagem clara

---

## 3. Lógica de Negócio em Código

### 3.1 Algoritmo Principal - Mapeamento O(1)

**Objetivo:** Usar Dict Python para busca rápida de Status

#### Passo 1: Criar Dicionário de Mapeamento

```
Entrada: df_octave (DataFrame)
Saída: mapa_status (dict)

Pseudocódigo:
┌─────────────────────────────────────────┐
│ mapa_status = {}                        │
│                                          │
│ PARA CADA linha i EM df_octave:         │
│   numero_os = df_octave.loc[i, 'Número da OS'] │
│   status = df_octave.loc[i, 'Status']   │
│   mapa_status[numero_os] = status       │
│                                          │
│ RETORNAR mapa_status                    │
└─────────────────────────────────────────┘
```

**Propriedades:**
- Tipo: `dict[str, str]`
- Tamanho: ~M entradas (M = linhas do Octave)
- Complexidade: O(M) para criar, **O(1) para buscar**
- Último valor vence se houver duplicatas

**Exemplo Resultante:**
```python
mapa_status = {
    "OS-001001": "Concluído",
    "OS-001002": "Concluído",
    "OS-001005": "Em Andamento",
    ...
}
```

---

#### Passo 2: Atualizar DataFrame de Consolidado

```
Entrada: df_consolidado (DataFrame), mapa_status (dict)
Saída: df_consolidado (modificado), lista_pendentes (list), contador

Pseudocódigo:
┌─────────────────────────────────────────────────────┐
│ lista_pendentes = []                                │
│ contador_atualizadas = 0                            │
│                                                      │
│ PARA CADA índice i EM df_consolidado.index:        │
│   numero_os = df_consolidado.loc[i, 'Número da OS']│
│                                                      │
│   SE numero_os ESTÁ EM mapa_status:    [O(1)]      │
│     status_novo = mapa_status[numero_os]           │
│     df_consolidado.loc[i, 'Status'] = status_novo  │
│     contador_atualizadas += 1                       │
│                                                      │
│   SENÃO:                                            │
│     lista_pendentes.append(numero_os)               │
│     # Mantém status original                        │
│                                                      │
│ RETORNAR df_consolidado, lista_pendentes,          │
│         contador_atualizadas                         │
└─────────────────────────────────────────────────────┘
```

**Saídas:**
- `df_consolidado`: DataFrame modificado com Status atualizado
- `lista_pendentes`: Lista de Números de OS não encontrados
- `contador_atualizadas`: Inteiro com total de atualizações

**Exemplo de Resultado:**
```python
# ANTES:
   Número da OS     Status
0    OS-001001   Pendente
1    OS-001002   Concluído
2    OS-001003   Aguardando

# DEPOIS:
   Número da OS     Status
0    OS-001001   Concluído    ← Atualizada
1    OS-001002   Concluído    ← Mantida
2    OS-001003   Aguardando   ← Pendente (não encontrada)

lista_pendentes = ["OS-001003"]
contador_atualizadas = 1
```

---

### 3.2 Complexidade Algorítmica

| Operação | Complexidade | Justificativa |
|----------|--------------|---------------|
| Criar `mapa_status` | O(M) | Uma passagem pelo Octave |
| Busca por Número OS | O(1) | Lookup em dict Python |
| Atualizar `df_consolidado` | O(N) | Uma passagem pelo Consolidado |
| **Total** | **O(N + M)** | Linear |

**Performance Esperada:**
- 1.000 linhas: < 0,1 seg
- 5.000 linhas: < 0,5 seg
- 50.000 linhas: < 5,0 seg

---

## 4. Tratamento de Erros

### 4.1 E-001: Arquivo Não Encontrado

**Condição:**
```
SE arquivo (CONSOLIDADO.xlsx OU DADOS_OCTAVE.xlsx) NÃO EXISTE
```

**Mensagem Exibida:**
```
┌───────────────────────────────────────┐
│ ERRO: Arquivo não encontrado!         │
│                                        │
│ Arquivo: CONSOLIDADO.xlsx             │
│ Caminho: C:\00. ATUALIZAR\...         │
│                                        │
│ Certifique-se de que o arquivo        │
│ está no mesmo diretório do script.    │
└───────────────────────────────────────┘
```

**Exit Code:** 1

---

### 4.2 E-002: Coluna Obrigatória Faltante

**Condição:**
```
SE coluna "Número da OS" OU "Status" NÃO EXISTE
```

**Mensagem Exibida:**
```
┌────────────────────────────────────────────┐
│ ERRO: Coluna obrigatória não encontrada!  │
│                                             │
│ Arquivo: DADOS_OCTAVE.xlsx                │
│ Coluna Esperada: "Número da OS"           │
│                                             │
│ Colunas Disponíveis:                       │
│   - Descrição                              │
│   - Responsável                            │
│   - OS                                     │
└────────────────────────────────────────────┘
```

**Exit Code:** 2

---

### 4.3 E-003: Planilha Vazia

**Condição:**
```
SE DataFrame tem 0 linhas
```

**Exit Code:** 3

---

### 4.4 E-004: Arquivo Excel Inválido

**Condição:**
```
SE arquivo não é um Excel válido (.xlsx)
```

**Exit Code:** 4

---

### 4.5 E-005: Erro de Escrita / Permissão

**Condição:**
```
SE arquivo está aberto em outro processo
   OU disco cheio
   OU sem permissão de escrita
```

**Exit Code:** 5

---

### 4.6 E-099: Erro Inesperado

**Para exceções não previstas**

**Exit Code:** 99

---

## 5. Relatório de Saída

### 5.1 Três Variáveis Obrigatórias

#### Variável 1: `total_linhas_processadas`
**Tipo:** `int`  
**Cálculo:** `len(df_consolidado)`  
**Descrição:** Total de linhas lidas em CONSOLIDADO  
**Exemplo:** `1250`

#### Variável 2: `total_atualizadas`
**Tipo:** `int`  
**Cálculo:** Contagem de OS encontradas em mapa_status  
**Descrição:** Total de Status atualizado com sucesso  
**Exemplo:** `1200`

#### Variável 3: `total_pendentes`
**Tipo:** `int`  
**Cálculo:** `len(lista_pendentes)` ou `total_linhas_processadas - total_atualizadas`  
**Descrição:** Total de OS NÃO encontradas no Octave  
**Exemplo:** `50`

---

### 5.2 Validação Antes de Exibir

```python
assert total_atualizadas + total_pendentes == total_linhas_processadas, \
    "ERRO: Contagem não coincide!"
```

Se falhar → Não salvar arquivo, abortar, Exit Code 99

---

### 5.3 Formato de Saída no Terminal

```
═══════════════════════════════════════════════════════
  RELATÓRIO DE EXECUÇÃO - ATUALIZADOR OCTAVE
═══════════════════════════════════════════════════════
Timestamp: 13/08/2026 14:30:48

Total de Linhas Processadas: {total_linhas_processadas}
Total de OS Atualizadas:     {total_atualizadas}
Total de OS Pendentes:       {total_pendentes}

OS Não Encontradas:
  • OS-001001
  • OS-001002
  • OS-001003
  [... mais ...]

═══════════════════════════════════════════════════════
Pressione ENTER para sair...
═══════════════════════════════════════════════════════
```

---

## 6. Estrutura do Código - Assinatura das Funções

### 6.1 Função Principal 1: `validar_arquivos()`

```python
def validar_arquivos(
    caminho_consolidado: str,
    caminho_octave: str
) -> tuple[bool, str]:
    """
    Valida se os arquivos Excel necessários existem.
    
    Parâmetros:
    -----------
    caminho_consolidado : str
        Caminho relativo/absoluto de CONSOLIDADO.xlsx
    
    caminho_octave : str
        Caminho relativo/absoluto de DADOS_OCTAVE.xlsx
    
    Retorno:
    --------
    tuple[bool, str]
        (True, "") se válido
        (False, "mensagem de erro") caso contrário
    
    Responsabilidades:
    - Verificar existência de arquivos
    - Verificar extensão .xlsx
    - Verificar se não estão vazios
    - Retornar mensagem de erro específica
    """
    pass
```

---

### 6.2 Função Principal 2: `carregar_dados()`

```python
def carregar_dados(
    caminho_consolidado: str,
    caminho_octave: str
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    Carrega os dois arquivos Excel em DataFrames Pandas.
    
    Parâmetros:
    -----------
    caminho_consolidado : str
        Caminho para CONSOLIDADO.xlsx
    
    caminho_octave : str
        Caminho para DADOS_OCTAVE.xlsx
    
    Retorno:
    --------
    tuple[pd.DataFrame, pd.DataFrame]
        (df_consolidado, df_octave)
    
    Exceções:
    ---------
    FileNotFoundError: Arquivo não existe
    ValueError: Planilha vazia ou coluna faltante
    InvalidFileException: Excel corrompido
    
    Responsabilidades:
    - Ler primeira aba de cada arquivo
    - Detectar automaticamente colunas (case-insensitive)
    - Validar que colunas obrigatórias existem
    - Validar que DataFrames não estão vazios
    - Usar encoding UTF-8
    """
    pass
```

---

### 6.3 Função Principal 3: `atualizar_status()`

```python
def atualizar_status(
    df_consolidado: pd.DataFrame,
    df_octave: pd.DataFrame
) -> tuple[pd.DataFrame, list[str], int]:
    """
    Realiza o mapeamento e atualização de status.
    
    Parâmetros:
    -----------
    df_consolidado : pd.DataFrame
        DataFrame com dados a atualizar
        Deve conter: "Número da OS", "Status"
    
    df_octave : pd.DataFrame
        DataFrame com dados de origem
        Deve conter: "Número da OS", "Status"
    
    Retorno:
    --------
    tuple[pd.DataFrame, list[str], int]
        (df_consolidado_modificado, lista_pendentes, contador_atualizadas)
    
    Responsabilidades:
    - Criar dict {OS: Status} com O(1) lookup
    - Iterar sobre df_consolidado
    - Atualizar Status se OS encontrado
    - Coletar OS não encontradas
    - Preservar estrutura (sem deletar/reordenar linhas)
    - Manter colunas adicionais intactas
    
    Algoritmo:
    1. Criar mapa_status = dict(zip(df_octave['Número da OS'], df_octave['Status']))
    2. Para cada linha em df_consolidado:
       - Se numero_os em mapa_status: atualizar + contar
       - Senão: adicionar a pendentes
    3. Retornar (df_modificado, pendentes, contador)
    """
    pass
```

---

### 6.4 Funções Auxiliares Recomendadas

#### `detectar_coluna_caso_insensitivo(df, coluna_alvo)`
```python
def detectar_coluna_caso_insensitivo(
    df: pd.DataFrame,
    coluna_alvo: str
) -> str:
    """
    Detecta nome real da coluna com busca case-insensitive.
    
    Retorna: nome exato da coluna em df.columns
    Exceção: ValueError se não encontrar
    """
    pass
```

#### `salvar_consolidado(df, caminho_saida)`
```python
def salvar_consolidado(
    df_consolidado: pd.DataFrame,
    caminho_saida: str
) -> bool:
    """
    Salva DataFrame no Excel, sobrescrevendo original.
    
    Retorna: True se sucesso, False se falhar
    Usa openpyxl como engine
    """
    pass
```

#### `exibir_relatorio(total_linhas, total_atualizadas, lista_pendentes)`
```python
def exibir_relatorio(
    total_linhas: int,
    total_atualizadas: int,
    lista_pendentes: list[str]
) -> None:
    """
    Exibe relatório formatado no terminal.
    
    Comportamento:
    - Imprime cabeçalho e métricas
    - Lista primeiras 10 OS pendentes
    - Aguarda ENTER antes de finalizar
    """
    pass
```

---

### 6.5 Fluxo do `main()`

```python
def main():
    """Orquestra fluxo completo de execução."""
    
    try:
        # 1. VALIDAR
        valido, msg = validar_arquivos("./CONSOLIDADO.xlsx", "./DADOS_OCTAVE.xlsx")
        if not valido:
            exibir_erro(msg)
            exit(1)
        
        # 2. CARREGAR
        df_consolidado, df_octave = carregar_dados(
            "./CONSOLIDADO.xlsx", "./DADOS_OCTAVE.xlsx"
        )
        
        # 3. ATUALIZAR
        df_consolidado, pendentes, atualizadas = atualizar_status(
            df_consolidado, df_octave
        )
        
        # 4. VALIDAR INTEGRIDADE
        total = len(df_consolidado)
        assert atualizadas + len(pendentes) == total
        
        # 5. SALVAR
        sucesso = salvar_consolidado(df_consolidado, "./CONSOLIDADO.xlsx")
        if not sucesso:
            exibir_erro("Erro ao salvar!")
            exit(5)
        
        # 6. RELATAR
        exibir_relatorio(total, atualizadas, pendentes)
        
    except FileNotFoundError as e:
        exibir_erro(f"Arquivo não encontrado: {e}")
        exit(1)
    except ValueError as e:
        exibir_erro(f"Erro de dados: {e}")
        exit(2)
    except PermissionError as e:
        exibir_erro(f"Erro de permissão: {e}")
        exit(5)
    except Exception as e:
        exibir_erro(f"Erro inesperado: {e}")
        exit(99)


if __name__ == "__main__":
    main()
```

---

## 7. Dependências Python

```
pandas>=1.3.0
openpyxl>=3.6.0
```

**Built-in:**
- `os`
- `sys`
- `datetime`

---

## 8. Notas Técnicas

1. **Case-Sensitivity:** Implementar detecção case-insensitive para colunas
2. **Valores Nulos:** NaN em Status é permitido; "Número da OS" não pode ser nulo
3. **Encoding:** UTF-8 obrigatório (suporta acentos portugueses)
4. **Índice:** Nunca manipular índice, apenas valores de células
5. **Exit Codes:** 1, 2, 3, 4, 5, 99
6. **Paths:** Usar `os.path` para compatibilidade Windows
7. **in-place:** Modificar df_consolidado sem criar cópia

---

**FIM DA ESPECIFICAÇÃO TÉCNICA**
