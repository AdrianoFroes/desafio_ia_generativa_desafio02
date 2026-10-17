# RF11 — Registro e rastreabilidade

## 1. Objetivo

Implementar registros estruturados de auditoria para acompanhar execuções, resultados, erros e decisões humanas na Central Inteligente de Atendimento e Comunicação Institucional.

A implementação busca permitir a reconstrução das operações realizadas sem expor credenciais ou registrar desnecessariamente dados pessoais e conteúdos integrais.

## 2. Arquivos envolvidos

**Módulos de auditoria e revisão:**

- `src/audit.py`: validação, registro e consulta da auditoria.
- `src/revisao_humana.py`: vínculo da decisão humana ao documento revisado.

**Fluxos integrados à auditoria:**

- `src/comparacao_prompts.py`: comparação de prompts do RF02.
- `src/prompt_seguro.py`: testes de segurança de prompts do RF03.
- `src/extracao.py`: extração estruturada do RF05.
- `src/audio.py`: transcrição de áudio do RF06.
- `src/sintese_voz.py`: síntese de voz do RF07.
- `src/vision.py`: extração de informações de imagem do RF08.
- `src/minuta.py`: geração de minutas do RF09.

**Proveniência de imagem:**

- `src/image_generation.py`: registro próprio de proveniência do RF10, ainda não integrado à auditoria central.

**Testes automatizados:**

- `testes/teste_rf11.py`: auditoria e integração com minutas.
- `testes/teste_rf11_revisao.py`: revisão humana e integridade.
- `testes/teste_rf11_sobrescrita.py`: proteção de arquivos existentes.
- `testes/teste_rf11_gravacao.py`: falhas simuladas de gravação.
- `testes/teste_rf11_falha_auditoria.py`: falhas simuladas da auditoria.
- `testes/teste_rf11_integridade_jsonl.py`: integridade do histórico JSONL.
- `testes/teste_rf11_extracao.py`: integração do RF05.
- `testes/teste_rf11_audio.py`: integração do RF06.
- `testes/teste_rf11_sintese_voz.py`: integração do RF07.
- `testes/teste_rf11_vision.py`: integração do RF08.
- `testes/teste_rf11_comparacao_prompts.py`: integração e auditoria do RF02.
- `testes/teste_rf11_prompt_seguro.py`: integração e auditoria do RF03.

**Outros arquivos:**

- `resultados/logs/auditoria.jsonl`: histórico local de auditoria.
- `.gitignore`: exclusão dos logs locais do versionamento.

## 3. Registros estruturados

A auditoria utiliza o formato JSON Lines (JSONL), com um objeto JSON por linha.

Os registros de execução podem conter:

- UUID da execução.
- Data e hora com informação de fuso horário.
- Requisito e origem.
- Identificador do caso, quando disponível.
- Modalidade de entrada: texto, áudio ou imagem.
- Caminhos dos arquivos de entrada, processamento e saída.
- Provedor e modelo.
- Versão do prompt.
- Parâmetros autorizados.
- Status da execução.
- Duração.
- Quantidade de tokens, quando disponível.
- Situação da revisão humana.
- Código de erro, quando aplicável.

O identificador da execução permite relacionar a saída, os metadados e os eventos de revisão, conforme as informações disponíveis em cada fluxo.

Os registros são acrescentados ao histórico, sem substituir intencionalmente os eventos anteriores.

O conteúdo integral dos prompts e das respostas não é armazenado no registro central de auditoria.

## 4. Integração com os fluxos do projeto

### RF02 — Comparação de prompts

Foi implementado o registro estruturado das execuções de comparação de prompts, incluindo provedor, modelo, parâmetros, duração, tokens quando disponíveis, resultado da execução e referência ao relatório produzido.

A integração foi validada por dois testes automatizados com respostas simuladas:

- Execução bem-sucedida das quatro consultas, com registro dos tokens e da duração.
- Falha simulada na consulta ao modelo, com registro do erro.

Os testes foram aprovados sem chamadas reais à API Gemini.

### RF03 — Segurança de prompts

Foi implementado o registro estruturado dos testes de entrada normal e de tentativa de injeção de prompt.

Cada teste possui identificador de execução, modelo, parâmetros, duração, status, referência ao arquivo produzido e código de erro quando aplicável.

A integração foi validada por três testes automatizados:

- Registro de duas execuções bem-sucedidas.
- Registro de falhas simuladas.
- Proteção contra sobrescrita de resultados existentes.

Os três testes foram aprovados sem chamadas reais à API Gemini.

### RF05 — Extração estruturada

A extração foi integrada à auditoria central, com registro da execução e referência ao arquivo produzido.

O fluxo possui testes de sucesso, falha e proteção contra sobrescrita.

A identificação do caso e a captura de métricas de tokens ainda podem exigir complementação, conforme os dados efetivamente retornados pelo módulo.

### RF06 — Transcrição de áudio

A transcrição foi integrada à auditoria central, incluindo modalidade de entrada, arquivos relacionados, status e informações disponíveis da execução.

Foram realizados testes automatizados com simulações, sem consumo de créditos de API.

### RF07 — Síntese de voz

A síntese de voz foi integrada à auditoria central, com identificação da execução, metadados e referência ao áudio produzido.

Foram implementadas proteções contra sobrescrita e tratamento de falhas simuladas.

Os testes automatizados verificam a integração com a auditoria, a proteção contra sobrescrita, o tratamento de falhas e a gravação efetiva dos arquivos WAV e JSON a partir de uma resposta HTTP simulada, sem chamada real à API Gemini.

O teste de gravação verifica o formato WAV mono, 16 bits, 24 kHz, os metadados, o identificador da execução e a ausência de credenciais no registro de auditoria.

### RF08 — Extração de informações de imagem

O fluxo foi integrado à auditoria central, com identificação da execução, arquivos relacionados, status e revisão humana pendente.

Foram realizados testes automatizados com simulações.

### RF09 — Geração de minutas

A integração automática registra as execuções de geração de minutas.

O programa verifica:

- Revisão humana obrigatória.
- Envio automático desativado.
- Existência da extração RF05.
- Existência do prompt institucional.
- Existência prévia dos arquivos de saída.
- Presença de protocolo no caso.

Na execução bem-sucedida, a minuta e os metadados são publicados antes do registro de sucesso na auditoria.

A revisão humana permanece inicialmente pendente e o envio automático permanece desativado.

### RF10 — Proveniência de imagem

O RF10 possui registro próprio de proveniência, contendo ferramenta utilizada, descrição do modelo, prompt documentado, imagens original e revisada e observações da revisão visual.

A imagem foi produzida no ChatGPT e salva manualmente no projeto.

O registro histórico de proveniência foi preservado, sem atribuição retroativa de identificadores de execução.

A integração do RF10 ao arquivo central `auditoria.jsonl` permanece pendente.

A aprovação humana realizada posteriormente deve ser documentada em evidência própria, sem alterar indevidamente o registro histórico original.

## 5. Proteção da gravação

Os fluxos integrados possuem mecanismos de proteção contra sobrescrita de arquivos existentes e tratamento de falhas, conforme as características de cada módulo.

Na geração de minutas RF09, são utilizados arquivos temporários para preparar a minuta e os metadados.

A publicação dos arquivos definitivos utiliza criação exclusiva, evitando sobrescrita de arquivos existentes.

Em falha simulada durante a publicação dos metadados, o programa remove a minuta incompleta e registra `ERRO_GRAVACAO`.

Em falha simulada no registro de auditoria, o programa remove os arquivos recém-publicados e propaga o erro.

Essas medidas foram verificadas por testes automatizados.

A operação não constitui uma transação totalmente atômica. Interrupções abruptas, falhas de energia e escritas parciais no próprio arquivo de auditoria exigem tratamento adicional.

## 6. Revisão humana e integridade

As decisões humanas são registradas como eventos associados ao UUID de uma execução bem-sucedida.

São permitidas decisões de aprovação e rejeição.

O módulo de revisão permite associar a decisão ao caminho do documento correspondente e ao seu hash SHA-256.

A verificação de integridade permite detectar alterações posteriores no documento associado.

O sistema rejeita decisões duplicadas e documentos que não correspondam à saída da execução.

O registro da decisão não realiza envio automático.

Os registros históricos produzidos antes da implementação da auditoria central permanecem documentados separadamente, sem criação artificial de eventos retroativos.

## 7. Proteção de dados

A auditoria utiliza uma lista restrita de campos permitidos.

Não são armazenados intencionalmente nos registros centrais:

- Chaves de API.
- Texto integral das solicitações.
- Texto integral das respostas do modelo.
- Conteúdo integral das minutas.
- Dados pessoais extraídos dos documentos.

Os arquivos JSONL locais são ignorados pelo Git.

Os arquivos de resultado de cada requisito podem conter informações necessárias à respectiva atividade, mas não devem ser confundidos com os registros centrais de auditoria.

Essas medidas não substituem controles de acesso, política de retenção, cópias de segurança ou demais obrigações aplicáveis da LGPD.

## 8. Testes realizados

A última execução da suíte completa, em 17 de outubro de 2026, apresentou:

**100 testes executados e 100 aprovados.**

Comando utilizado:

`python -m unittest discover -s testes -p "teste_*.py"`

Entre os cenários verificados estão:

- Criação e leitura de registros JSONL.
- Validação de campos e bloqueio de informações indevidas.
- Rastreabilidade de casos e arquivos.
- Integração simulada do RF02, incluindo sucesso, falha e contabilização de tokens.
- Integração simulada do RF03, incluindo sucesso, falha e proteção contra sobrescrita.
- Integração simulada com RF05, RF06, RF07, RF08 e RF09.
- Registro de erros e decisões humanas.
- Aprovação e rejeição.
- Bloqueio de decisões duplicadas.
- Associação da decisão ao documento revisado.
- Verificação de integridade por SHA-256.
- Proteção contra sobrescrita.
- Falhas simuladas na gravação de arquivos.
- Falhas simuladas no registro da auditoria.
- Gravação dos arquivos WAV e JSON do RF07 com resposta HTTP simulada.

Os testes utilizaram dados fictícios e simulações, sem chamadas reais à API Gemini.

A verificação `git diff --check` não identificou erros de formatação, apresentando apenas avisos relacionados à conversão LF/CRLF no Windows.

## 9. Limitações

Permanecem como limitações e verificações pendentes:

- Integração do registro de proveniência RF10 à auditoria central.
- Falhas anteriores ao carregamento da configuração em determinados fluxos.
- Recuperação de registros JSONL parcialmente gravados.
- Garantia de atomicidade em interrupções abruptas.
- Controles de acesso e política de retenção.
- Proteção contra alterações externas nos logs.
- Integração completa das decisões humanas ao fluxo operacional de revisão e publicação.
- Captura e consolidação de custos de execução, quando houver dados e preços verificáveis.
- Complementação de identificadores de caso e métricas de uso nos fluxos que ainda não os disponibilizam.

Os dados de custo não devem ser inventados quando a API ou a configuração não fornecerem informações suficientes para calculá-los.

## 10. Conclusão

O RF11 possui implementação funcional de auditoria estruturada, com identificadores de execução, rastreabilidade de arquivos, registro de erros e vínculo de decisões humanas.

A auditoria foi integrada aos fluxos RF02, RF03, RF05, RF06, RF07, RF08 e RF09, com testes automatizados de integração e tratamento de falhas. O RF10 mantém registro próprio de proveniência, ainda não integrado à auditoria central.

A última execução da suíte completa apresentou **100 testes aprovados**.

A conclusão definitiva do requisito depende da verificação das limitações remanescentes e da conferência final das evidências exigidas pelo enunciado.