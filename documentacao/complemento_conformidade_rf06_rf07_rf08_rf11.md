# Complemento de conformidade — RF06, RF07, RF08 e RF11

## RF06 — Referência de transcrição
O arquivo `dados/gabaritos/rf06_referencia_posterior.txt` foi criado **depois** da inferência, a partir da transcrição revisada. Não constitui gabarito independente; compará-lo à transcrição revisada é circular. A documentação anterior relata revisão por escuta, mas não permite demonstrar que existia referência anterior à execução. Para resolver plenamente, ouvir o MP3 original e produzir uma referência humana independente, identificando a data e o responsável, sem alegar criação anterior.

## RF07 — Minuta aprovada
A síntese de ensaio permanece preservada. O comando `python -m src.sintese_voz resultados/minutas/rf09_minuta_revisada.txt --aprovado --final-rf09` utiliza o texto revisado RF09 e gera arquivos separados. Só executar após confirmar a aprovação da minuta e a disponibilidade de créditos da API. A saída mantém revisão por escuta pendente, mesmo que o modelo conclua a geração. Registrar manualmente a escuta, a data e a decisão, sem marcar aprovação antecipadamente.

## RF08 — Avaliação do OCR
O gabarito final foi ajustado depois do OCR; a divergência da data de matrícula foi registrada. O resultado é uma avaliação retrospectiva e não um teste cego. Preservar o gabarito inicial, o texto bruto e a correção humana.

## RF11 — Auditoria
O módulo de auditoria registra eventos de execuções futuras. O histórico das inferências antigas não pode ser criado retroativamente como log original. `demonstracao_offline.jsonl` comprova apenas conferência offline. Caso exista `auditoria.jsonl` original no computador, verificar integridade e confidencialidade antes de incluí-lo no pacote. A ausência de histórico completo permanece uma limitação do protótipo.
