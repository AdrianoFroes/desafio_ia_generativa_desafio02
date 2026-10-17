# Desafio Prático 1 — IA Generativa

Projeto desenvolvido no **Módulo 01 — IA Generativa**, do curso FIC Dev IA.

## 1. Sobre o projeto

Este repositório contém uma **Central Inteligente de Atendimento e Comunicação Institucional**, desenvolvida para simular atividades de uma secretaria pública.

O projeto utiliza técnicas de inteligência artificial generativa para apoiar o tratamento de solicitações de cidadãos, incluindo processamento de textos, áudios, documentos e imagens, além da elaboração de materiais institucionais.

Os **13 requisitos funcionais (RF01 a RF13)** foram implementados, com testes automatizados, registros de execução e documentação.

**Atenção:** os conteúdos gerados por inteligência artificial são sugestões e precisam passar por revisão humana antes de qualquer utilização institucional. O sistema não realiza envio automático de respostas aos cidadãos.

## 2. Tecnologias e pré-requisitos

- Python 3.12
- Git
- Acesso à internet para instalação das dependências
- Bibliotecas Python definidas em `requirements.txt`
- Credenciais de serviços externos de IA, apenas quando necessárias

Dependências principais:

```text
openai==3.33.0
python-dotenv==1.2.4
requests==2.34.2
pymupdf==1.28.2
pytest==9.1.1
```

O projeto utiliza integrações com serviços como Gemini, Groq e Hugging Face, conforme a funcionalidade executada.

A inicialização básica e os testes automatizados não exigem credenciais reais.

## 3. Organização do projeto

| Diretório ou arquivo | Descrição |
|---|---|
| `src/` | Código-fonte Python |
| `testes/` | Testes automatizados |
| `dados/` | Dados de entrada, exemplos e arquivos processados |
| `prompts/` | Prompts utilizados nos experimentos |
| `resultados/` | Resultados, minutas, imagens, áudios e logs |
| `documentacao/` | Documentação técnica e registros de revisão |
| `config.json` | Configurações gerais do sistema |
| `.env.example` | Exemplo das variáveis de ambiente |
| `requirements.txt` | Dependências Python |

Alguns arquivos de entrada e saída podem ser gerados durante a execução e não estar versionados no Git.

## 4. Instalação e execução

As instruções abaixo contemplam Windows, Linux e macOS.

Antes de começar, instale o **Git** e o **Python 3.12** no sistema operacional utilizado.

### 4.1. Windows — PowerShell

**Passo 1 — Clonar o repositório**

```powershell
git clone https://github.com/Yasmine-Lino/desafio_ia_generativa.git
cd desafio_ia_generativa
```

**Passo 2 — Criar o ambiente virtual**

```powershell
py -3.12 -m venv .venv
```

**Passo 3 — Ativar o ambiente virtual**

```powershell
.\.venv\Scripts\Activate.ps1
```

**Passo 4 — Instalar as dependências**

```powershell
python -m pip install -r requirements.txt
```

**Passo 5 — Executar a inicialização do projeto**

```powershell
python -m src.main
```

Caso o PowerShell bloqueie a ativação do ambiente virtual, é possível executar diretamente o Python desse ambiente:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.main
```

### 4.2. Linux — Terminal

**Passo 1 — Clonar o repositório**

```bash
git clone https://github.com/Yasmine-Lino/desafio_ia_generativa.git
cd desafio_ia_generativa
```

**Passo 2 — Criar o ambiente virtual**

```bash
python3.12 -m venv .venv
```

**Passo 3 — Ativar o ambiente virtual**

```bash
source .venv/bin/activate
```

**Passo 4 — Instalar as dependências**

```bash
python -m pip install -r requirements.txt
```

**Passo 5 — Executar a inicialização**

```bash
python -m src.main
```

**Observação:** dependendo da distribuição Linux, pode ser necessário instalar separadamente o suporte a ambientes virtuais (`venv`) para Python 3.12.

### 4.3. macOS — Terminal

**Passo 1 — Clonar o repositório**

```bash
git clone https://github.com/Yasmine-Lino/desafio_ia_generativa.git
cd desafio_ia_generativa
```

**Passo 2 — Criar o ambiente virtual**

```bash
python3.12 -m venv .venv
```

**Passo 3 — Ativar o ambiente virtual**

```bash
source .venv/bin/activate
```

**Passo 4 — Instalar as dependências**

```bash
python -m pip install -r requirements.txt
```

**Passo 5 — Executar a inicialização**

```bash
python -m src.main
```

**Observação:** o Python 3.12 precisa estar instalado e disponível no terminal. Dependendo da instalação do macOS, pode ser necessário instalar essa versão separadamente.

## 5. Configuração das APIs

O arquivo `.env.example` apresenta as variáveis de ambiente previstas:

```dotenv
GEMINI_API_KEY=
GROQ_API_KEY=
HF_TOKEN=
```

Para utilizar funcionalidades que dependem dessas APIs, crie uma cópia chamada `.env`.

**Windows — PowerShell**

```powershell
Copy-Item .env.example .env
```

**Linux e macOS**

```bash
cp .env.example .env
```

Abra o arquivo `.env` e preencha as credenciais correspondentes aos serviços que pretende utilizar.

**Cuidados de segurança:**

- Nunca publique chaves de API no GitHub.
- Não inclua credenciais diretamente no código-fonte.
- Não compartilhe o conteúdo do arquivo `.env`.
- Verifique as permissões, os limites de uso e as cotas disponíveis de cada provedor.

As configurações gerais do sistema estão no arquivo `config.json`.

## 6. Execução dos testes automatizados

Com o ambiente virtual ativado, execute:

```bash
python -m unittest discover -s testes -p "teste_*.py"
```

O comando é o mesmo para Windows, Linux e macOS.

Na última execução realizada durante o desenvolvimento, o projeto apresentou:

```text
Ran 123 tests

OK
```

Os testes incluem simulações de erros e situações excepcionais. Por isso, algumas mensagens de falha podem aparecer durante a execução sem indicar problemas no resultado final.

Os testes foram desenvolvidos para validar os comportamentos sem necessidade de realizar chamadas reais às APIs externas.

## 7. Requisitos funcionais e evidências

O projeto contempla os requisitos **RF01 a RF13**, com implementações em `src/`, testes em `testes/` e registros complementares em `documentacao/` e `resultados/`.

Entre as evidências disponíveis estão:

- **RF03 — Testes de segurança contra instruções maliciosas:** `documentacao/avaliacao_rf03.md` e `resultados/logs/rf03_injecao.json`.
- **RF09 — Elaboração e revisão de minuta institucional:** `documentacao/revisao_rf09.md` e arquivos em `resultados/minutas/`.
- **RF12 — Privacidade e minimização de dados:** `src/privacidade.py`, `testes/teste_rf12.py` e `documentacao/revisao_rf12.md`.
- **RF13 — Avaliação de qualidade e revisão humana:** `src/avaliacao_qualidade.py`, `src/executar_avaliacao_rf13.py`, `testes/teste_rf13.py`, `documentacao/revisao_rf13.md` e `resultados/logs/rf13_avaliacao.json`.

### Avaliação de qualidade — RF13

A avaliação considera cinco critérios:

1. Fidelidade
2. Completude
3. Formato
4. Linguagem
5. Segurança

Foram avaliados dois casos independentes, com os seguintes resultados:

| Caso | Pontuação | Resultado |
|---|---|---|
| RF03 — Injeção de prompt | 10/10 | Aprovado |
| RF09 — Minuta original | 8/10 | Correção manual necessária |

A **taxa de aprovação inicial foi de 50%**.

A minuta do RF09 foi corrigida e aprovada posteriormente por revisão humana. Essa correção não foi contabilizada como um novo caso.

## 8. Limitações e cuidados

Este projeto é um **protótipo educacional**, não um sistema de produção de uma secretaria pública.

As principais limitações e precauções são:

- Modelos de IA podem produzir informações incorretas, incompletas ou não confirmadas.
- Serviços externos podem apresentar indisponibilidade, limites de uso ou ausência de créditos.
- Os resultados devem ser verificados por uma pessoa responsável.
- Dados pessoais e informações sigilosas exigem tratamento adequado, observando as exigências aplicáveis da LGPD.
- A geração de materiais não representa autorização para publicação ou envio automático.
- A execução foi testada no ambiente de desenvolvimento Windows. As instruções para Linux e macOS foram incluídas para facilitar a portabilidade, mas ainda não foram validadas nesses sistemas.

## 9. Situação do desenvolvimento

Os requisitos **RF01 a RF13 foram implementados e publicados no repositório**.

A suíte automatizada apresentou **123 testes aprovados** na última execução.

As evidências, limitações e revisões estão registradas na documentação do projeto.

## 10. Curso

**FIC Dev IA — Módulo 01: IA Generativa.**


## Demonstração offline e identidade visual (complemento da entrega)

As minutas `.txt` permanecem inalteradas como evidências de geração e revisão.
As versões de **apresentação** em PDF incluem `dados/originais/brasao.png`,
identificação de documento fictício e aviso de que não são comunicações oficiais.
O brasão é usado apenas para demonstração acadêmica; não indica aprovação do GOV.MT.

```bash
python -m src.gerar_minuta_pdf --versao ambas
python -m src.demonstracao
python -m src.demonstracao --registrar
python -m pytest -q
```

A demonstração é **offline**: verifica a presença dos artefatos já produzidos,
não chama modelos, não recria respostas e não simula inferências. A opção
`--registrar` cria um log JSONL verdadeiro **da própria conferência offline**,
sem afirmar que as chamadas históricas à API foram reexecutadas.
O comando `python -m src.main` continua sendo o ponto de entrada de
inicialização/configuração, e não um pipeline automático de produção.

A síntese RF07 documentada utiliza uma minuta de teste aprovada para o ensaio;
não corresponde ao áudio da minuta definitiva RF09. Para uso institucional,
a versão aprovada precisaria passar por síntese e conferência específicas.

**Pacote de entrega:** `.env.example` deve ser incluído; `.env` verdadeiro,
`.venv`, caches e credenciais não devem ser incluídos. Os arquivos fictícios
originais e os gabaritos locais são evidências necessárias para a avaliação.


## Complemento de conformidade RF06, RF07, RF08 e RF11

- `dados/gabaritos/rf06_referencia_posterior.txt` é uma **referência retrospectiva**, copiada da transcrição revisada, e **não é um gabarito independente preparado antes da inferência**. O RF06 ainda exige validação por escuta independente se esse for o critério de aceite aplicado.
- A síntese original `rf07_minuta_falada.wav` é um ensaio. Para sintetizar a **minuta RF09 aprovada** sem sobrescrever o ensaio, conferir previamente o texto e executar:

```powershell
python -m src.sintese_voz resultados/minutas/rf09_minuta_revisada.txt --aprovado --final-rf09
```

O comando requer `GEMINI_API_KEY` configurada, acesso à API e pode consumir créditos. Produz `resultados/audios/rf07_minuta_rf09_aprovada.wav` e metadados separados. **Ouça o áudio inteiro** e confirme correspondência antes de declarar a revisão concluída; a execução deixa `revisao_audio_pendente=true`.

- `python -m src.verificar_pendencias` confere a presença das evidências, o hash da minuta associada ao áudio e a existência do log central, sem chamar APIs.
- O gabarito RF08 foi atualizado após o OCR: essa comparação não é avaliação cega independente.
- Logs antigos que não foram coletados **não podem ser reconstruídos como se fossem registros originais**. `resultados/logs/demonstracao_offline.jsonl` registra somente a demonstração offline. Se houver `resultados/logs/auditoria.jsonl` real no PC, preservar e avaliar inclusão na entrega após conferir dados sensíveis.
