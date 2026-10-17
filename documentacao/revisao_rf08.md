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
