# Complemento de conformidade — RF06, RF07, RF08 e RF11

Atualização baseada nas evidências disponíveis em 17/10/2026. Este documento diferencia execução real, decisão humana posterior e limitações históricas.

## RF06 — Transcrição

A nova transcrição está em `dados/processados/rf06_nova_transcricao_20261017_160731.txt`, com metadados em arquivo adjacente. A referência em `dados/gabaritos/rf06_gabarito_validado.txt` foi conferida por escuta humana do áudio original e validada antes da nova execução. A nova transcrição foi aprovada em 17/10/2026 às 16h09; o evento de decisão humana está vinculado à execução e ao SHA-256 do arquivo revisado no log central.

**Limitação preservada:** a referência foi derivada de uma transcrição anterior, ainda que conferida por escuta. Por isso, não é um gabarito independente da primeira inferência. A nova comparação é útil, mas não deve ser descrita como avaliação totalmente cega.

## RF07 — Síntese de voz

O áudio definitivo `resultados/audios/rf07_minuta_rf09_aprovada.wav` foi gerado a partir de `resultados/minutas/rf09_minuta_revisada.txt` e aprovado por escuta humana em 17/10/2026 às 15h23. O hash da minuta registrada nos metadados coincide com o conteúdo do arquivo incluído no pacote. O valor `revisao_audio_pendente` nos metadados de geração representa o estado no momento da geração; a aprovação posterior está registrada separadamente e o valor histórico não foi alterado.

## RF08 — Visão e OCR

Os seis campos do gabarito validado (`codigo_matricula`, `data_nascimento`, `cpf`, `rg`, `data_matricula` e `inicio_curso`) foram confirmados visualmente pelo usuário no PDF original antes da nova execução. O texto bruto está preservado em `dados/processados/rf08_nova_extracao_20261017_161929.txt`; a versão corrigida está em `dados/processados/rf08_nova_extracao_20261017_161929_corrigida.txt`. A versão corrigida foi aprovada em 17/10/2026 às 16h24, e o SHA-256 confere com o evento de decisão humana no log central.

**Limitação preservada:** a aprovação humana da versão corrigida não transforma correções posteriores em acertos originais do OCR. A avaliação da primeira execução permanece retrospectiva; os resultados e gabaritos anteriores foram mantidos.

## RF11 — Auditoria

`resultados/logs/auditoria.jsonl` contém cinco eventos reais:

1. Execução RF07 (síntese de voz).
2. Execução RF06 (nova transcrição).
3. Aprovação humana RF06.
4. Execução RF08 (nova extração OCR).
5. Aprovação humana RF08.

Os eventos de decisão humana referenciam as execuções e, nos casos RF06/RF08, os arquivos aprovados e seus hashes. Os eventos antigos não registrados continuam sem reconstrução retroativa; a demonstração offline registra apenas a conferência offline. RF10 possui nota de proveniência separada, ainda não integrada ao log central.

## Verificação reproduzível

Execute:

```powershell
python -m pytest -q
python -m src.verificar_pendencias
python -m src.demonstracao
```

O verificador não chama APIs nem altera o log de auditoria. A suíte aprovada contém 126 testes no pacote revisado. Os testes não eliminam as limitações históricas descritas acima.
