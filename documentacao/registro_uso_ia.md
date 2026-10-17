# Registro do uso de IA no desenvolvimento

## 1. Finalidade

Durante o desenvolvimento do Desafio Prático 1 — Central Inteligente de Atendimento e Comunicação Institucional, foram utilizadas ferramentas de inteligência artificial como apoio à organização das atividades, elaboração de sugestões técnicas, revisão de código e documentação.

As sugestões foram submetidas a verificações e ajustes durante o desenvolvimento, considerando os requisitos do enunciado e os resultados dos testes.

## 2. Ferramentas utilizadas

- **ChatGPT (OpenAI):** apoio à estruturação do projeto, esclarecimento de dúvidas sobre Python, sugestões de implementação e organização da documentação.
- **Gemini (Google):** modelo utilizado nos experimentos de geração de respostas institucionais e na integração por API.
- **Modelo Gemini 3.8 Flash:** identificado nos registros dos experimentos RF02 e RF04.

As versões específicas das ferramentas de assistência utilizadas durante a programação não foram registradas.

## 3. Exemplos de solicitações feitas à IA

**Solicitação 1 — Organização do projeto**

Apoio na definição da estrutura de diretórios, organização dos arquivos Python e preparação do ambiente de desenvolvimento, considerando os requisitos apresentados no enunciado.

**Solicitação 2 — Integração com API**

Orientações para estruturar chamadas a modelos de linguagem, configurar parâmetros e tratar situações como ausência de credenciais, indisponibilidade do serviço e respostas vazias.

**Solicitação 3 — Avaliação de respostas institucionais**

Apoio na elaboração de critérios para verificar fidelidade, completude, formato, linguagem e segurança das respostas geradas, incluindo identificação de informações não confirmadas.

## 4. Análise e aproveitamento das sugestões

As sugestões foram avaliadas de acordo com a finalidade do projeto e os resultados observados.

- **Sugestões aproveitadas:** organização modular do código, separação das configurações, tratamento de erros e estruturação dos registros de avaliação.
- **Sugestões modificadas:** ajustes em prompts e respostas institucionais para evitar informações não confirmadas e melhorar a adequação da linguagem.
- **Sugestões não adotadas:** respostas que acrescentavam informações não presentes no contexto, especialmente sobre procedimentos, avaliações técnicas ou prazos.

No experimento RF02, o prompt estruturado manualmente foi selecionado por apresentar maior fidelidade aos dados fornecidos.

## 5. Erros e inadequações identificados

Durante os experimentos e as avaliações, foram observadas situações que exigiram atenção:

- Inclusão de informações não confirmadas nas respostas produzidas pelos prompts A e C do RF02.
- Necessidade de tratamento de falhas nas chamadas de API, incluindo autenticação, limites de requisições e indisponibilidade.
- Identificação de uma redação potencialmente ambígua na minuta institucional do RF09, posteriormente corrigida.

Esses resultados reforçaram a necessidade de conferir as saídas produzidas por modelos generativos.

## 6. Validação dos resultados

A validação foi realizada por meio de testes automatizados, análise dos arquivos produzidos e revisão das respostas institucionais.

Entre as evidências registradas estão:

- Comparação de três estratégias de prompting no RF02.
- Seis testes automatizados de tratamento de respostas e falhas de API no RF04.
- Avaliação de qualidade de dois casos no RF13, sendo um aprovado inicialmente e outro encaminhado para correção manual.
- Execução da suíte completa com 126 testes automatizados aprovados.

A avaliação RF13 apresentou taxa inicial de aprovação de 50%, considerando dois casos independentes. Esse resultado é demonstrativo e não representa uma estimativa geral de qualidade do modelo.

## 7. Limitações e responsabilidade

O uso de ferramentas de IA não elimina a possibilidade de erros, informações inventadas ou inadequações nas respostas.

Os resultados do projeto devem ser interpretados considerando suas limitações, especialmente a utilização de dados fictícios, a disponibilidade dos provedores externos e a necessidade de revisão humana.

A equipe assume a responsabilidade pela conferência das evidências, pelas decisões adotadas na versão entregue e pela apresentação e justificativa técnica da solução.

Nenhuma resposta institucional produzida pelo sistema deve ser enviada automaticamente ao cidadão.

## 8. Referências internas

- `documentacao/avaliacao_rf02.md`
- `documentacao/avaliacao_rf04.md`
- `documentacao/revisao_rf09.md`
- `documentacao/revisao_rf13.md`
- `resultados/logs/`
- `testes/`