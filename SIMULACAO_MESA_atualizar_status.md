# SIMULAÇÃO DE MESA (TABLETOP VALIDATION)
## Função: `atualizar_status()`

**Data:** 13/08/2026  
**Objetivo:** Validar o algoritmo de atualização com dados fictícios  
**Método:** Simulação passo-a-passo linha por linha

---

## 1. Dados de Entrada

### 1.1 DataFrame: `DADOS_OCTAVE` (Origem)

**Arquivo:** `DADOS_OCTAVE.xlsx`  
**Descrição:** Dados mais recentes do sistema Octave  
**Total de linhas:** 4

```
   Número da OS         Status
0       A01           Concluído
1       A02           Concluído
2       A03           Em Andamento
3       A05           Pendente
```

| Número da OS | Status | Observação |
|---|---|---|
| A01 | Concluído | Status novo |
| A02 | Concluído | Status novo |
| A03 | Em Andamento | Status novo |
| A05 | Pendente | Status novo |

---

### 1.2 DataFrame: `CONSOLIDADO` (Destino - Antes)

**Arquivo:** `CONSOLIDADO.xlsx`  
**Descrição:** Planilha mestra que será atualizada  
**Total de linhas:** 6

```
   Número da OS    Status     Descrição
0       A01        Aguardando Manutenção Preventiva
1       A02        Parado     Inspeção Técnica
2       A03        Iniciado   Teste de Componentes
3       A04        Aguardando Reparo Hidráulico
4       A05        Parado     Verificação Elétrica
5       A06        Iniciado   Calibração de Sensores
```

| Número da OS | Status (Antigo) | Descrição |
|---|---|---|
| A01 | Aguardando | Manutenção Preventiva |
| A02 | Parado | Inspeção Técnica |
| A03 | Iniciado | Teste de Componentes |
| A04 | Aguardando | Reparo Hidráulico |
| A05 | Parado | Verificação Elétrica |
| A06 | Iniciado | Calibração de Sensores |

---

## 2. Execução do Algoritmo

### 2.1 Fase 1: Criar Mapa de Status (Dict)

**Operação:** `mapa_status = {}`

```python
mapa_status = {}

PARA cada linha em df_octave:
    mapa_status[df_octave.loc[i, 'Número da OS']] = df_octave.loc[i, 'Status']
```

**Resultado:**
```python
mapa_status = {
    "A01": "Concluído",
    "A02": "Concluído",
    "A03": "Em Andamento",
    "A05": "Pendente"
}
```

**Propriedades:**
- Tamanho: 4 entradas
- Tipo: `dict[str, str]`
- Complexidade: O(1) para lookup

---

### 2.2 Fase 2: Atualizar CONSOLIDADO Linha por Linha

**Operação:** Iterar sobre `df_consolidado` e buscar cada OS em `mapa_status`

#### Linha 0: Número da OS = "A01"

```
numero_os = df_consolidado.loc[0, 'Número da OS'] = "A01"

SE "A01" ESTÁ EM mapa_status? SIM ✓

status_novo = mapa_status["A01"] = "Concluído"

df_consolidado.loc[0, 'Status'] = "Concluído"

RESULTADO: ✅ ATUALIZADA
contador_atualizadas += 1  → contador = 1
```

**Antes:**
| Número da OS | Status | 
|---|---|
| A01 | Aguardando |

**Depois:**
| Número da OS | Status |
|---|---|
| A01 | **Concluído** ← Atualizada |

---

#### Linha 1: Número da OS = "A02"

```
numero_os = df_consolidado.loc[1, 'Número da OS'] = "A02"

SE "A02" ESTÁ EM mapa_status? SIM ✓

status_novo = mapa_status["A02"] = "Concluído"

df_consolidado.loc[1, 'Status'] = "Concluído"

RESULTADO: ✅ ATUALIZADA
contador_atualizadas += 1  → contador = 2
```

**Antes:**
| Número da OS | Status |
|---|---|
| A02 | Parado |

**Depois:**
| Número da OS | Status |
|---|---|
| A02 | **Concluído** ← Atualizada |

---

#### Linha 2: Número da OS = "A03"

```
numero_os = df_consolidado.loc[2, 'Número da OS'] = "A03"

SE "A03" ESTÁ EM mapa_status? SIM ✓

status_novo = mapa_status["A03"] = "Em Andamento"

df_consolidado.loc[2, 'Status'] = "Em Andamento"

RESULTADO: ✅ ATUALIZADA
contador_atualizadas += 1  → contador = 3
```

**Antes:**
| Número da OS | Status |
|---|---|
| A03 | Iniciado |

**Depois:**
| Número da OS | Status |
|---|---|
| A03 | **Em Andamento** ← Atualizada |

---

#### Linha 3: Número da OS = "A04"

```
numero_os = df_consolidado.loc[3, 'Número da OS'] = "A04"

SE "A04" ESTÁ EM mapa_status? NÃO ✗

# Status mantém valor original

df_consolidado.loc[3, 'Status'] = "Aguardando"  (sem alteração)

RESULTADO: ⏸️ PENDENTE
lista_pendentes.append("A04")  → lista = ["A04"]
```

**Antes:**
| Número da OS | Status |
|---|---|
| A04 | Aguardando |

**Depois:**
| Número da OS | Status |
|---|---|
| A04 | Aguardando ← Mantida (Pendente) |

**Motivo:** OS "A04" não existe em DADOS_OCTAVE

---

#### Linha 4: Número da OS = "A05"

```
numero_os = df_consolidado.loc[4, 'Número da OS'] = "A05"

SE "A05" ESTÁ EM mapa_status? SIM ✓

status_novo = mapa_status["A05"] = "Pendente"

df_consolidado.loc[4, 'Status'] = "Pendente"

RESULTADO: ✅ ATUALIZADA
contador_atualizadas += 1  → contador = 4
```

**Antes:**
| Número da OS | Status |
|---|---|
| A05 | Parado |

**Depois:**
| Número da OS | Status |
|---|---|
| A05 | **Pendente** ← Atualizada |

---

#### Linha 5: Número da OS = "A06"

```
numero_os = df_consolidado.loc[5, 'Número da OS'] = "A06"

SE "A06" ESTÁ EM mapa_status? NÃO ✗

# Status mantém valor original

df_consolidado.loc[5, 'Status'] = "Iniciado"  (sem alteração)

RESULTADO: ⏸️ PENDENTE
lista_pendentes.append("A06")  → lista = ["A04", "A06"]
```

**Antes:**
| Número da OS | Status |
|---|---|
| A06 | Iniciado |

**Depois:**
| Número da OS | Status |
|---|---|
| A06 | Iniciado ← Mantida (Pendente) |

**Motivo:** OS "A06" não existe em DADOS_OCTAVE

---

## 3. Resultado Final

### 3.1 DataFrame: `CONSOLIDADO` (Após Atualização)

```
   Número da OS    Status           Descrição
0       A01        Concluído        Manutenção Preventiva
1       A02        Concluído        Inspeção Técnica
2       A03        Em Andamento     Teste de Componentes
3       A04        Aguardando       Reparo Hidráulico
4       A05        Pendente         Verificação Elétrica
5       A06        Iniciado         Calibração de Sensores
```

| Número da OS | Status (Novo) | Tipo | Descrição |
|---|---|---|---|
| A01 | Concluído | ✅ Atualizada | De "Aguardando" → "Concluído" |
| A02 | Concluído | ✅ Atualizada | De "Parado" → "Concluído" |
| A03 | Em Andamento | ✅ Atualizada | De "Iniciado" → "Em Andamento" |
| A04 | Aguardando | ⏸️ Pendente | Mantida (não encontrada) |
| A05 | Pendente | ✅ Atualizada | De "Parado" → "Pendente" |
| A06 | Iniciado | ⏸️ Pendente | Mantida (não encontrada) |

---

### 3.2 Variáveis de Saída

**Após executar `atualizar_status(df_consolidado, df_octave)`:**

```python
df_consolidado_atualizado = df_consolidado  # Modificado
lista_pendentes = ["A04", "A06"]
contador_atualizadas = 4
```

---

## 4. Cálculo de Validação

### 4.1 Três Variáveis de Relatório

#### Variável 1: `total_linhas_processadas`
```python
total_linhas_processadas = len(df_consolidado)
total_linhas_processadas = 6
```

**Descrição:** Total de linhas lidas em CONSOLIDADO (todas as 6)

---

#### Variável 2: `total_atualizadas`
```python
total_atualizadas = contador_atualizadas
total_atualizadas = 4
```

**Descrição:** Total de Status que foram alterados  
**Quais:** A01, A02, A03, A05

---

#### Variável 3: `total_pendentes`
```python
total_pendentes = len(lista_pendentes)
total_pendentes = 2
```

**Descrição:** Total de OS não encontradas (Status mantido)  
**Quais:** A04, A06

---

### 4.2 Validação da Integridade

**Verificação:**
```python
assert total_atualizadas + total_pendentes == total_linhas_processadas
```

**Cálculo:**
```
total_atualizadas + total_pendentes = ?

4 + 2 = 6  ✓

6 == 6  ✓✓✓ VÁLIDO
```

**Resultado:** ✅ **INTEGRIDADE CONFIRMADA**

---

### 4.3 Tabela de Validação

| Métrica | Valor | Validação |
|---------|-------|-----------|
| Total de Linhas Processadas | 6 | ✓ Correto |
| Total de OS Atualizadas | 4 | ✓ Correto |
| Total de OS Pendentes | 2 | ✓ Correto |
| Total Atualizadas + Pendentes | 4 + 2 = 6 | ✓ Igual ao Total |
| **Status Geral** | **SUCESSO** | **✓✓✓** |

---

## 5. Resumo da Simulação

### 5.1 Comportamento Observado

| Situação | Resultado | Quantidade |
|----------|-----------|-----------|
| OS encontrada em Octave → Status atualizado | ✅ Atualizada | 4 |
| OS NÃO encontrada em Octave → Status mantido | ⏸️ Pendente | 2 |
| Total processado | | 6 |

---

### 5.2 OS Atualizadas

```
✅ A01: Aguardando → Concluído
✅ A02: Parado → Concluído
✅ A03: Iniciado → Em Andamento
✅ A05: Parado → Pendente
```

**Total:** 4 atualizações

---

### 5.3 OS Pendentes (Não Encontradas)

```
⏸️ A04: Aguardando (mantido - não está no Octave)
⏸️ A06: Iniciado (mantido - não está no Octave)
```

**Total:** 2 pendentes

---

## 6. Relatório de Execução (Saída Terminal)

```
═════════════════════════════════════════════════════════
  RELATÓRIO DE EXECUÇÃO - ATUALIZADOR OCTAVE
═════════════════════════════════════════════════════════
Timestamp: 13/08/2026 14:30:48

Total de Linhas Processadas: 6
Total de OS Atualizadas:     4
Total de OS Pendentes:       2

OS Não Encontradas:
  • A04 (Reparo Hidráulico)
  • A06 (Calibração de Sensores)

═════════════════════════════════════════════════════════
Status: ✓ SUCESSO - Arquivo salvo
═════════════════════════════════════════════════════════
Pressione ENTER para sair...
═════════════════════════════════════════════════════════
```

---

## 7. Validação do Algoritmo O(1)

### 7.1 Análise de Complexidade

**Fase 1: Criar Mapa**
```python
mapa_status = {}
for i in range(len(df_octave)):  # M linhas
    numero_os = df_octave.loc[i, 'Número da OS']
    status = df_octave.loc[i, 'Status']
    mapa_status[numero_os] = status  # O(1) por inserção

Complexidade: O(M) onde M = 4
Neste caso: O(4) = 4 operações
```

**Fase 2: Atualizar Consolidado**
```python
lista_pendentes = []
contador = 0

for i in range(len(df_consolidado)):  # N linhas
    numero_os = df_consolidado.loc[i, 'Número da OS']
    
    if numero_os in mapa_status:  # O(1) busca em dict
        status_novo = mapa_status[numero_os]  # O(1) acesso
        df_consolidado.loc[i, 'Status'] = status_novo
        contador += 1
    else:
        lista_pendentes.append(numero_os)

Complexidade: O(N) onde N = 6
Neste caso: O(6) = 6 operações
```

**Total:**
```
O(M + N) = O(4 + 6) = O(10)
Linear, extremamente eficiente para até 50.000 linhas
```

---

### 7.2 Comparação: Loop vs Dict

**❌ Método Lento (Sem Dict):**
```python
# Para cada linha em Consolidado
for i in range(len(df_consolidado)):  # N = 6
    numero_os = df_consolidado.loc[i, 'Número da OS']
    
    # Buscar em Octave (loop secundário)
    for j in range(len(df_octave)):  # M = 4
        if df_octave.loc[j, 'Número da OS'] == numero_os:
            # Atualizar...

Complexidade: O(N × M) = O(6 × 4) = O(24)
```

**✅ Método Rápido (Com Dict - Usado):**
```python
# Criar dict uma vez
mapa_status = dict(...)  # O(M) = 4

# Para cada linha em Consolidado
for i in range(len(df_consolidado)):  # N = 6
    numero_os = df_consolidado.loc[i, 'Número da OS']
    
    # Busca instantânea
    if numero_os in mapa_status:  # O(1)
        # Atualizar...

Complexidade: O(M + N) = O(4 + 6) = O(10)
Economia: 24 vs 10 = 2.4x mais rápido
```

---

## 8. Conclusões da Simulação

### ✅ Validações Confirmadas

1. **Algoritmo Correto**
   - [x] OS encontrada → Status atualizado
   - [x] OS não encontrada → Status mantido
   - [x] Nenhuma linha deletada ou reordenada
   - [x] Colunas adicionais preservadas

2. **Integridade de Dados**
   - [x] Total de linhas preservado: 6
   - [x] Equação válida: 4 + 2 = 6
   - [x] Nenhuma perda de informação

3. **Eficiência**
   - [x] Usa Dict para O(1) lookup
   - [x] Complexidade total O(N + M)
   - [x] Escalável para 50.000+ linhas

4. **Lógica de Negócio**
   - [x] Regra 1 (Chave Principal): OK
   - [x] Regra 2 (Origem e Destino): OK
   - [x] Regra 3 (Atualização): OK
   - [x] Regra 4 (Não Encontrado): OK
   - [x] Regra 5 (Integridade): OK

---

## 9. Pronto para Implementação

Esta simulação de mesa valida que a especificação técnica da função `atualizar_status()` está:

- ✅ Logicamente correta
- ✅ Algoritmicamente eficiente
- ✅ Conforme com regras de negócio
- ✅ Pronta para codificação em Python

**Status:** 🟢 **VALIDADO PARA DESENVOLVIMENTO**
