# PRD - Automação de Atualização de Preventivas (Octave)

**Versão:** 2.0  
**Data:** 13/08/2026  
**Autor:** [Seu Nome]  
**Status:** Aprovado para Desenvolvimento  

---

## 1. Objetivo

Automatizar o processo de atualização do status das atividades preventivas, substituindo o procedimento manual. O sistema consistirá em um script em Python empacotado como um executável (`.exe`) que integrará os dados do **Octave** com a **planilha de controle interna**, garantindo precisão e rastreabilidade com **um único clique do usuário**.

---

## 2. Escopo

**Dentro do Escopo:**
- Um único diretório chamado `00. ATUALIZAR` conterá todos os arquivos necessários.
- Leitura da planilha mestre `DADOS_OCTAVE.xlsx` (fonte dos dados do Octave).
- Leitura e Sobrescrita da planilha de controle `CONSOLIDADO.xlsx`.
- Mapeamento dos dados utilizando a coluna **Número da OS** como chave.
- Atualização da coluna **Status** na planilha de Controle com os dados do Octave.
- Empacotamento do script em um único arquivo `.exe` para execução simplificada.
- Relatório de execução exibido diretamente no terminal (janela preta) durante a execução.

**Fora do Escopo:**
- Alteração de outras colunas que não sejam o "Status".
- Conexão direta com o banco de dados do Octave (API).
- Interface gráfica (GUI) complexa para o usuário.
- Alteração de arquivos que estejam fora da pasta `00. ATUALIZAR`.

---

## 3. Regras de Negócio

| # | Regra | Descrição |
|---|-------|-----------|
| 1 | **Chave Principal** | A coluna **Número da OS** é o identificador único e **obrigatório** em ambas as planilhas. |
| 2 | **Origem e Destino** | O script lê os dados atualizados de `DADOS_OCTAVE.xlsx` e aplica as alterações diretamente no `CONSOLIDADO.xlsx`. |
| 3 | **Atualização** | Para cada OS encontrada na planilha DADOS_OCTAVE, o campo "Status" na planilha CONSOLIDADO é sobrescrito pelo valor da fonte. |
| 4 | **Não Encontrado** | Se uma OS existir no `CONSOLIDADO` mas **não** estiver presente no `DADOS_OCTAVE`, o status atual dessa linha é mantido e a OS é reportada no relatório final como "Pendente". |
| 5 | **Integridade** | As linhas da planilha `CONSOLIDADO` não são excluídas ou reordenadas. Apenas o valor da célula de status é alterado. |

---

## 4. Fluxo de Execução (Experiência do Usuário)

1. O usuário abre a pasta `00. ATUALIZAR` no Windows Explorer.
2. O usuário dá um duplo clique no arquivo **`atualizador.exe`**.
3. Uma janela de terminal (CMD/PowerShell) se abre.
4. O script executa automaticamente o seguinte fluxo interno:
    - **Carregar** a planilha `CONSOLIDADO.xlsx`.
    - **Carregar** a planilha `DADOS_OCTAVE.xlsx`.
    - **Identificar** os índices (nomes) das colunas de "Número da OS" e "Status" em cada planilha.
    - **Criar um dicionário** no Octave: `{Número_da_OS: Status_Novo}`.
    - **Percorrer** a planilha `CONSOLIDADO` linha por linha.
    - Para cada linha: Extrair o "Número da OS". Buscar a OS no dicionário.
        - Se encontrada: Atualizar a célula de "Status" na planilha `CONSOLIDADO`.
        - Se não encontrada: Registrar em uma lista de "pendentes".
    - **Salvar** a planilha `CONSOLIDADO.xlsx` (sobrescrevendo a original).
5. O terminal exibe um relatório resumido e pausa para o usuário ler os resultados.
6. O usuário fecha a janela do terminal.

---

## 5. Entregáveis

- **Aplicativo:** `atualizador.exe` (Gerado via PyInstaller, dentro da pasta `00. ATUALIZAR`).
- **Arquivos de Dados:**
    - `00. ATUALIZAR/DADOS_OCTAVE.xlsx` (Entrada - planilha mais recente extraída do sistema Octave).
    - `00. ATUALIZAR/CONSOLIDADO.xlsx` (Entrada/Saída - planilha mestra que será sobrescrita).
- **Relatório no Terminal:** Contendo:
    - Total de linhas processadas no CONSOLIDADO.
    - Total de OS atualizadas com sucesso.
    - Total de OS não encontradas no OCTAVE (pendentes de atualização manual).

---

## 6. Tecnologias e Dependências (Ambiente de Desenvolvimento)

- **Linguagem:** Python 3.9+
- **Bibliotecas Python:**
    - `pandas` (para manipulação eficiente de dados e Excel)
    - `openpyxl` (motor de leitura/escrita de `.xlsx` pelo Pandas)
    - `os` (Gerenciamento de caminhos de arquivo)
- **Empacotamento:** `pyinstaller` (Para gerar o arquivo `.exe` único).

*(Nota: O usuário final não precisa ter Python instalado, apenas o `atualizador.exe` pronto para uso).*

---

## 7. Critérios de Aceite

- [ ] O script roda sem erros ao ser executado como `.exe` (sem necessidade de abrir o VS Code).
- [ ] O status das OS que estão no `DADOS_OCTAVE` é **atualizado corretamente** na planilha `CONSOLIDADO.xlsx`.
- [ ] O status das OS que **não estão** no `DADOS_OCTAVE` permanece inalterado (mantendo o valor antigo).
- [ ] A planilha `CONSOLIDADO.xlsx` é sobrescrita corretamente (os dados antigos dão lugar aos novos dados atualizados).
- [ ] Um relatório com contagens é impresso na janela do terminal ao final da execução.