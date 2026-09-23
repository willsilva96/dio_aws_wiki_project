# 📝 Resposta do Laboratório: A Wiki Perdida dos Arquivos Corporativos

> Preencha este arquivo com a sua proposta de solução.
>
> Sua resposta deve explicar como transformar os documentos brutos da pasta `raw/` em uma Wiki Corporativa Inteligente, pesquisável e segura usando apenas serviços da AWS.

---

## 👤 Identificação

**Nome:**  
Wilian Pereira da Silva

**Data:**  
08/09/2026

**Link do repositório:**  
[Github: Dio AWS Wiki Project](https://github.com/willsilva96/dio_aws_wiki_project)

---

# ✅ Quest 1: O Mapa dos Arquivos Perdidos

## 1.1 Formatos encontrados na pasta `raw/`

Descreva quais tipos de arquivos existem dentro da pasta `raw/`.

```md
Exemplo de como responder, com o formato e o que ele implica:
- <extensao>: <nasce digital ou precisa de OCR?>, <o que da para extrair>
```

> Abra a pasta e liste o que voce encontrou de fato. Esta quest avalia a sua
> leitura do acervo, entao a resposta certa e a que corresponde aos arquivos.

**Sua resposta:**

```md
 Criei um script utils.py o qual possui uma função que irá retornar um dicionario para os arquivos presentes na pasta com seus atributos (Path, Name e Type), posteriormente cada tipo poderá ser processado de uma maneira. 
```

---

## 1.2 Principais desafios encontrados

Explique quais dificuldades esses documentos podem apresentar.

```md
Exemplo:
- Arquivos sem padrão de nomenclatura
- Documentos escaneados com baixa qualidade
- Textos manuscritos ou parcialmente ilegíveis
- Atas com estruturas diferentes
- Informações importantes espalhadas em vários formatos
```

**Sua resposta:**

```md
Nomenclatura despadronizada gera um desafio para tornar os dados estruturados ao longo do tempo, considerando que reunioes tem um fator determinamente sobre os dados e decisões tomadas nela, que é o tempo. Documentos de baixa qualidade geram o desafio de definir um indicador de precisão minima na coleta para consideração, assim como escrita problematica. Os diferentes formatos geram o desafio em criar pipelines apartados para tratamento separado definido pelo tipo do arquivo.
```

---

## 1.3 Informações importantes a serem extraídas

Liste quais informações precisam ser identificadas para transformar os documentos em conhecimento pesquisável.

**Sua resposta:**

```md
Data e Hora da Reunião 
Responsavel
Itens adicionais de classificação da reunião
Participantes - Nome
Participantes - Função
Participantes - Papel na reunião
Objetivos e Pauta
Indicadores tratados na reunião (nomes e valores)
Comentarios Gerais durante a reunião
Planos de ação e itens para acompanhamento estabelecidos na reunião
Riscos e Oportunidades
Comentarios Finais
```

---

## 1.4 Estratégia de classificação inicial

Como você classificaria os documentos sem depender de subpastas dentro de `raw/`?

**Sua resposta:**

```md
Os classificaria por tipo do arquivo, arquivos csv são mais simples de realizar o tratamento pois possuem uma estrutra de colunas e linhas determinadas. Para os arquivos de imagem ou documentos (como pdf), irei trata-los em um pipeline partado para itentificação de elementos importantes.
```

---

# ✅ Quest 2: O Portal de Entrada na AWS

## 2.1 Armazenamento dos arquivos brutos

Explique como os arquivos da pasta `raw/` seriam enviados e armazenados na AWS.

Serviços que você pode considerar:

- Amazon S3
- AWS IAM
- AWS KMS
- Amazon S3 Versioning
- Amazon S3 Lifecycle

**Sua resposta:**

```md
Considerei o S3 para armazenamento dos arquivos, e o IAM para gestão das chaves de acesso e segurança para gestão do Bucket forma segura em connections.py. E KNS para criptografica dos arquivos.
```

---

## 2.2 Preservação dos arquivos originais

Explique como garantir que os arquivos originais sejam mantidos intactos e rastreáveis.

**Sua resposta:**

```md
No script create_bucket em utils.py inclui uma variavel por padrão definida como True para enable_object_lock, dessa forma de o S3 irá aplicar regras de retenção para os arquivos carregados e eles não poderam ser apagados ou modificados.
```

---

## 2.3 Extração de texto dos documentos

Explique como cada tipo de arquivo seria processado.

Considere:

- PDFs escaneados;
- Imagens;
- PDFs digitais;
- Arquivos `.txt`;
- Arquivos `.docx`;
- Arquivos `.md`.

Serviços que você pode considerar:

- Amazon Textract
- AWS Lambda
- AWS Step Functions
- Amazon S3
- Amazon CloudWatch

**Sua resposta:**

```md
Separei o processamento por tipo de arquivo e na sequencia os transformando em arquivos markdown em um bucket expecificos. 

Amazon S3 usado para armazemaneto dos dados originais, e para o novo bucket de .md processados

AWS Lambda orquestra o processamento de acordo com o tipo de arquivo, e direciona para o novo bucket

Amazon Textract processa imagems e arquivos pdf com pouco texto detectado pela biblioteca pypdf, buscando retenção de custos desncessarios ao utilizar o Textract .

Arquivos txt e docx apenas transformo em .md e envio para o bucket de arquivos processaods.

```

---

## 2.4 Tratamento de falhas

Explique como sua solução identificaria e registraria erros de processamento.

**Sua resposta:**

```md
A cada execução será chamado a função log.pt o qual irá orquestrar um conjuto de itens a serem registrados no padrão Cloud Watch e irá enviar os logs para um bucket do S3 exclusivo para os registros (Sucesso, Erro e Informação). Com a estrutura de ids (batch_id e trace_id) cada execução irá manter um vinculo para a atividade executada no fluxo
```

---

# ✅ Quest 3: A Relíquia dos Metadados

## 3.1 Padronização dos textos processados

Explique como os textos extraídos seriam limpos, normalizados e preparados para consulta.

**Sua resposta:**

```md
Unificação para markdown, todo arquivo é processado para gerar arquivo .md aramazenado em um bucket intermediario assim procesamento utilizando LLMs para obter dados e enriquecimento fica facilitado devido ao proprio escopo de leitura facilitado desse tipo de arquivo.
```

---

## 3.2 Metadados propostos

Defina quais metadados você extrairia de cada documento.

| Metadado | Por que ele é importante? |
|---|---|
| Nome do documento | Permite rastreabilidade para o arquivo original em todas as camadas de visualização e tratamento |
| Tipo do documento | Permite tratamento condicional, contingenciado custos utilizando o melhor metodo para cada especificidade|
| Data identificada | Permite criar evolução temporal das informações facilitando analise|
| Tema principal | Ajuda a sumarizar os dados visualizado para o assunto, e apoia LLMs no enrequecimento do contexto |
| Participantes | Ajuda na convernancia e no enrequecimento das informações |
| Decisões tomadas | Ajuda na rastreabilidade dos resultados futuros, permitindo entender os impactos futuros dos resultados |
| Responsáveis | Toma ciencia do que foi discutido, apoia na governancia das informações discutidas |
| Próximos passos | Da mesma forma que as decisões tomadas, mas permite cateogriazação das ações |
| Nível de confidencialidade | Restringe ou permite a visualização e manutenção das informações de acordo com o estabelecido para a reunião e apoia auditorias futuras e o processamento para repostas da Wiki |
| Caminho do arquivo original | Rastreabilidade e governancia |

---

## 3.3 Uso de IA para enriquecimento dos documentos

Explique como o Amazon Bedrock poderia ajudar a identificar temas, decisões, responsáveis, pendências e resumos dos documentos.

**Sua resposta:**

```md
Utilização de skills declarativas que pode ser utilizado por modelos no Amazon Bedrock como a Skill de convernancia, o qual possui o fluxo de avaliar os arquivos markdown intermediarios em busca de metadadados definidos para enrequecimento em um json que pode ser facilmente utilizado. 
```

---

## 3.4 Armazenamento dos metadados

Explique onde os metadados seriam armazenados e como seriam conectados aos documentos originais.

Serviços que você pode considerar:

- Amazon S3
- Amazon DynamoDB
- AWS Glue Data Catalog
- Amazon Bedrock Knowledge Bases

**Sua resposta:**

```md
Nesse caso foi utilizado o S3 Compaion File, que degera um .json para cada arquivo normalizado. E cada arquivo armazena explicitamente o caminho do arquivo bruto oringal, mantendo a rastrabilidade e mantendo o arquivo fisico original imutavel, formato exigido pelo Amazon Bedrock Knowledge Bases
```

---

# ✅ Quest 4: O Oráculo da Wiki Inteligente

## 4.1 Estratégia de indexação

Explique como os documentos seriam divididos em trechos menores e preparados para busca semântica.

**Sua resposta:**

```md
Com o indexer.py os arquivos .md processados de enriquecidos são quebrados em arquivos menores em um novo bucket utlizando a estrategia de tokenrização baseado em semantica mantendo um numero determinado de palavras para o proximo bloco quebrado. Com o chunk_index a rastreabilidade se mantem. 
```

---

## 4.2 Busca semântica e base vetorial

Explique como embeddings seriam gerados e onde seriam armazenados.

Serviços que você pode considerar:

- Amazon Bedrock Knowledge Bases
- Amazon OpenSearch Serverless
- Amazon Aurora PostgreSQL com pgvector
- Amazon S3 Vectors
- Modelos de embeddings no Amazon Bedrock

**Sua resposta:**

```md
Aqui o Amazon Titan apoiaria na transformação dos textos em dos dados em vetores numericos, que poderam ser lidos pelo Amazon OpenSearch Serverless.
```

---

## 4.3 Geração de respostas com IA

Explique como a Wiki responderia perguntas em linguagem natural com base nos documentos originais.

Considere explicar:

- Como a pergunta do usuário seria recebida;
- Como os trechos relevantes seriam recuperados;
- Como o Amazon Bedrock geraria a resposta;
- Como a resposta indicaria as fontes utilizadas.

**Sua resposta:**

```md
O modulo user_ask.py, recebe a pergunta do usuario, e a pergunta é vetorizada pelo Text Embeddings. O serach_documentos.py busca no dados bucket de dados preocessos em .md e seus metadados de enriquecimento. O Amazon Bedrock utiliza skil wiki_oracle que impoem regras de restrição para a reposta. Todas as respostas fornecem a fonte pelo "source_file" com indetnficação de datas e outros trechos relevantes
```

---

## 4.4 Interface de consulta

Proponha como os usuários acessariam essa Wiki Inteligente.

Serviços que você pode considerar:

- Amazon Q Business
- AWS Amplify
- Amazon API Gateway
- AWS Lambda
- Amazon Cognito

**Sua resposta:**

```md
Poderia ser utilizado um portal Web hospedado no Amazon Amplify ou utilizando o Amazon Q Business o qual seria usado para disponibilizar um chat comporativo. O Amazon Cognito forneceria a tela de login SSO. Com o API Gateway as apis para chamdas seriam expostas e executadas com Amazon Lambda as chamadas para a api do user_ask.py seriam feitas, e as repostas seriam obtidas. 
```
---

## 4.5 Segurança, auditoria e monitoramento

Explique como controlar acesso, proteger dados, auditar consultas e monitorar custos, erros e qualidade das respostas.

Serviços que você pode considerar:

- AWS IAM
- AWS KMS
- Amazon Cognito
- AWS CloudTrail
- Amazon CloudWatch
- Amazon Macie
- AWS Cost Explorer

**Sua resposta:**

```md
O Amazon Cognito faria o papel de atenticar os usuarios para acessar a ferramenta/ Solução. O Amazon CloudWatch orquestraria os logs das interações executas. O Cost Explorer manteria a visibilidade planejamento para custo da solução. Amazon KMS segurança e criptografica para upload e leitura de arquivos
```

---

# 🧩 Arquitetura Final da Solução

Agora reúna tudo em uma visão única.

## 1. Visão geral

Explique em poucas linhas a ideia central da sua arquitetura.

**Sua resposta:**

```md
A arquitetura proposta transforma acervos corporativos brutos e despadronizados em uma Wiki Inteligente pesquisável e auditável, baseada em serviços Serverless da AWS e IA Generativa (RAG):

1. **Ingestão Segura e Imutabilidade (Amazon S3 + AWS KMS)**:
   - Os arquivos brutos (imagens, PDFs e tabelas CSV) são armazenados em um bucket dedicado (`dio_project_wiki_raw_data`) protegido por criptografia em repouso com **AWS KMS** e políticas de imutabilidade (**S3 Object Lock / Versioning**), garantindo a preservação jurídica dos documentos originais.

2. **Orquestração e Normalização Serverless (AWS Lambda + Amazon Textract)**:
   - Um pipeline unificado (`file_to_lambda`) executa a triagem inteligente por tipo de arquivo:
     - *Imagens e digitalizações* passam pelo **Amazon Textract** para OCR de alta precisão;
     - *PDFs nativos* são extraídos via camadas leves em Python (PyPDF), reduzindo custos desnecessários de OCR;
     - *Tabelas CSV do CRM* são convertidas dinamicamente em blocos semânticos.
   - Todos os arquivos são normalizados para **Markdown (`.md`)** e salvos no bucket de dados processados (`dio_project_wiki_raw_processed`).

3. **Enriquecimento Cognitivo com Agentes e Skills (Amazon Bedrock + Strands)**:
   - Um agente de IA orquestrado pelo framework **Strands** executa habilidades declarativas (`.skills/meta_data_governace.md`) para extrair metadados estruturados (datas, participantes, decisões tomadas, responsáveis e pendências), gravando arquivos de metadados companheiros (`.metadata.json`) no S3.

4. **Oráculo RAG e Citação de Fontes (Bedrock Knowledge Bases / OpenSearch)**:
   - As consultas dos usuários são atendidas por um oráculo cognitivo (`user_ask.py` + `.skills/wiki_oracle.md`) que recupera os trechos contextuais dos documentos e gera respostas fundamentadas com diretrizes estritas de *grounding* (sem alucinações), acompanhadas de citações formais das fontes de origem e páginas no S3.

5. **Observabilidade e Auditoria Contínua (Amazon CloudWatch + S3 Logs)**:
   - Todo o ciclo de vida da esteira gera logs estruturados em JSON no padrão **Amazon CloudWatch**, associando cada execução e arquivo a identificadores de rastreabilidade (`batch_id` e `trace_id`), com persistência direta da memória para um bucket de logs de auditoria (`dio_project_wiki_logs`).
```

---

## 2. Serviços AWS utilizados

| Serviço AWS | Papel na solução |
|---|---|
| Amazon S3 | Amazenamento, imutabilidade dos arquivos e logs de auditoria |
| Amazon Textract | Leitura e OCR de arquivos digitalizados (scans), imagens e PDFs rasterizados |
| Amazon Bedrock | Enriquecimento dos dados, sumarização e processamento em linguagem natural via LLMs |
| Amazon Bedrock Knowledge Bases | Vetorização contínua (Embeddings), gerenciamento de chunks e recuperação semântica (RAG) |
| AWS Lambda | Execução serverless da triagem de arquivos (`file_to_lambda`), normalização para Markdown e parsers |
| AWS Step Functions | Orquestração do pipeline assíncrono de ingestão em lote, retries e governança |
| Amazon CloudWatch | Observabilidade e centralização de logs estruturados em JSON com rastreabilidade |
| AWS IAM | Controle de acesso granular com privilégio mínimo para execução de serviços e usuários |
| AWS KMS | Criptografia gerenciada em repouso para buckets S3 com chaves dedicadas por classificação |

Adicione, remova ou ajuste os serviços conforme sua proposta.

---

## 3. Fluxo de dados de ponta a ponta

Descreva o caminho dos dados desde a pasta `raw/` até a Wiki Inteligente.

```md
Exemplo de estrutura:

1. Arquivos estão inicialmente na pasta raw/
2. Arquivos são enviados para o Amazon S3
3. Documentos escaneados passam pelo Amazon Textract
4. Arquivos digitais têm seus textos extraídos
5. Textos são limpos e padronizados
6. Metadados são extraídos
7. Conteúdos são indexados em uma base pesquisável
8. Usuário pesquisa na Wiki
9. IA responde com base nos documentos originais
```

**Sua resposta:**

```md
1. **Ingestão no Repositório Bruto:** Os arquivos corporativos heterogêneos (`.pdf`, `.png`, `.csv`) presentes na pasta local `raw/` são validados e enviados para o bucket seguro `dio_project_wiki_raw_data/raw/` com criptografia gerenciada via AWS KMS e bloqueio de imutabilidade (S3 Object Lock).
2. **Disparo da Orquestração Serverless:** O upload gera um evento no S3 que aciona a esteira serverless (AWS Lambda / Step Functions) inicializando o contexto de execução com identificadores únicos de rastreio (`batch_id` e `trace_id`).
3. **Triagem Inteligente de Formatos:** O módulo `file_to_lambda` inspeciona a extensão e a estrutura interna de cada arquivo:
   - Imagens e digitalizações (`.png`, `.jpg` ou PDFs escaneados) são encaminhadas para o **Amazon Textract** para OCR de alta acurácia;
   - PDFs com camada digital nativa têm o texto extraído diretamente via parser leve em Python (PyPDF), economizando custos de OCR;
   - Tabelas estruturadas de vendas (`.csv`) são convertidas em blocos semânticos rotulados com métricas e contexto textual legível.
4. **Normalização e Padronização:** O conteúdo extraído de todas as fontes é formatado em **Markdown (`.md`)** padronizado, higienizado contra ruídos de formatação e salvo no bucket `dio_project_wiki_raw_processed/processed/`.
5. **Enriquecimento Cognitivo de Metadados:** Um agente de IA (Strands Agent + Amazon Bedrock) executa a habilidade declarativa (`.skills/meta_data_governace.md`), extraindo entidades críticas (datas, participantes, decisões tomadas, responsáveis e pendências), gravando um arquivo de metadados companheiro (`.metadata.json`) no S3.
6. **Vetorização e Indexação Semântica:** Os documentos em Markdown são fragmentados em blocos lógicos com sobreposição semântica (*chunking*) e convertidos em vetores via modelo **Amazon Titan Text Embeddings V2**, sendo indexados no **Amazon Bedrock Knowledge Bases / OpenSearch Serverless**.
7. **Consulta e Entrada do Usuário:** O usuário final submete uma pergunta em linguagem natural através do assistente corporativo (`user_ask.py` / Interface Web).
8. **Recuperação Híbrida de Contexto:** A consulta é vetorizada e submetida a uma busca híbrida (k-NN semântica + BM25 léxico com filtros de metadados), recuperando os fragmentos documentais mais relevantes diretamente do S3 processado.
9. **Geração Fundamentada e Auditoria:** O oráculo de IA (`.skills/wiki_oracle.md`) sintetiza a resposta final estritamente baseada no contexto recuperado (*grounding* anti-alucinação), citando formalmente o documento de origem e gravando todo o rastro de auditoria nos logs do CloudWatch e no bucket `dio_project_wiki_logs`.
```

---

## 4. Diagrama textual da arquitetura

Crie um diagrama simples usando texto.

```md
Exemplo:

raw/ → Amazon S3 → Lambda/Step Functions → Textract → S3 Processado → Bedrock Knowledge Bases → Interface de Consulta → Usuário Final
```

**Sua resposta:**

```md
[ raw/ Arquivos Locais ] (.pdf, .png, .csv)
         │
         ▼  (Upload Seguro com Criptografia KMS + S3 Object Lock)
[ Amazon S3: dio_project_wiki_raw_data ]
         │
         ▼  (S3 Event Trigger)
[ AWS Lambda / Step Functions ] ──(Triagem Inteligente de Tipo)──┐
         │                                                        │
         ├── [.png / Scan PDF] ──► [ Amazon Textract (OCR) ]     │
         ├── [.pdf Digital]    ──► [ PyPDF Parser Direto ]       │
         └── [.csv CRM Tabular]──► [ Parser Semântico Tabular ]  │
                                                                  │
         ┌────────────────────────────────────────────────────────┘
         ▼
[ Amazon S3: dio_project_wiki_raw_processed ] (.md Padronizado)
         │
         ▼
[ Strands Agent + Amazon Bedrock ] ◄── Carrega [.skills/meta_data_governace.md]
         │
         ├──► Gera [.metadata.json no S3] (Datas, Participantes, Decisões, Pendências)
         └──► [ Amazon Bedrock Knowledge Bases / OpenSearch Serverless ]
                     │  (Vetorização: Titan Text Embeddings V2)
                     ▼
         ┌────────────────────────────────────────────────────────┐
         │              ÍNDICE SEMÂNTICO PESQUISÁVEL              │
         └────────────────────────────────────────────────────────┘
                     ▲
                     │ (Busca Híbrida Semântica k-NN + BM25)
                     │
[ Usuário Final / Web App (AWS Amplify + Cognito) ]
         │
         ▼ (Consulta em Linguagem Natural)
[ Oráculo RAG (user_ask.py) ] ◄── Carrega [.skills/wiki_oracle.md]
         │
         ▼ (Síntese Fundamentada com Citação de Fontes)
[ Resposta Final Confiável ] ──► Exibição ao Usuário
         │
         ▼ (Auditoria Contínua)
[ Amazon CloudWatch ] ──► [ S3: dio_project_wiki_logs ] (Rastreabilidade batch_id & trace_id)
```

---

## 5. Riscos e limitações

Liste possíveis desafios da sua solução.

```md
Exemplo:
- Documentos ilegíveis podem prejudicar a extração de texto.
- OCR pode gerar erros em documentos com baixa qualidade.
- Custos podem aumentar conforme o volume de documentos.
- Metadados inferidos por IA podem precisar de validação humana.
- Respostas geradas por IA devem sempre referenciar documentos de origem.
```

**Sua resposta:**

```md
1. **Qualidade e Degradação de Documentos Físicos (OCR):**
   - *Risco:* Imagens escaneadas com baixa resolução, sombras, manchas ou caligrafia manual ilegível podem resultar em transcrições incompletas ou com caracteres corrompidos pelo Textract.
   - *Mitigação:* Implementar validação do score de confiança retornado pela API do Textract; documentos com score abaixo de 80% são sinalizados para fila de revisão humana (Human-in-the-Loop via Amazon A2I).

2. **Alucinação e Respostas Incorretas de Modelos Generativos:**
   - *Risco:* O modelo de linguagem pode inventar dados financeiros, datas ou atribuições de responsabilidade que não constavam nas atas originais.
   - *Mitigação:* Regras de *grounding* estritas implementadas na skill `wiki_oracle.md` proibindo suposições, exigindo citação explícita do documento de origem e emitindo uma recusa padronizada caso a informação não exista no contexto recuperado.

3. **Escalabilidade de Custos Operacionais (FinOps):**
   - *Risco:* Processamento indiscriminado de grandes volumes de documentos via Textract e chamadas excessivas a modelos fundacionais podem elevar os custos na AWS.
   - *Mitigação:* Roteamento inteligente na triagem (utilizando PyPDF antes do Textract para PDFs com texto nativo), uso de modelos otimizados para extração (Claude 3 Haiku / Titan), dimensionamento de chunks para reduzir consumo de tokens e alarmes no AWS Budgets.

4. **Vazamento de Informações Sensíveis e Privacidade (LGPD):**
   - *Risco:* Ingestão de arquivos contendo dados pessoais identificáveis (PII) ou números de documentos de funcionários sem isolamento adequado.
   - *Mitigação:* Verificação automatizada via Amazon Macie para detecção e mascaramento de PII antes da indexação, criptografia KMS por chave dedicada e controle de acesso baseado em funções (RBAC) via AWS IAM e Cognito.

5. **Dessincronização de Índices e Metadados:**
   - *Risco:* Alteração ou exclusão de documentos no bucket S3 que continuem sendo recuperados pelo índice vetorial desatualizado.
   - *Mitigação:* Ingestão orientada a eventos com S3 Event Notifications sincronizando o catálogo do Knowledge Bases/OpenSearch e imutabilidade de versões via S3 Object Lock.
```

---

## 6. Melhorias futuras

Descreva como a solução poderia evoluir.

```md
Exemplo:
- Criar uma interface web para consulta.
- Criar um chat interno para perguntas sobre atas.
- Adicionar controle de acesso por departamento.
- Criar dashboard de decisões e pendências.
- Gerar alertas automáticos sobre ações em aberto.
- Integrar com ferramentas corporativas.
```

**Sua resposta:**

```md
1. **Interface Web Corporativa Completa (AWS Amplify + Amazon Cognito):**
   - Desenvolvimento de um portal web responsivo e amigável em React/Next.js integrado ao Amazon Cognito, oferecendo login com autenticação multifator (MFA), visualizador de documentos com realce dos trechos citados e controle de acesso por departamento (RBAC).

2. **Integração com Ferramentas Colaborativas (Chatbots em Slack e Microsoft Teams):**
   - Criação de um bot corporativo conectado à API do Oráculo RAG via Amazon API Gateway e AWS Lambda, permitindo que gestores façam perguntas diretas nos canais de comunicação da empresa ("@WikiBot quem ficou responsável pela meta de vendas da filial Sul?").

3. **Dashboard Executivo de Acompanhamento de Decisões e Pendências:**
   - Construção de painéis analíticos no Amazon QuickSight ou frontend dedicado alimentado pelos metadados estruturados (`.metadata.json`), exibindo gráficos de decisões pendentes, matriz de responsabilidades e cumprimento de prazos definidos em atas.

4. **Sistema Automatizado de Notificações e Alertas de Ação:**
   - Integração com Amazon EventBridge e Amazon SNS para disparar lembretes automáticos por e-mail ou mensagem direta para os responsáveis citados nas atas quando uma ação estiver próxima da data limite de entrega.

5. **Fluxo Human-in-the-Loop (Amazon Augmented AI - A2I):**
   - Estabelecer uma interface de aprovação para curadores de conhecimento revisarem documentos complexos ou com OCR duvidoso antes de disponibilizá-los na base de conhecimento oficial.
```

---

# 🧠 Checklist Final

Antes de entregar, confirme se sua solução responde:

- [✅] Como transformar documentos escaneados em texto?
- [✅] Como lidar com diferentes formatos dentro da mesma pasta `raw/`?
- [✅] Como armazenar os documentos originais?
- [✅] Como preservar a rastreabilidade entre resposta e documento fonte?
- [✅] Como organizar metadados?
- [✅] Como criar busca semântica?
- [✅] Como usar Amazon Bedrock na solução?
- [✅] Como proteger documentos sensíveis?
- [✅] Como monitorar falhas?
- [✅] Como a empresa usaria essa Wiki no dia a dia?

---

# 🏁 Conclusão

Escreva uma breve conclusão defendendo sua solução como se estivesse apresentando para uma liderança técnica ou de negócio.

**Sua resposta:**

```md
A solução desenvolvida para a **Wiki Inteligente Corporativa** resolve de forma definitiva o problema histórico de "arquivos mortos" e silos de informação desestruturados na organização. Ao unir uma arquitetura **100% Serverless** na nuvem AWS com as capacidades mais avançadas de **IA Generativa e RAG (Retrieval-Augmented Generation)**, entregamos uma plataforma que é simultaneamente ágil, econômica, segura e altamente precisa.

Sob a perspectiva de **Engenharia e Governança Técnica**, a arquitetura se destaca pela resiliência e rigor:
- **Segurança e Conformidade:** Garantimos a proteção total dos dados corporativos com criptografia de ponta a ponta (AWS KMS), imutabilidade documental para respaldo jurídico (S3 Object Lock) e auditoria transparente de cada interação com identificadores universais (`batch_id` e `trace_id`) no CloudWatch e S3.
- **Eficiência Operacional e FinOps:** O pipeline híbrido de triagem inteligente evita desperdício de recursos, utilizando OCR especializado (Amazon Textract) apenas quando indispensável e priorizando parsers nativos de alta performance para arquivos digitais e tabulares.
- **Confiabilidade Anti-Alucinação:** O oráculo de conhecimento ancorado no Amazon Bedrock e no framework Strands opera sob diretrizes estritas de *grounding*, assegurando que nenhuma resposta seja inventada e que toda afirmação venha acompanhada da respectiva citação de documento e página de origem.

Sob a perspectiva de **Negócio e Valor Estratégico**, a Wiki Corporativa transforma arquivos estáticos e atas esquecidas em um ativo vivo de tomada de decisão. A liderança e as equipes de vendas, operações e governança ganham a capacidade de consultar instantaneamente deliberações passadas, mapear pendências, identificar responsáveis e consultar históricos em segundos através de linguagem natural.

Esta arquitetura não apenas atende integralmente a todos os requisitos do desafio técnico com nível de excelência, como estabelece a base fundacional para a transformação digital e a cultura orientada a dados e IA na companhia.
```

