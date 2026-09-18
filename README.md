# 📋Monitor de Assinatura

Painel interativo para acompanhamento de atendimentos médicos e status de assinatura eletrônica, construído com **Python** e **Streamlit**, com dados consultados diretamente de um banco **PostgreSQL**.

## 🎯 Sobre o projeto

Este painel foi criado para acompanhar se os **médicos/prestadores estão assinando digitalmente** os documentos dos atendimentos que realizam. Ele serve como ferramenta de apoio a um fluxo de ação:

1. O painel aponta quais atendimentos estão **sem assinatura**
2. Para cada prestador com pendências, verifica-se se ele **já possui assinatura eletrônica** cadastrada:
   - ✅ **Possui assinatura eletrônica** → o prestador é **cobrado** para assinar os documentos pendentes
   - ❌ **Não possui assinatura eletrônica** → o prestador é **convocado** para criar sua assinatura eletrônica antes de poder regularizar as pendências

Além disso, o painel também permite:

- Ver quantos atendimentos estão **assinados** ou **pendentes de assinatura**
- Ver quais **prestadores** têm mais pendências (para priorizar a cobrança)
- Ver a distribuição dos atendimentos por **centro de custo**
- Acompanhar a evolução dos atendimentos ao longo dos dias

## ✨ Funcionalidades

- 🔍 Filtro por **período** (data inicial e final, escolhido livremente pelo usuário)
- 🔍 Filtro por **prestador**
- 🔍 Filtro por **centro de custo**
- 🔍 Filtro por **status de assinatura**
- 📊 KPIs no topo: total de atendimentos, assinados e pendentes
- 📈 Gráfico de barras: atendimentos por dia
- 🥧 Gráfico de pizza: proporção de assinaturas
- 🏆 Ranking de pendências por prestador (para priorizar quem cobrar)
- 📄 Tabela detalhada com todos os atendimentos filtrados, incluindo se o prestador **possui assinatura eletrônica** — informação chave para decidir entre cobrar a assinatura ou convocar o prestador para criá-la
- 🔄 Botão para atualizar os dados manualmente (força nova consulta ao banco)

## 🛠️ Tecnologias utilizadas

- [Python](https://www.python.org/)
- [Streamlit](https://streamlit.io/) — interface web do painel
- [Pandas](https://pandas.pydata.org/) — manipulação dos dados
- [SQLAlchemy](https://www.sqlalchemy.org/) — conexão com o banco de dados
- [Plotly Express](https://plotly.com/python/plotly-express/) — gráficos interativos
- [PostgreSQL](https://www.postgresql.org/) — banco de dados

## 📦 Estrutura do banco de dados

O painel consulta as seguintes tabelas:

| Tabela | Descrição |
|---|---|
| `evomed` | Registros de atendimentos/evoluções |
| `cadope` | Cadastro de operadores |
| `cadprest` | Cadastro de prestadores |
| `arqatend` | Vínculo entre atendimento e centro de custo |
| `cadcc` | Cadastro de centros de custo |

## 🚀 Como rodar localmente

### 1. Clone o repositório

```bash
git clone https://github.com/PedroHGardim/painel-de-prescricoes.git
cd painel-de-prescricoes
```

### 2. Crie um ambiente virtual (recomendado)

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as credenciais do banco

Copie o arquivo de exemplo e preencha com suas credenciais reais:

```bash
mkdir .streamlit
copy secrets.toml.example .streamlit\secrets.toml     # Windows
cp secrets.toml.example .streamlit/secrets.toml        # Linux/Mac
```

Edite `.streamlit/secrets.toml` com os dados do seu banco:

```toml
[database]
host = "seu_host"
port = 5432
dbname = "seu_banco"
user = "seu_usuario"
password = "sua_senha"
```

> ⚠️ **Nunca** suba esse arquivo para o GitHub — ele já está protegido pelo `.gitignore`.

### 5. Execute o painel

```bash
streamlit run app.py
```

O painel abrirá automaticamente no navegador, geralmente em `http://localhost:8501`.

## 📁 Estrutura do projeto

```
painel-de-prescricoes/
├── app.py                    # Código principal do painel
├── requirements.txt          # Dependências do projeto
├── secrets.toml.example      # Modelo de configuração (sem dados reais)
├── .gitignore                # Arquivos ignorados pelo Git
└── .streamlit/
    └── secrets.toml          # Credenciais reais (não versionado)
```

## 📌 Observações

- A query filtra atendimentos por `datagrav`, com o período totalmente ajustável pela barra lateral
- O status de assinatura considera `'S'` como assinado e qualquer outro valor (`'N'` ou `NULL`) como pendente
- A presença de assinatura eletrônica do prestador segue a mesma lógica: `'S'` para sim, `'N'`/`NULL` para não

### Fluxo de decisão para atendimentos pendentes

Ao identificar um atendimento **não assinado** na tabela ou no ranking, o próximo passo é checar a coluna **"Possui assinatura eletrônica"** daquele prestador:

| Possui assinatura eletrônica? | Ação recomendada |
|---|---|
| Sim | Cobrar o prestador para assinar os documentos pendentes |
| Não | Convocar o prestador para criar sua assinatura eletrônica |

## 📝 Licença

Este projeto é de uso pessoal/interno. Ajuste conforme a necessidade da sua organização.

---

Desenvolvido por [Pedro Gardim](https://github.com/PedroHGardim)
