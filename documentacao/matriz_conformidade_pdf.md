# Matriz de conformidade — Desafio Prático 1, versão 1.0 (2026)

**Escopo:** análise do pacote de código e evidências, **sem apresentação/vídeo**. Base: `documentacao/enunciado_desafio.pdf`, seções 1, 6 a 11 e 13. **Atendido** significa que existem implementação e evidências correspondentes; não é certificação de uma execução integral em ambiente limpo. **Ressalva** significa que parte do critério não pode ser demonstrada com evidência independente. Esta matriz não altera fatos históricos.

| Requisito | Evidência no pacote | Conclusão e limite |
|---|---|---|
| RF01 — Configuração | `src/main.py`, `config.json`, `.env.example`, `requirements.txt`, `README.md` | Implementação e instruções presentes. Reprodutibilidade integral depende de configuração externa e acesso aos serviços. |
| RF02 — Prompts | `prompts/rf02_A_zero_shot.txt`, `rf02_B_estruturado.txt`, `rf02_C_metaprompt.txt`, `resultados/logs/rf02_20261016_220512.json`, `resultados/logs/rf02_20261016_220512_avaliacao.csv`, `documentacao/avaliacao_rf02.md` | Evidências das três variantes e avaliação presentes. |
| RF03 — Prompt seguro | `src/prompt_seguro.py`, `resultados/logs/rf03_injecao.json`, `resultados/logs/rf03_normal.json`, `documentacao/avaliacao_rf03.md` | Delimitação, instruções e teste adversarial documentados. |
| RF04 — API | `src/llm_client.py`, `testes/teste_rf04.py`, `documentacao/avaliacao_rf04.md` | Código e testes de falhas; chamada real adicional evidenciada em RF07. |
| RF05 — Texto/JSON | `dados/originais/entrada_texto.txt`, `dados/processados/rf05_extracao.json`, `src/extracao.py`, `testes/teste_rf05.py` | Saída estruturada e original preservados. |
| RF06 — Transcrição | `dados/originais/entrada_audio.mp3`, `dados/processados/rf06_transcricao.txt`, `rf06_transcricao_revisada.txt`, `rf06_informacoes.json`, `documentacao/revisao_rf06.md`, `dados/gabaritos/rf06_referencia_origem.json` | **RESSALVA:** revisão por escuta relatada; referência posterior não comprova gabarito independente elaborado antes da inferência (seção 6). Não reclassificar retroativamente. |
| RF07 — TTS | `src/sintese_voz.py`, `resultados/minutas/rf09_minuta_revisada.txt`, `resultados/audios/rf07_minuta_rf09_aprovada.wav`, `rf07_minuta_rf09_informacoes.json`, `rf07_revisao_humana.json` | **Atendido com evidência posterior:** áudio definitivo gerado, hash da minuta confere, aprovação por escuta em 17/10/2026 15h23. O indicador `revisao_audio_pendente` no JSON de geração retrata o momento anterior à escuta e não deve ser adulterado. |
| RF08 — OCR | `dados/originais/entrada_pdf-imagem.pdf`, `dados/processados/rf08_texto_bruto.txt`, `rf08_texto_corrigido.txt`, `rf08_comparacao.json`, `dados/gabaritos/rf08_gabarito_inicial.txt`, `rf08_gabarito.txt`, `documentacao/revisao_rf08.md` | **RESSALVA:** data crítica corrigida manualmente; comparação com gabarito final retrospectivo, não cego. O indicador de revisão pendente no JSON de comparação é histórico; revisão está documentada separadamente. |
| RF09 — Minuta | `src/minuta.py`, `prompts/rf09_minuta_institucional.txt`, `resultados/minutas/rf09_minuta_revisada.txt`, `rf09_minuta_revisada_com_brasao.pdf`, `dados/originais/brasao.png`, `documentacao/revisao_rf09.md` | Minuta revisada, fontes e aviso de não envio; identidade visual usada como protótipo acadêmico. |
| RF10 — Imagem | `src/image_generation.py`, `prompts/rf10_geracao_imagem.txt`, `resultados/imagens/rf10_cartaz_matricula_revisado.png`, `rf10_proveniencia.json`, `documentacao/revisao_rf10.md` | Arte e nota de proveniência presentes; auditoria central não integrada. |
| RF11 — Auditoria | `src/audit.py`, `resultados/logs/auditoria.jsonl`, `resultados/logs/demonstracao_offline.jsonl`, `resultados/audios/rf07_revisao_humana.json`, `documentacao/revisao_rf11.md`, testes RF11 | **PARCIAL COMO EVIDÊNCIA HISTÓRICA:** implementação testada, mas histórico central entregue possui apenas **um evento real** (RF07). O log offline não comprova inferências anteriores. Não fabricar eventos passados. |
| RF12 — Privacidade | `src/privacidade.py`, `documentacao/revisao_rf12.md`, `.gitignore`, `.env.example` | Política de dados fictícios e minimização documentada. Exame estático de arquivos não é garantia absoluta contra todo segredo. |
| RF13 — Qualidade | `src/avaliacao_qualidade.py`, `resultados/logs/rf13_avaliacao.json`, `documentacao/revisao_rf13.md` | Dois casos avaliados, um aprovado e outro corrigido, taxa inicial de 50%. |

## Itens transversais do enunciado

- **Seção 6 — Cenários mínimos:** `dados/originais/entrada_texto.txt`, `entrada_audio.mp3`, `entrada_pdf-imagem.pdf`, `brasao.png`. Os gabaritos RF06 e RF08 têm as limitações temporais declaradas acima.
- **Seção 8 — Fluxo:** `src/demonstracao.py` verifica arquivos existentes **sem** executar as APIs de ponta a ponta. Não é prova de pipeline integral automatizado.
- **Seção 9 — Estrutura:** organização sugerida representada por `src/`, `dados/`, `prompts/`, `resultados/`, `testes/`, `documentacao/`.
- **Seção 10 — Uso de IA:** `documentacao/registro_uso_ia.md`.
- **Seção 11 — Entregáveis:** código, README, requirements, `.env.example`, `.gitignore`, originais, gabaritos, prompts, saídas e relatório incluídos no ZIP.
- **Seção 13 — Segurança:** sem envio automático; `.env` não incluído no pacote. Verificar arquivos antes de publicar em outros repositórios.

## Regra para futuras avaliações

Não confundir **funcionalidade implementada**, **teste com simulação**, **execução real**, **revisão humana posterior** e **gabarito independente prévio**. Uma nova revisão não deve reabrir como 'pendência de geração' o áudio RF07 já produzido e aprovado, nem apresentar o único evento RF07 como histórico completo. Para eliminar as ressalvas históricas seria necessária uma **nova execução prospectiva** com gabaritos preparados antes e coleta de logs desde o início; isso não deve ser fingido como se já tivesse ocorrido.
