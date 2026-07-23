<div align="center">

Planejamento Nutricional

Aplicação web para criação, personalização e gerenciamento de planos alimentares semanais



</div>

Sobre o projeto

O Planejamento Nutricional é uma aplicação web full stack desenvolvida para gerar e administrar planejamentos alimentares semanais.

O sistema calcula metas estimadas a partir do peso informado, permite selecionar preferências alimentares, montar refeições, substituir itens individualmente e salvar os planos em um banco de dados SQLite.

A aplicação também permite personalizar o nome da marca, o responsável, o tema, o logotipo e as informações exibidas no documento de impressão.

Aviso: os valores gerados são estimativas automáticas e não substituem avaliação ou acompanhamento realizado por nutricionista ou profissional de saúde.

Principais recursos

Cálculo estimado de calorias, proteína e consumo de água

Planejamento semanal com 3 a 6 refeições por dia

Seleção de proteínas, carboidratos, frutas, verduras e legumes

Pesquisa e filtros rápidos de alimentos

Troca individual de alimentos dentro de cada refeição

Substituição completa de uma refeição

Salvamento persistente em SQLite

Edição, duplicação e exclusão de planos

Pesquisa de planos cadastrados

Personalização de nome, tema, responsável e logotipo

Impressão em formato A4

Exportação de backup em JSON

Interface responsiva para desktop e dispositivos móveis

Tecnologias

Camada

Tecnologia

Back-end

Python e Flask

Banco de dados

SQLite

Front-end

HTML5, CSS3 e JavaScript

Templates

Jinja2

Comunicação

API REST com JSON

Persistência

SQLite com modo WAL

Arquitetura

┌──────────────────────────────┐
│         Navegador            │
│ HTML + CSS + JavaScript      │
└──────────────┬───────────────┘
               │ HTTP / JSON
┌──────────────▼───────────────┐
│          Flask               │
│ Rotas, validações e API REST │
└──────────────┬───────────────┘
               │ SQL
┌──────────────▼───────────────┐
│          SQLite              │
│ Planos, preferências e tema  │
└──────────────────────────────┘

Estrutura do projeto

planejamento_nutricional_sqlite/
├── app.py                 # Aplicação Flask e endpoints da API
├── database.sqlite3       # Banco de dados local
├── requirements.txt       # Dependências Python
├── INICIAR.bat            # Inicialização no Windows
├── iniciar.sh             # Inicialização no Linux/macOS
├── README.md              # Documentação do projeto
└── templates/
    └── index.html         # Interface completa da aplicação

Banco de dados

O banco é criado automaticamente no arquivo:

database.sqlite3

Tabela plans

Campo

Tipo

Descrição

id

TEXT

UUID do plano

title

TEXT

Nome do planejamento

client_name

TEXT

Nome da pessoa

preferences_json

TEXT

Preferências serializadas em JSON

targets_json

TEXT

Metas nutricionais em JSON

plan_json

TEXT

Estrutura semanal em JSON

created_at

TEXT

Data de criação em UTC

updated_at

TEXT

Data da última atualização em UTC

Tabela settings

Registro único com as configurações visuais:

Nome da marca

Subtítulo

Responsável

Texto do rodapé

Logotipo em formato Data URL

Tema selecionado

Tabela preferences

Registro único utilizado para manter as últimas preferências preenchidas no formulário.

API REST

Método

Endpoint

Descrição

GET

/api/health

Verifica o funcionamento da aplicação

GET

/api/plans

Lista os planos

POST

/api/plans

Cadastra um plano

GET

/api/plans/<id>

Retorna um plano completo

PUT

/api/plans/<id>

Atualiza um plano

DELETE

/api/plans/<id>

Exclui um plano

POST

/api/plans/<id>/duplicate

Duplica um plano

GET

/api/settings

Retorna as configurações

PUT

/api/settings

Atualiza as configurações

DELETE

/api/settings

Restaura as configurações padrão

GET

/api/preferences

Retorna as preferências

PUT

/api/preferences

Salva as preferências

DELETE

/api/preferences

Limpa as preferências

GET

/api/export

Exporta todos os dados em JSON

Teste de disponibilidade

curl http://127.0.0.1:5000/api/health

Resposta esperada:

{
  "database": "database.sqlite3",
  "status": "ok"
}

Instalação

Requisitos

Python 3.10 ou superior recomendado

pip disponível no terminal

Navegador moderno

Windows

Extraia o projeto e execute:

INICIAR.bat

O script verifica o Python, instala as dependências, inicia o Flask e abre o sistema no navegador.

Instalação manual

Clone o repositório:

git clone URL_DO_REPOSITORIO
cd planejamento_nutricional_sqlite

Crie um ambiente virtual:

python -m venv .venv

Ative no Windows:

.venv\Scripts\activate

Ative no Linux ou macOS:

source .venv/bin/activate

Instale as dependências:

python -m pip install -r requirements.txt

Execute:

python app.py

Acesse:

http://127.0.0.1:5000

Linux ou macOS

chmod +x iniciar.sh
./iniciar.sh

Backup

Backup completo

Pare a aplicação e copie:

database.sqlite3

Como o SQLite está configurado para usar o modo WAL, durante a execução também podem existir:

database.sqlite3-wal
database.sqlite3-shm

Para um backup manual consistente, encerre o servidor antes de copiar o banco.

Exportação em JSON

GET /api/export

O arquivo exportado inclui planos, preferências e configurações.

Configuração do servidor

A aplicação inicia por padrão em:

host="127.0.0.1"
port=5000
debug=False

Isso limita o acesso ao próprio computador.

Para publicação em produção, recomenda-se adicionar:

Servidor WSGI

Proxy reverso com HTTPS

Autenticação de usuários

Proteção CSRF

Controle de acesso por perfil

Variáveis de ambiente

Backups automatizados

Limitações atuais

Não possui login ou controle de usuários

Foi projetado inicialmente para execução local

Não possui migrações de banco

O logotipo é armazenado diretamente no SQLite

Os cálculos nutricionais são estimativas simplificadas

Não substitui prescrição profissional

Melhorias planejadas

Autenticação e perfis de acesso

Cadastro completo de pacientes

Histórico de medidas e evolução

Relatórios em PDF

Importação de backups

Cadastro personalizado de alimentos

Migrações de banco com Alembic

Testes automatizados

Docker

Suporte a PostgreSQL

Segurança e privacidade

Não publique arquivos de banco contendo informações pessoais.

Adicione ao .gitignore:

.venv/
__pycache__/
*.pyc
database.sqlite3
database.sqlite3-wal
database.sqlite3-shm
.env

Contribuição

git checkout -b feature/nova-funcionalidade
git commit -m "feat: adiciona nova funcionalidade"
git push origin feature/nova-funcionalidade

Ao contribuir:

Valide os dados recebidos pela API

Não envie bancos reais ao repositório

Mantenha a documentação atualizada

Utilize mensagens de commit claras

Autor

Desenvolvido por Guilherme Pires.

<div align="center">

Projeto criado para estudo e aplicação prática de desenvolvimento web full stack, API REST e persistência de dados com SQLite.

</div>
