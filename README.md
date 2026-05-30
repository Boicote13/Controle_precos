# Controle de Preços

Este aplicativo tem como objetivo criar um banco de dados com notas fiscais de compras (mais especificamente mercados) com o qual onde o usuário poderá explorar informações de gastos mais detalhadamente.

### Cadastro de notas

A aplicação permite cadastrar notas fiscais de duas formas:
 1. Manualmente. Cada item com sua quantidade, valor unitário e unidade deve ser preenchido em um formulário disponível na aba Notas.
 2. Através do arquivo html da nota fiscal obtido no site da Fazenda (https://sped.fazenda.pr.gov.br/NFCe/webservices/sped/nfce/completa). Notas Fiscais Eletrônicas podem ser acessadas através da Chave de Acesso no site indicado, ou através do QRCode na nota. Com a chave de acesso o usuário pode acessar a nota através do navegador pelo computador e baixar o conteúdo completo da página. Este arquivo pode ser passado como input na aplicação.


 ### Exploração de dados

 Para explorar os dados inseridos no banco o usuário pode acessar a parte da aplicação voltada para geração de gráficos interativos com os dados. 

 
> - Se der certo a ideia é fazer outra IA pra subcategorias de alimento (parte nutricional: carboidratos, proteínas, lipidios, fibras)


# Recuperação de banco

Para recuperar o banco de um backup, primeiro vc precisa ter um backup:

```
python3 manage.py dumpdata --indent 2 > backups/backup_$(date +%Y%m%d).json
```

A partir do backup vc pode reconstruir o banco

```
rm db.sqlite3

#Cria o banco zerado
python3 manage.py migrate

#Insere tudo, CASO não tenha mudanças significativas nos Models
python3 manage.py loaddata backups/backup_20260114.json
```

A sugestão é que em cada mudança siginificativa de algum Model seja feito um backup pois pode haver conflito na hora de recuperar backups de bancos com estruturas diferentes.

---

# Setup para desenvolvimento

## Pré-requisitos

- Python 3.10+
- PostgreSQL (opcional, apenas se for usar este banco)

## Instalação

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd controle_precos/backend

# Crie e ative um virtualenv
python3 -m venv venv
source venv/bin/activate

# Instale as dependências
pip install -r requirements.txt

# Configure o ambiente
cp .env.example .env
# Edite .env conforme necessário
```

## Configuração do banco de dados

### Modo padrão (SQLite)

Com `DEBUG=true` e sem configurar PostgreSQL, a aplicação usa SQLite automaticamente:

```bash
python manage.py migrate
python manage.py runserver
```

### Modo debug com PostgreSQL

Defina as variáveis no `.env`:

```env
DEBUG=true
DB_ENGINE=django.db.backends.postgresql
DB_NAME=mydb
DB_USER=postgres
DB_PASSWORD=minha_senha
DB_HOST=localhost
DB_PORT=5432
POSTGRES_PASSWORD=minha_senha
USE_POSTGRES=true
```

Ou via variáveis de ambiente (sobrescreve o `.env`):

```bash
DB_ENGINE=django.db.backends.postgresql DB_NAME=mydb DB_USER=postgres \
DB_PASSWORD=minha_senha DB_HOST=localhost DB_PORT=5432 \
USE_POSTGRES=true python manage.py runserver
```

### Modo produção (DEBUG=false, sempre PostgreSQL)

```env
DEBUG=false
DB_ENGINE=django.db.backends.postgresql
DB_NAME=mydb
DB_USER=postgres
DB_PASSWORD=minha_senha
DB_HOST=localhost
DB_PORT=5432
POSTGRES_PASSWORD=minha_senha
```

> Com `DEBUG=false` o PostgreSQL é obrigatório — a aplicação não usa SQLite em produção.

## Lógica de seleção do banco

A aplicação usa dois sistemas de banco diferentes:

### Django ORM (admin, listas, formulários)

```python
# settings.py
DATABASES = {
    "default": {
        "ENGINE": os.environ.get("DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.environ.get("DB_NAME", str(BASE_DIR / "db.sqlite3")),
        ...
    }
}
```

| `DB_ENGINE` configurado? | Banco usado |
|--------------------------|-------------|
| Não | SQLite (`backend/db.sqlite3`) |
| Sim (ex: `postgresql`) | PostgreSQL |

### Peewee (DatabaseOperations — upload de arquivo HTML)

A classe `DatabaseOperations` em `notas_fiscais/scripts/arquivoPdatabase.py` segue esta ordem de decisão:

1. Se `use_postgres` passado explicitamente → usa esse valor
2. Se `USE_POSTGRES=true` no ambiente → PostgreSQL
3. Se `DEBUG=false` → PostgreSQL
4. Senão → SQLite

### Streamlit (precos_visual)

O módulo `precos_visual/visual.py` conecta diretamente no PostgreSQL lendo as credenciais do `.env` do backend.

```bash
cd precos_visual
pip install -r requirements.txt
streamlit run visual.py
```

## Migrações

```bash
python manage.py makemigrations   # criar migrações se houver mudanças nos models
python manage.py migrate          # aplicar migrações
```

## Servidor de desenvolvimento

```bash
python manage.py runserver
# Acessar: http://127.0.0.1:8000
```

## Backup e restauração

```bash
# Backup
python manage.py dumpdata --indent 2 > backups/backup_$(date +%Y%m%d).json

# Restauração (banco SQLite)
rm db.sqlite3
python manage.py migrate
python manage.py loaddata backups/backup_20260114.json
```

---

## Estrutura do projeto

```
controle_precos/
├── backend/                  # Django (backend principal)
│   ├── controle_precos/      # Configurações do Django
│   ├── notas_fiscais/        # App principal
│   │   ├── management/       # Comandos personalizados
│   │   ├── scripts/          # Processamento de notas (PDF/HTML → BD)
│   │   └── templates/        # Templates HTML
│   ├── .env                  # Config local (não versionado)
│   ├── .env.example          # Template de configuração
│   └── requirements.txt
├── precos_visual/            # Streamlit (visualização de dados)
│   ├── visual.py
│   ├── .streamlit/config.toml
│   └── requirements.txt
└── README.md
```