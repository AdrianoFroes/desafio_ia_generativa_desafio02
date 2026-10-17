# Relatório Técnico Consolidado
## Desafio Prático 1 — Central Inteligente de Atendimento e Comunicação Institucional

### 1. Objetivo

Desenvolver um protótipo de central inteligente capaz de apoiar o tratamento de solicitações institucionais recebidas em diferentes formatos, incluindo texto, áudio e documentos digitalizados.

A solução utiliza inteligência artificial generativa para interpretar informações, organizar dados, elaborar minutas de resposta, produzir áudio acessível e criar material visual ilustrativo.

O projeto utiliza casos fictícios, mantém a revisão humana obrigatória e não realiza envio automático de respostas ao cidadão.

### 2. Arquitetura e tecnologias

A solução foi desenvolvida em Python, com organização modular dos requisitos funcionais RF01 a RF13.

O processamento envolve as seguintes etapas:

1. Recebimento de dados fictícios em texto, áudio ou documento digitalizado.
2. Preparação e minimização de informações pessoais quando aplicável.
3. Processamento por modelos de inteligência artificial.
4. Organização das informações e geração dos arquivos de resultado.
5. Produção de minuta institucional e recursos complementares de acessibilidade.
6. Registro de auditoria e avaliação de qualidade.
7. Revisão humana antes de qualquer utilização institucional.

As principais tecnologias utilizadas foram Python, API Google Gemini, ferramentas de geração de imagem do ChatGPT, JSON, JSONL e PyMuPDF.

### 3. Modelos e ferramentas utilizados

| Atividade | Modelo ou ferramenta |
|---|---|
| Comparação de prompts e geração de texto | Gemini 3.8 Flash |
| Extração estruturada | Gemini, por meio do cliente de API do projeto |
| Transcrição de áudio | Gemini 3.5 Transcribe |
| Síntese de voz | Gemini 2.5 Flash Preview TTS |
| OCR e interpretação de documento digitalizado | Gemini 3.8 Flash |
| Geração de minuta institucional | Gemini 3.8 Flash |
| Geração e revisão de imagem | Ferramenta de imagens do ChatGPT |

A geração de imagem foi realizada pela interface do ChatGPT, após uma tentativa com o modelo Gemini 2.5 Flash Image retornar erro HTTP 429, relacionado à indisponibilidade de cota gratuita.

### 4. Engenharia de prompts e segurança

No RF02, foram comparadas três estratégias de prompting:

- **Prompt A — Zero-shot:** resposta parcialmente fiel, com inclusão de informações não fornecidas.
- **Prompt B — Estruturado:** maior fidelidade, sem informações inventadas identificadas na execução.
- **Prompt C — Metaprompting:** resposta organizada, mas com acréscimos não confirmados.

O Prompt B foi selecionado por apresentar maior fidelidade aos dados disponíveis.

No RF03, foram realizados testes de resistência à injeção de prompt. O caso avaliado preservou as informações institucionais e manteve a revisão humana obrigatória.

Esses resultados não garantem proteção contra todas as tentativas de manipulação.

### 5. Integração com API

O RF04 implementou um cliente para comunicação com o Gemini, incluindo configuração, tratamento de erros, controle de tempo de execução e obtenção de informações de uso.

Foi realizada uma consulta real, com resposta recebida em 5,76 segundos.

Também foram aprovados seis testes automatizados com respostas simuladas, incluindo situações de falha de autenticação, limite de requisições, indisponibilidade e resposta vazia.

A integração depende da disponibilidade do serviço externo e das cotas de utilização.

### 6. Resultados do processamento multimodal

**RF05 — Extração textual**

A solicitação fictícia foi processada e organizada em JSON válido.

O sistema identificou o protocolo 2026-000142, a data 14/10/2026, o assunto relacionado à matrícula e a ausência de informação confirmada sobre documentos pendentes.

**RF06 — Transcrição de áudio**

O áudio fictício foi transcrito utilizando o modelo Gemini 3.5 Transcribe.

A execução registrou 3,47 segundos e produziu 766 caracteres.

A transcrição foi conferida por escuta humana, sem divergências identificadas.

**RF07 — Síntese de voz**

Foi produzido um arquivo WAV utilizando o modelo Gemini 2.5 Flash Preview TTS, com voz Kore e orientação de leitura institucional em português brasileiro.

A revisão humana confirmou a correspondência entre o áudio e a minuta de teste.

Além do ensaio com minuta de teste, foi gerado o áudio definitivo `resultados/audios/rf07_minuta_rf09_aprovada.wav` a partir da minuta revisada RF09 em 17/10/2026. A aprovação por escuta ocorreu posteriormente, às 15h23, e está registrada em `resultados/audios/rf07_revisao_humana.json`. Os metadados originais preservam o estado "revisao_audio_pendente" no momento da síntese; não se trata de pendência atual.

**RF08 — OCR e visão multimodal**

Foi processado um PDF digitalizado contendo uma ficha fictícia de matrícula.

A extração utilizou o modelo Gemini 3.8 Flash e registrou 60,79 segundos e 2.273 tokens totais.

O resultado foi conferido com o documento original.

Na revisão complementar de 17/10/2026, foi identificado um erro de OCR na data da matrícula. O PDF original apresenta 14/10/2026, enquanto o Gemini extraiu 14/01/2026.

A saída original da IA foi preservada em rf08_texto_bruto.txt. A data foi corrigida manualmente em rf08_texto_corrigido.txt e no gabarito final.

A divergência demonstra a necessidade de revisão humana dos campos críticos antes de qualquer utilização institucional.

O gabarito inicial apresentou divergências posteriormente esclarecidas por revisão humana. O gabarito final foi atualizado após a execução, não constituindo uma referência integralmente independente.

A comparação automática complementar, realizada com o script
`src/comparacao_vision.py`, adaptado da contribuição de Adriano Froes
da Costa, avaliou 22 campos estruturados: 21 correspondentes e
1 divergente (data da matrícula), resultando em 95,45% de
correspondência dos campos. A similaridade textual completa foi
de 89,68%, mas não representa a taxa de acerto dos campos.
O resultado foi registrado em `dados/processados/rf08_comparacao.json`.
**RF09 — Minuta institucional**

Foi gerada uma minuta de resposta a partir das informações extraídas do caso fictício.

A execução registrou 3,38 segundos e 836 tokens totais.

A minuta foi aprovada com ajuste humano para evitar interpretação de compromisso institucional não confirmado.

A versão revisada permanece como rascunho, sem envio ao cidadão.

**RF10 — Imagem institucional ilustrativa**

Foi produzida uma peça visual sintética relacionada à orientação sobre matrícula.

A primeira versão foi revisada para substituir uma afirmação sobre documentos pendentes por uma orientação de verificação.

A versão final contém identificação de conteúdo gerado por inteligência artificial.

### 7. Auditoria e rastreabilidade

O RF11 implementou registros estruturados em JSONL, com identificação das execuções, informações técnicas, referências aos arquivos, erros e decisões humanas.

O sistema permite associar decisões de revisão a documentos por meio de identificadores e hashes SHA-256.

A auditoria foi integrada aos fluxos RF02, RF03, RF05, RF06, RF07, RF08 e RF09.

O RF10 mantém registro próprio de proveniência, ainda não integrado à auditoria central.

Os logs locais são excluídos do versionamento e não devem armazenar credenciais ou conteúdos pessoais integrais.

### 8. Privacidade e LGPD

O RF12 implementou mecanismos básicos de minimização de dados nos fluxos textuais, incluindo ocultação de padrões conhecidos de informações pessoais.

O projeto considera os princípios de finalidade, adequação, necessidade, segurança e prevenção da Lei Geral de Proteção de Dados Pessoais.

Foram utilizados exclusivamente cenários fictícios.

A minimização implementada não garante anonimização completa. Arquivos de áudio, imagem e documentos também podem conter informações pessoais que exigiriam proteção adicional em uma aplicação real.

A utilização institucional dependeria de controles de acesso, políticas de retenção, avaliação dos provedores, medidas de segurança e análise jurídica.

### 9. Avaliação de qualidade

O RF13 definiu cinco critérios de avaliação, com pontuação de zero a dois pontos por critério:

- Fidelidade.
- Completude.
- Formato.
- Linguagem.
- Segurança.

A aprovação exige pontuação mínima de oito pontos, ausência de erro moderado ou grave e pontuação positiva em fidelidade e segurança.

Foram avaliados dois casos independentes:

| Caso | Pontuação | Resultado inicial |
|---|---:|---|
| RF03 — Injeção de prompt | 10/10 | Aprovado |
| RF09 — Minuta institucional | 8/10 | Correção manual necessária |

A taxa inicial de aprovação foi de 50%.

Esse percentual é apenas demonstrativo, devido à quantidade reduzida de casos avaliados.

A suíte completa do projeto registrou 123 testes automatizados aprovados.

### 10. Custos e desempenho

As execuções reais registraram tempos e informações de tokens quando disponibilizados pelos provedores.

Não foi possível consolidar um custo financeiro confiável para todas as operações, pois os preços aplicáveis por modelo e modalidade não estavam completamente configurados e confirmados.

A geração de imagem pela API Gemini foi limitada pela cota gratuita disponível.

Os resultados demonstram que o custo operacional depende do volume de solicitações, da modalidade de processamento, dos tokens consumidos e das condições comerciais dos provedores.

Antes de qualquer implantação, seria necessário estabelecer limites de consumo, monitoramento financeiro e critérios de escolha dos modelos.

### 11. Limitações e riscos

As principais limitações identificadas foram:

- Dependência de serviços externos e de suas cotas.
- Possibilidade de respostas inventadas ou ambíguas.
- Necessidade de conferência de transcrições e documentos digitalizados.
- Proteção limitada de dados pessoais por expressões regulares.
- Ausência de integração completa do RF10 à auditoria central.
- Falta de controles de produção para autenticação, retenção e recuperação de falhas.
- Avaliação de qualidade realizada com número reduzido de casos.
- Ausência de envio automático, por decisão de segurança.
- Necessidade de confirmação humana de informações administrativas.

### 12. Conclusão

O projeto demonstrou a utilização de inteligência artificial generativa em diferentes etapas do atendimento institucional, incluindo interpretação textual, processamento de áudio, leitura de documentos, geração de minutas e produção de material visual.

Os resultados evidenciaram a importância da engenharia de prompts, da proteção de dados, da rastreabilidade e da revisão humana.

O protótipo atende a uma finalidade educacional e não constitui um sistema pronto para utilização em produção.

Qualquer aplicação institucional real exigiria avaliações adicionais de segurança, privacidade, desempenho, custos e governança.

**A responsabilidade pelas decisões e pela utilização das respostas permanece humana.**

### Complemento de entrega — identidade visual e demonstração

As versões de apresentação `resultados/minutas/rf09_minuta_com_brasao.pdf` e
`resultados/minutas/rf09_minuta_revisada_com_brasao.pdf` incorporam a imagem
`dados/originais/brasao.png`, com aviso expresso de protótipo acadêmico, sem
chancela institucional. As minutas `.txt` originais e revisadas foram preservadas.

O módulo `src/demonstracao.py` apresenta o encadeamento das evidências de
texto, áudio, OCR, minuta, imagem e avaliação, sem novas chamadas a APIs.
O log `resultados/logs/demonstracao_offline.jsonl` registra a execução real
dessa verificação, e **não** representa auditoria retroativa das inferências.

O comando `python -m src.main` continua restrito à inicialização.
A demonstração offline não substitui uma execução multimodal ponta a ponta,
e a síntese RF07 final está disponível com revisão humana documentada. A demonstração offline não representa execução integral da cadeia de APIs.
