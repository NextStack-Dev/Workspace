# PRD - Automação de Atualização de Preventivas (Octave)

**Versão:** 1.0
**Data:** 13/08/2026
**Autor:** [Seu Nome]
**Status:** Em Elaboração

---

## 1. Objetivo

Automatizar o processo de atualização do status das atividades preventivas, substituindo o procedimento manual (copiar/colar) por um script que integra os dados do **Octave** com a **planilha de controle interna**, garantindo precisão e rastreabilidade.

---

## 2. Escopo

**Dentro do Escopo:**
- Leitura de duas planilhas `.xlsx` (Controle e Octave).
- Mapeamento dos dados utilizando a coluna **Número da OS** como chave.
- Atualização da coluna **Status** na planilha de Controle com os dados do Octave.
- Geração de uma nova planilha (saída) sem alterar os arquivos originais.

**Fora do Escopo:**
- Alteração de outras colunas que não sejam o "Status".
- Conexão direta com o banco de dados do Octave (API).
- Interface gráfica para o usuário.

---

## 3. Regras de Negócio

| # | Regra | Descrição |
|---|-------|-----------|
| 1 | **Chave Principal** | A coluna **Número da OS** é o identificador único e **obrigatório** em ambas as planilhas. |
| 2 | **Atualização** | Para cada OS encontrada no Octave, o campo "Status" na planilha de Controle é sobrescrito pelo valor do Octave. |
| 3 | **Não Encontrado** | Se uma OS existir no Controle mas **não** no Octave, o status atual é mantido e a OS é reportada em um log de "Não Atualizados". |
| 4 | **Integridade** | As linhas da planilha de Controle não são excluídas ou reordenadas. Apenas o valor da célula de status é alterado. |

---

## 4. Fluxo de Execução

1. **Carregar** a planilha de Controle (`controle.xlsx`).
2. **Carregar** a planilha do Octave (`octave.xlsx`).
3. **Identificar** os índices (ou nomes) das colunas de "OS" e "Status" em cada planilha.
4. **Criar um índice** (dicionário) no Octave: `{OS: Status}`.
5. **Percorrer** a planilha de Controle linha por linha.
6. Para cada linha:
    - Extrair o "Número da OS".
    - Buscar a OS no dicionário do Octave.
    - Se encontrada: Atualizar a célula de "Status" na planilha de Controle.
    - Se não encontrada: Registrar em uma lista de "pendentes".
7. **Salvar** a planilha de Controle atualizada em um novo arquivo (`controle_atualizado.xlsx`).
8. **Exibir** um relatório resumido no terminal (quantas atualizadas, quantas pendentes).

---

## 5. Entregáveis

- **Script:** `src/atualizador.py`
- **Planilha de Saída:** `outputs/controle_atualizado.xlsx`
- **Relatório no Terminal:** Contendo:
    - Total de linhas processadas.
    - Total de OS atualizadas.
    - Total de OS não encontradas (pendentes).

---

## 6. Tecnologias e Dependências

- **Linguagem:** Python 3.9+
- **Bibliotecas:**
    - `openpyxl` (Leitura e escrita de `.xlsx`)
    - `os` (Gerenciamento de caminhos de arquivo)

---

## 7. Critérios de Aceite

- [ ] O script roda sem erros em um ambiente com Python configurado.
- [ ] O status das OS que estão no Octave é **atualizado corretamente** na planilha de saída.
- [ ] O status das OS que **não estão** no Octave permanece inalterado.
- [ ] Um relatório simples é impresso no terminal ao final da execução.
- [ ] As planilhas originais não são modificadas.