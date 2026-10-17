# RF08 — Visão e OCR

## Objetivo

Extrair informações de um documento digitalizado utilizando visão multimodal e conferir os resultados com o documento original.

## Documento utilizado

Arquivo: dados/originais/entrada_pdf-imagem.pdf

Tipo: ficha de matrícula fictícia.

O documento possui uma página e não contém texto selecionável.

## Implementação

Foi utilizado o arquivo src/vision.py.

O programa converte a página do PDF em imagem PNG utilizando PyMuPDF e envia a imagem para a API do Gemini.

Modelo utilizado: gemini-3.8-flash.

Tempo registrado: 60,79 segundos.

Tokens totais registrados: 2.273.

## Arquivos produzidos

- rf08_texto_bruto.txt: resultado original da IA.
- rf08_texto_corrigido.txt: versão conferida.
- rf08_informacoes.json: informações da execução.
- rf08_gabarito_inicial.txt: referência elaborada antes do OCR.
- rf08_gabarito.txt: referência final revisada.

Os arquivos com dados de identificação foram mantidos localmente e ignorados pelo Git.

## Comparação com o gabarito

A comparação inicial identificou divergências em campos como código, nome, datas e documentos de identificação.

A conferência humana posterior do PDF confirmou os valores extraídos pelo Gemini.

Assim, as divergências identificadas nesses campos decorreram de erros ou incertezas do gabarito provisório.

O gabarito inicial foi preservado para demonstrar a evolução da revisão.

A referência final foi atualizada depois da execução do OCR e, portanto, não representa uma avaliação independente feita integralmente antes da execução.

## Revisão humana

Situação: aprovada.

A pessoa responsável conferiu o documento original e confirmou a extração do Gemini, incluindo os campos críticos.

A versão corrigida mantém o conteúdo extraído, pois não foram solicitadas alterações após a conferência.

## Incertezas e limitações

A leitura inicial apresentou incertezas em campos manuscritos, especialmente documentos de identificação.

Essas informações exigiram conferência humana.

Modelos multimodais podem confundir números, letras e datas, principalmente em documentos digitalizados de baixa qualidade.

O sistema não deve considerar uma transcrição automática como confirmação definitiva de identidade.

## Privacidade e processamento local

O exercício utiliza dados fictícios.

Mesmo assim, documentos de matrícula contêm informações que exigem cuidado, como nome, nascimento, documentos de identificação e contato.

O processamento local seria preferível quando houver dados reais protegidos, restrições de compartilhamento com provedores externos ou exigências de soberania e governança.

Nesses casos, uma ferramenta de OCR local pode reduzir a exposição dos documentos a serviços externos, embora também exija controles de segurança.

## Resultado

A extração por visão multimodal funcionou e foi aprovada na revisão humana.

O envio de informações e a utilização institucional dos dados continuam dependendo das etapas posteriores do projeto.

## Revisão complementar — 17/10/2026

Durante uma nova conferência do documento original, foi identificada
uma divergência na data da matrícula.

- Data no PDF original: 14/10/2026.
- Data extraída pelo Gemini: 14/01/2026.
- Data correta após conferência humana: 14/10/2026.

A extração automática confundiu o mês 10 com o mês 01.

O arquivo rf08_texto_bruto.txt foi preservado como evidência
da saída original da IA.

O arquivo rf08_texto_corrigido.txt foi atualizado com a data correta.

O arquivo rf08_gabarito.txt também foi atualizado para refletir
a conferência visual do documento original.

O gabarito inicial foi mantido sem alterações.

### Conclusão atualizada

O RF08 foi executado com sucesso, mas apresentou um erro de OCR
em um campo crítico: a data da matrícula.

O erro foi identificado em uma conferência humana complementar
e corrigido na versão revisada.

Portanto, a extração automática não deve ser considerada
integralmente correta sem revisão humana.


## Comparação automática complementar — 17/10/2026

Foi incorporado ao projeto o script src/comparacao_vision.py,
adaptado a partir da contribuição de Adriano Froes da Costa.

O programa compara a saída original do Gemini com o gabarito
revisado, sem realizar novas chamadas à API.

### Resultados

- Campos estruturados avaliados: 22.
- Campos correspondentes: 21.
- Campos divergentes: 1.
- Taxa de correspondência dos campos: 95,45%.
- Similaridade textual completa: 89,68%.
- Campo divergente: DATA MATRICULA.

O Gemini extraiu 14/01/2026, enquanto a conferência visual
do PDF original confirmou 14/10/2026.

A similaridade textual considera também informações adicionais
do gabarito e não representa a taxa de acerto dos campos.

O gabarito final foi revisado após a extração, portanto esta
comparação não constitui uma avaliação totalmente independente.

O resultado automático permanece sinalizado para revisão humana.
A divergência identificada foi conferida e corrigida manualmente
na versão revisada do texto.

Esta avaliação complementar atualiza a conclusão da revisão
humana inicial, que não havia identificado o erro na data.

O resultado detalhado foi registrado em
dados/processados/rf08_comparacao.json.


## Atualização da nova execução e aprovação — 17/10/2026

Antes da nova execução, seis campos foram confirmados visualmente no PDF original e registrados em `dados/gabaritos/rf08_gabarito_validado.json`, com metadados e SHA-256 do documento em `rf08_gabarito_validado_origem.json`. A nova extração bruta está em `dados/processados/rf08_nova_extracao_20261017_161929.txt`. Ela repetiu a divergência da data de matrícula (`14/01/2026` em vez de `14/10/2026`) e apresentou variações no nome e no e-mail; essas correções humanas foram aplicadas na versão `rf08_nova_extracao_20261017_161929_corrigida.txt`, sem sobrescrever a saída bruta.

A pessoa responsável aprovou a versão corrigida às 16h24. O evento de decisão humana em `resultados/logs/auditoria.jsonl` identifica a execução, o arquivo revisado e o SHA-256, que foi conferido no pacote. A aprovação diz respeito à versão corrigida, não significa que o OCR bruto estava integralmente correto. A avaliação retrospectiva anterior permanece preservada e não deve ser apresentada como teste cego.
