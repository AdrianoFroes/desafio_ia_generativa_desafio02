\# RF12 — LGPD, privacidade e minimização de dados



\## 1. Objetivo



Demonstrar os cuidados adotados no protótipo Central Inteligente de Atendimento e Comunicação Institucional para reduzir a exposição desnecessária de informações durante o processamento por inteligência artificial.



O projeto utiliza exclusivamente cenários fictícios. A implementação considera os princípios de finalidade, adequação, necessidade, segurança e prevenção previstos na LGPD.



\## 2. Identificação dos campos e avaliação de riscos



A classificação abaixo considera como os campos seriam tratados em um cenário real de atendimento institucional.



| Campo | Seria dado pessoal? | Finalidade | Necessidade | Risco | Proteção |

|---|---|---|---|---|---|

| Nome do solicitante | Sim | Identificar o cidadão | Não necessário para classificar o assunto | Identificação indevida | Substituição por marcador |

| CPF e RG | Sim | Identificação cadastral | Desnecessários para as tarefas demonstradas | Fraude e exposição de identificadores | Ocultação de padrões conhecidos |

| E-mail | Sim | Contato com o cidadão | Desnecessário para classificação e geração da minuta | Exposição de contato | Ocultação |

| Telefone | Sim | Contato com o cidadão | Desnecessário para geração da minuta | Contato indevido e exposição | Ocultação ou exclusão do campo |

| Data de nascimento | Sim | Eventual identificação cadastral | Desnecessária para o protótipo | Exposição de informação pessoal | Ocultação de padrão conhecido |

| Nome da mãe | Sim | Eventual identificação cadastral | Desnecessário para o protótipo | Exposição de informação familiar | Ocultação de padrão conhecido |

| Protocolo | Pode ser, quando vinculado a uma pessoa identificável | Relacionar solicitação e atendimento | Necessário para rastreabilidade | Reidentificação por associação | Utilização de identificador fictício |

| Data da solicitação | Pode ser dado associado a uma pessoa | Contextualizar o atendimento | Necessária quando relevante | Associação com histórico individual | Uso de data fictícia |

| Assunto e pedido | Podem conter dados pessoais | Compreender a solicitação | Necessários para a resposta | Exposição de dados inseridos em texto livre | Minimização antes do envio |

| Categoria | Geralmente não identifica alguém isoladamente, mas pode compor um perfil | Classificar a solicitação | Necessária | Inferências sobre o cidadão | Categorias padronizadas |

| Documentos pendentes | Podem revelar informações pessoais | Informar pendências verificadas | Necessários apenas quando confirmados | Exposição ou informação incorreta | Sinalização de ausência e revisão humana |



\## 3. Medidas técnicas implementadas



O módulo `src/privacidade.py` disponibiliza:



\- `minimizar\_texto()`: oculta padrões conhecidos de informações pessoais.

\- `minimizar\_campos()`: seleciona campos autorizados e minimiza os valores textuais.



No RF05, o texto da solicitação passa por preparação antes de ser enviado ao modelo para classificação e interpretação.



No RF09, somente os campos selecionados pela função `preparar\_dados()` são utilizados para construir o contexto enviado ao modelo. Seus valores textuais também passam pela minimização.



O módulo de auditoria RF11 utiliza campos controlados e não deve registrar credenciais ou o conteúdo integral das solicitações.



O envio automático de respostas institucionais permanece desativado, e a revisão humana é obrigatória.



\## 4. Evidências dos testes



Foram executados 11 testes automatizados específicos de privacidade, todos aprovados.



Naquela etapa intermediária, a suíte apresentou 111 testes aprovados. Na verificação final da entrega, a suíte completa apresentou 123 testes aprovados.



Uma verificação local com dados fictícios confirmou:



\- Ocultação de CPF e e-mail no campo `pedido`.

\- Exclusão de telefone não autorizado.

\- Preservação do protocolo e do assunto.

\- Ausência de chamadas reais ao provedor durante os testes.



\## 5. Minimização no envio ao provedor



O protótipo aplica minimização nos fluxos textuais RF05 e RF09.



Nos fluxos de áudio e imagem, o envio do conteúdo pode expor informações presentes nos arquivos. Portanto, esses recursos devem ser utilizados exclusivamente com materiais fictícios, previamente revisados.



O processamento local deve ser considerado quando houver necessidade de maior controle, confidencialidade ou soberania dos dados.



\## 6. Limitações e riscos residuais



A proteção baseada em expressões regulares não identifica todas as formas de dados pessoais, como nomes escritos em estruturas diferentes, endereços ou informações contextuais que permitam reidentificação.



Também existe risco de exposição em textos livres, arquivos de áudio, imagens e documentos.



A minimização não representa anonimização irreversível e não torna seguro o processamento de dados pessoais reais.



O projeto não deve receber documentos reais ou sigilosos. Em um cenário de produção, seriam necessárias medidas adicionais, incluindo avaliação jurídica, controle de acesso, políticas de retenção, tratamento de incidentes e avaliação dos contratos com provedores.



\## 7. Conclusão



O RF12 demonstra a aplicação de minimização de dados nos fluxos textuais e documenta os riscos associados aos campos processados.



A solução permanece restrita a dados fictícios e exige revisão humana. A verificação final das evidências e dos arquivos destinados à entrega deve confirmar a ausência de credenciais e dados pessoais reais.
