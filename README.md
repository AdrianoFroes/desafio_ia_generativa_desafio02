# Desafio Prático 1 — IA Generativa

Este repositório contém o desenvolvimento do primeiro desafio prático do Módulo 01 — IA Generativa, do curso FIC Dev IA.

## Sobre o desafio

A proposta é desenvolver uma Central Inteligente de Atendimento e Comunicação Institucional, simulando o atendimento de uma secretaria pública.

O sistema deverá utilizar ferramentas de inteligência artificial para receber solicitações de cidadãos em diferentes formatos, como texto, áudio e PDF, extrair informações e gerar sugestões de respostas.

As respostas deverão passar por revisão humana antes de serem aprovadas.

## Tecnologias

- Python
- APIs e modelos de inteligência artificial
- Bibliotecas para processamento de texto, áudio e imagens

As ferramentas e bibliotecas serão definidas conforme o desenvolvimento do projeto.

## Organização do projeto

- `dados/` — arquivos de entrada, gabaritos e dados processados.
- `src/` — códigos Python do sistema.
- `prompts/` — prompts utilizados nos testes.
- `resultados/` — respostas, áudios, imagens e logs gerados.
- `testes/` — testes do projeto.
- `documentacao/` — enunciado e documentação do desafio.

## Como instalar e executar

Para executar o projeto, é necessário ter o Python 3.12 instalado.

**1. Criar o ambiente virtual**

No PowerShell, dentro da pasta do projeto:

```powershell
py -3.12 -m venv .venv
```

**2. Ativar o ambiente virtual**

```powershell
.\.venv\Scripts\Activate.ps1
```

**3. Instalar as bibliotecas**

```powershell
python -m pip install -r requirements.txt
```

**4. Configurar o projeto**

O arquivo `config.json` contém as configurações iniciais do sistema, como o modelo de IA e os caminhos das pastas.

O arquivo `.env.example` mostra as variáveis utilizadas para as chaves das APIs. Quando necessário, deve ser criada uma cópia chamada `.env`, preenchida com as credenciais correspondentes.

As chaves não devem ser colocadas diretamente no código nem enviadas ao GitHub.

**5. Executar o programa**

```powershell
python -m src.main
```

O programa mostra as configurações carregadas, verifica as pastas e apresenta as versões do Python e das bibliotecas.

A inicialização pode ser testada sem uma chave de API.

## Andamento

A estrutura inicial do projeto foi criada.

O RF01 está em desenvolvimento. A leitura das configurações, a verificação das pastas e a identificação das versões já foram implementadas e testadas.

As demais funcionalidades serão desenvolvidas ao longo do desafio.

## Curso

FIC Dev IA — Módulo 01: IA Generativa.