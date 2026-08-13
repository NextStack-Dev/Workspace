# SPEC - Automação de Atualização de Preventivas (Octave)

**Versão Técnica:** 2.0  
**Data:** 13/08/2026  
**Status:** Especificação para Implementação  
**Tipo:** Engenharia de Software  
**Origem:** PRD v2.0

---

## Visão Geral

Especificação técnica detalhada para desenvolvimento de `atualizador.py`, um script Python que automatiza a sincronização de status de atividades preventivas entre dois arquivos Excel: `DADOS_OCTAVE.xlsx` (origem) e `CONSOLIDADO.xlsx` (destino). O script será executado diretamente em Python durante desenvolvimento e empacotado como `.exe` via PyInstaller para distribuição final.

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

## 4. Requisitos Funcionais

### RF-1: Carregamento de Dados
**Descrição:** O sistema deve carregar duas planilhas Excel corretamente.
- **RF-1.1:** Ler arquivo `CONSOLIDADO.xlsx` do diretório de execução
- **RF-1.2:** Ler arquivo `DADOS_OCTAVE.xlsx` do diretório de execução
- **RF-1.3:** Detectar automaticamente as colunas "Número da OS" e "Status" em ambas as planilhas
- **RF-1.4:** Suportar planilhas com cabeçalho na primeira linha

### RF-2: Mapeamento de Dados
**Descrição:** O sistema deve criar uma estrutura de dados para rápida busca.
- **RF-2.1:** Construir dicionário: `{Número_da_OS: Status_Novo}` a partir de `DADOS_OCTAVE.xlsx`
- **RF-2.2:** Permitir busca O(1) por Número da OS
- **RF-2.3:** Manter valores vazios ou nulos conforme presentes na fonte

### RF-3: Atualização de Status
**Descrição:** O sistema deve atualizar status de forma precisa e segura.
- **RF-3.1:** Para cada linha em `CONSOLIDADO.xlsx`, buscar Número da OS no dicionário
- **RF-3.2:** Se encontrada: sobrescrever o valor de "Status" com o valor do Octave
- **RF-3.3:** Se não encontrada: manter valor de "Status" original e registrar como pendente
- **RF-3.4:** Preservar formatação de células (cores, fontes) durante atualização

### RF-4: Persistência de Dados
**Descrição:** O sistema deve salvar as alterações de forma segura.
- **RF-4.1:** Sobrescrever o arquivo `CONSOLIDADO.xlsx` original com dados atualizados
- **RF-4.2:** Validar integridade antes de salvar
- **RF-4.3:** Manter estrutura de linhas e colunas idêntica ao original
- **RF-4.4:** Criar backup automático antes de sobrescrever (opcional, em pasta de backup)

### RF-5: Relatório de Execução
**Descrição:** O sistema deve exibir relatório resumido no terminal.
- **RF-5.1:** Total de linhas processadas em `CONSOLIDADO.xlsx`
- **RF-5.2:** Total de OS atualizadas com sucesso
- **RF-5.3:** Total de OS não encontradas (pendentes)
- **RF-5.4:** Lista de OS pendentes (Números da OS)
- **RF-5.5:** Timestamp de execução
- **RF-5.6:** Status final (Sucesso / Erro)

### RF-6: Tratamento de Erros
**Descrição:** O sistema deve gerenciar condições de erro graciosamente.
- **RF-6.1:** Detectar arquivo não encontrado e informar ao usuário
- **RF-6.2:** Detectar colunas obrigatórias faltantes ("Número da OS", "Status")
- **RF-6.3:** Tratamento de planilhas vazias ou malformadas
- **RF-6.4:** Pausar terminal para leitura de mensagens de erro antes de fechar

---

## 5. Requisitos Não-Funcionais

### RNF-1: Performance
- Processar planilhas com até 5.000+ linhas em menos de 5 segundos
- Uso eficiente de memória (máx. 100MB RAM)

### RNF-2: Portabilidade
- Executável único (`.exe`) funciona sem dependência de Python instalado
- Compatível com Windows 7+
- Não requer privilégios administrativos

### RNF-3: Confiabilidade
- Nenhuma perda de dados durante atualização
- Operação atômica (tudo ou nada)
- Logs de operação para auditoria

### RNF-4: Usabilidade
- Execução com duplo clique
- Interface simples via terminal
- Relatório claro e legível
- Pausa terminal antes de fechar para leitura

### RNF-5: Manutenibilidade
- Código bem estruturado e comentado
- Fácil localização de bugs
- Logs detalhados para debugging

---

## 6. Arquitetura de Solução

### Componentes Principais

```
┌─────────────────────────────────────────────────┐
│         atualizador.exe (PyInstaller)          │
├─────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────┐  │
│  │         Módulo Principal (main.py)       │  │
│  │   - Orquestração do fluxo de execução    │  │
│  │   - Tratamento de exceções globais       │  │
│  └──────────────────────────────────────────┘  │
│         ↓              ↓              ↓         │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ │
│  │   Data     │ │  Mapping   │ │   Report   │ │
│  │  Manager   │ │  Engine    │ │  Generator │ │
│  │ (pandas)   │ │ (dict)     │ │ (terminal) │ │
│  └────────────┘ └────────────┘ └────────────┘ │
│         ↓                             ↑        │
│  ┌──────────────────────────────────────────┐  │
│  │    Camada de Acesso a Arquivos (I/O)    │  │
│  │  - Leitura XLSX (openpyxl/pandas)       │  │
│  │  - Escrita XLSX (openpyxl/pandas)       │  │
│  │  - Validação de integridade             │  │
│  └──────────────────────────────────────────┘  │
│             ↓                     ↑            │
└─────────────────────────────────────────────────┘
              ↓                     ↑
      ┌──────────────────────────────────────┐
      │   Arquivos Excel (00. ATUALIZAR/)    │
      │  - CONSOLIDADO.xlsx (entrada/saída)  │
      │  - DADOS_OCTAVE.xlsx (entrada)       │
      └──────────────────────────────────────┘
```

### Fluxo de Dados

```
DADOS_OCTAVE.xlsx
       ↓
  [Leitura DataFrame]
       ↓
  [Extrair Números OS]
       ↓
  [Criar Dicionário: OS → Status]
       ↓
CONSOLIDADO.xlsx → [Leitura DataFrame]
       ↓              ↓
  [Merge/Update] ←───┘
       ↓
  [Validação]
       ↓
  [Escrita XLSX]
       ↓
  [Gerar Relatório]
       ↓
  [Exibir Terminal]
       ↓
CONSOLIDADO.xlsx (atualizado)
```

---

## 7. Design Técnico

### 7.1 Estrutura de Modules

```
atualizador.exe
├── main.py                 # Ponto de entrada, orquestração
├── data_manager.py         # Leitura/escrita de arquivos
├── mapping_engine.py       # Lógica de mapeamento e atualização
├── report_generator.py     # Geração de relatório
└── utils.py                # Funções auxiliares (logs, validações)
```

### 7.2 Algoritmo Principal

```python
1. INICIALIZAR
   - Definir caminho de execução
   - Validar existência de arquivos

2. CARREGAR_DADOS
   - df_consolidado = pandas.read_excel('CONSOLIDADO.xlsx')
   - df_octave = pandas.read_excel('DADOS_OCTAVE.xlsx')

3. VALIDAR_ESTRUTURA
   - Verificar colunas obrigatórias em ambos os DataFrames
   - Normalizar nomes de colunas (strip, case)

4. CRIAR_MAPEAMENTO
   - mapa_os_status = dict(
       zip(df_octave['Número da OS'], 
           df_octave['Status'])
     )

5. ATUALIZAR_CONSOLIDADO
   - os_nao_encontradas = []
   - Para cada linha em df_consolidado:
     - numero_os = linha['Número da OS']
     - Se numero_os em mapa_os_status:
       - linha['Status'] = mapa_os_status[numero_os]
       - contar_atualizada += 1
     - Senão:
       - os_nao_encontradas.append(numero_os)

6. VALIDAR_RESULTADO
   - Verificar integridade de dados
   - Confirmar número de linhas

7. SALVAR_CONSOLIDADO
   - df_consolidado.to_excel('CONSOLIDADO.xlsx', index=False)

8. GERAR_RELATORIO
   - total_processadas = len(df_consolidado)
   - total_atualizadas = contar_atualizada
   - total_pendentes = len(os_nao_encontradas)
   - Exibir relatório no terminal

9. FINALIZAR
   - Pausar terminal para leitura
   - Fechar graciosamente
```

### 7.3 Mapeamento de Colunas

O sistema deve ser flexível para detectar automaticamente o nome das colunas:

```python
COLUNAS_PROCURADAS = {
    'numero_os': [
        'Número da OS', 
        'numero da os', 
        'os', 
        'nº da os',
        'numero os'
    ],
    'status': [
        'Status', 
        'status', 
        'estado',
        'situação'
    ]
}
```

**Estratégia:** Busca case-insensitive com normalização de strings (remover acentos, espaços extras).

### 7.4 Tipos de Dados e Validação

| Campo | Tipo | Validação |
|-------|------|-----------|
| Número da OS | String | Não vazio, único |
| Status | String | Pode ser vazio, mantém valor original se não encontrado |
| Linhas CONSOLIDADO | Tabular | Mínimo 1, máximo 50.000 |
| Linhas OCTAVE | Tabular | Mínimo 1 |

---

## 8. Fluxo de Dados Detalhado

### Entrada
- **Arquivo 1:** `CONSOLIDADO.xlsx`
  - Coluna obrigatória: "Número da OS"
  - Coluna a atualizar: "Status"
  - Outras colunas: preservadas intactas

- **Arquivo 2:** `DADOS_OCTAVE.xlsx`
  - Coluna obrigatória: "Número da OS"
  - Coluna de origem: "Status"
  - Pode conter colunas adicionais (ignoradas)

### Processamento

1. **Leitura:** Ambas as planilhas carregadas via Pandas
2. **Mapeamento:** Dicionário Python criado em memória
3. **Iteração:** Loop por cada linha de CONSOLIDADO
4. **Busca:** O(1) lookup no dicionário
5. **Atualização:** Célula de status modificada se encontrada
6. **Registro:** OS não encontradas armazenadas em lista

### Saída
- **Arquivo Atualizado:** `CONSOLIDADO.xlsx` (sobrescrito)
- **Relatório Terminal:**
  ```
  ╔═══════════════════════════════════════╗
  ║   RELATÓRIO DE EXECUÇÃO               ║
  ║   Atualizador Octave v2.0             ║
  ╠═══════════════════════════════════════╣
  ║ Data/Hora: 13/08/2026 14:30:45       ║
  ║ Total de Linhas Processadas: 1250    ║
  ║ Status Atualizados com Sucesso: 1200 ║
  ║ OS Não Encontradas (Pendentes): 50   ║
  ╠═══════════════════════════════════════╣
  ║ OS Pendentes:                         ║
  ║ - OS-001234                           ║
  ║ - OS-001235                           ║
  ║ [... mais 48 ...]                     ║
  ╠═══════════════════════════════════════╣
  ║ Status: ✓ SUCESSO                    ║
  ║ Pressione qualquer tecla para sair... ║
  ╚═══════════════════════════════════════╝
  ```

---

## 9. Tratamento de Erros

### Cenários de Erro Esperados

| Código | Erro | Ação |
|--------|------|------|
| E-001 | Arquivo não encontrado | Informar qual arquivo, caminho esperado, pausar terminal |
| E-002 | Coluna obrigatória faltante | Informar nome da coluna esperada, arquivo afetado |
| E-003 | Planilha vazia | Informar qual planilha, interromper execução |
| E-004 | Erro de permissão | Informar que arquivo está aberto/protegido, tentar fechar |
| E-005 | Formato inválido | Informar que arquivo não é Excel válido |
| E-006 | Erro de escrita | Informar impossibilidade de salvar, sugerir verificar espaço em disco |
| E-007 | Erro desconhecido | Log detalhado de exceção, sugerir contato com suporte |

### Tratamento de Exceções

```python
try:
    # Executar fluxo principal
    executar_atualizacao()
except FileNotFoundError as e:
    exibir_erro(f"Arquivo não encontrado: {e.filename}")
except PermissionError:
    exibir_erro("Arquivo aberto ou protegido. Feche o arquivo e tente novamente.")
except ValueError as e:
    exibir_erro(f"Erro de dados: {str(e)}")
except Exception as e:
    exibir_erro(f"Erro inesperado: {str(e)}\nEntre em contato com o suporte.")
finally:
    pausar_terminal()
```

---

## 10. Interface de Usuário

### Apresentação do Terminal

#### Inicialização
```
═══════════════════════════════════════════════════════
  ATUALIZADOR OCTAVE v2.0
  Automação de Atualização de Preventivas
═══════════════════════════════════════════════════════
[14:30:45] Iniciando...
[14:30:45] Validando arquivos...
[14:30:45] ✓ CONSOLIDADO.xlsx encontrado
[14:30:45] ✓ DADOS_OCTAVE.xlsx encontrado
[14:30:45] Carregando dados...
```

#### Processamento
```
[14:30:46] Lendo CONSOLIDADO.xlsx (1250 linhas)...
[14:30:46] ✓ Carregado com sucesso
[14:30:46] Lendo DADOS_OCTAVE.xlsx (1200 linhas)...
[14:30:46] ✓ Carregado com sucesso
[14:30:46] Mapeando dados (criando índice)...
[14:30:47] ✓ Índice criado: 1200 registros
[14:30:47] Atualizando status...
[14:30:47] [████████████████████░░░░░░░░░░░░] 50%
[14:30:48] ✓ Atualização concluída
[14:30:48] Salvando CONSOLIDADO.xlsx...
[14:30:48] ✓ Arquivo salvo com sucesso
```

#### Conclusão
```
═══════════════════════════════════════════════════════
  RELATÓRIO FINAL
═══════════════════════════════════════════════════════
Data/Hora:                    13/08/2026 14:30:48
Total de Linhas Processadas:  1250
Status Atualizados:           1200
OS Não Encontradas:           50

OS Pendentes (Primeiras 10):
  • OS-001001
  • OS-001002
  • OS-001003
  • OS-001004
  • OS-001005
  • OS-001006
  • OS-001007
  • OS-001008
  • OS-001009
  • OS-001010
  [... 40 mais ...]

Status: ✓ SUCESSO
═══════════════════════════════════════════════════════
Pressione qualquer tecla para sair...
```

---

## 11. Entregáveis

### Aplicação

| Item | Descrição | Localização |
|------|-----------|-------------|
| Executável | `atualizador.exe` | `00. ATUALIZAR/atualizador.exe` |
| Código Fonte | Repositório Git | GitHub/repositorio/src/ |
| Documentação | README técnico | `README.md` |

### Dados

| Item | Descrição | Localização | Nota |
|------|-----------|-------------|------|
| Consolidado | Planilha mestre | `00. ATUALIZAR/CONSOLIDADO.xlsx` | Será sobrescrita |
| Octave | Dados de origem | `00. ATUALIZAR/DADOS_OCTAVE.xlsx` | Não será modificada |
| Backup (opcional) | Backup automático | `00. ATUALIZAR/backup/CONSOLIDADO_YYYYMMDD_HHMMSS.xlsx` | Mantém histórico |

---

## 12. Considerações de Teste

### Testes Unitários (TDD)

1. **Leitura de Arquivos**
   - [ ] Arquivo Excel válido é lido corretamente
   - [ ] Arquivo não encontrado gera exceção tratada
   - [ ] Planilha vazia é detectada
   - [ ] Múltiplas abas: testa primeira aba por padrão

2. **Mapeamento de Dados**
   - [ ] Dicionário criado com tamanho correto
   - [ ] Busca rápida por Número da OS
   - [ ] Valores nulos são tratados

3. **Atualização de Status**
   - [ ] Status é atualizado quando OS encontrada
   - [ ] Status mantido quando OS não encontrada
   - [ ] Linhas estrutura preservada
   - [ ] Formatação original mantida (colorir de forma opcional)

4. **Persistência**
   - [ ] Arquivo salvo sem corrupção
   - [ ] Dados persistem após fechamento
   - [ ] Estrutura de linhas/colunas idêntica

5. **Tratamento de Erros**
   - [ ] Arquivo não encontrado tratado
   - [ ] Colunas faltantes detectadas
   - [ ] Planilha malformada identificada
   - [ ] Mensagens de erro claras

6. **Relatório**
   - [ ] Contagem correta de processadas
   - [ ] Contagem correta de atualizadas
   - [ ] Contagem correta de pendentes
   - [ ] Lista de pendentes completa e correta

### Testes de Integração

- [ ] Fluxo completo: carregar → mapear → atualizar → salvar → reportar
- [ ] Com arquivos reais do Octave
- [ ] Com cenários de dados faltantes

### Testes de Aceitação (UAT)

- [ ] Duplo clique no `.exe` inicia execução
- [ ] Relatório exibido é compreensível ao usuário final
- [ ] Dados em `CONSOLIDADO.xlsx` são atualizados conforme esperado
- [ ] Terminal pausa para leitura antes de fechar

---

## 13. Cronograma e Marcos

| Marco | Descrição | Duração |
|-------|-----------|---------|
| M-1 | Setup de projeto e dependências | 1 dia |
| M-2 | Desenvolvimento do módulo de I/O | 2 dias |
| M-3 | Desenvolvimento do motor de mapping | 2 dias |
| M-4 | Desenvolvimento de relatório e UI terminal | 1 dia |
| M-5 | Testes unitários e integração | 2 dias |
| M-6 | Empacotamento como `.exe` (PyInstaller) | 1 dia |
| M-7 | Testes de aceitação e ajustes | 1 dia |
| M-8 | Documentação final e entrega | 1 dia |

**Total Estimado:** 11 dias

---

## 14. Riscos e Mitigação

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Formato de planilha diferente que esperado | Alto | Média | Testes com arquivos reais; validação de coluna flexível |
| Perda de dados durante atualização | Crítico | Baixa | Backup automático; testes rigorosos |
| Compatibilidade Windows 7 | Médio | Baixa | Testes em múltiplas versões Windows |
| Performance com 50K+ linhas | Médio | Baixa | Otimização de algoritmo; testes de carga |
| Usuário executa de pasta errada | Médio | Alta | Validação de caminho; mensagem de erro clara |

---

## 15. Critérios de Aceite Técnico

- [ ] **CA-1:** Código passa em 100% dos testes unitários
- [ ] **CA-2:** Integração de ponta a ponta funciona sem erros
- [ ] **CA-3:** Executável funciona sem Python instalado no cliente
- [ ] **CA-4:** Relatório terminal é legível e contém todas as métricas
- [ ] **CA-5:** Arquivo `CONSOLIDADO.xlsx` é atualizado corretamente
- [ ] **CA-6:** Sem perda de dados ou integridade comprometida
- [ ] **CA-7:** Tempo de execução < 5 segundos para 5.000 linhas
- [ ] **CA-8:** Documentação técnica completa e precisa

---

## 16. Próximos Passos

1. Validar SPEC com stakeholders
2. Iniciar desenvolvimento (M-1)
3. Criar repositório Git com estrutura de branches
4. Configurar ambiente de desenvolvimento
5. Implementar pipeline de testes (CI/CD)
