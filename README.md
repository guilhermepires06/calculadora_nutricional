Planejamento Nutricional com Flask e SQLite

Aplicação web para criação, personalização e gerenciamento de planos alimentares semanais, desenvolvida com Python, Flask, SQLite, HTML, CSS e JavaScript.

O sistema permite gerar planos com base em peso, quantidade de refeições, rotina e preferências alimentares. Os dados são persistidos em banco SQLite, permitindo que os planos continuem disponíveis mesmo após fechar o navegador ou reiniciar o servidor.

Funcionalidades
Geração automática de planejamento alimentar semanal
Cálculo estimado de calorias, proteínas e consumo de água
Seleção de proteínas, carboidratos, frutas, verduras e legumes
Substituição individual de alimentos
Substituição completa de refeições
Cadastro e salvamento de planos
Edição de planos existentes
Duplicação e exclusão de planos
Pesquisa de planos cadastrados
Personalização de marca, cores e logotipo
Impressão do planejamento em formato A4
Interface responsiva para desktop e dispositivos móveis
Persistência de dados utilizando SQLite
Tecnologias utilizadas
Python
Flask
SQLite
HTML5
CSS3
JavaScript
Jinja2
Arquitetura

A aplicação utiliza Flask como servidor web e responsável pelo processamento das rotas, regras de negócio e comunicação com o banco de dados.

O SQLite é utilizado como banco relacional local, armazenando:

Planos alimentares
Preferências dos usuários
Configurações do sistema
Informações de identidade visual
Logotipo personalizado

O front-end é desenvolvido com HTML, CSS e JavaScript, sendo responsável pela interface, cálculos dinâmicos, seleção de alimentos e interação com as refeições.

Estrutura do banco de dados
plans

Armazena os planejamentos alimentares cadastrados, incluindo nome, usuário, metas nutricionais, refeições e datas de criação e atualização.

preferences

Armazena dados como peso, rotina, número de refeições, alimentos selecionados e restrições alimentares.

settings

Armazena nome da aplicação, responsável, tema visual, texto de rodapé e logotipo.

Persistência

Os dados são armazenados no arquivo:

database.sqlite3

Para realizar um backup completo, basta copiar esse arquivo enquanto a aplicação estiver desligada.

Execução local

Clone o repositório:

git clone URL_DO_REPOSITORIO
cd NOME_DO_REPOSITORIO

Crie um ambiente virtual:

python -m venv venv

Ative o ambiente virtual no Windows:

venv\Scripts\activate

Instale as dependências:

pip install -r requirements.txt

Execute a aplicação:

python app.py

Acesse no navegador:

http://127.0.0.1:5000
Objetivo técnico

O projeto foi desenvolvido para aplicar conceitos de:

Desenvolvimento web full stack
Operações CRUD
Persistência de dados com SQLite
Integração entre front-end e back-end
Manipulação de dados em JavaScript
Organização de rotas e regras de negócio com Flask
Interface responsiva
Geração de documentos para impressão
Personalização dinâmica da aplicação
Aviso

Os valores nutricionais gerados são estimativas automáticas e não substituem avaliação ou acompanhamento realizado por nutricionista ou profissional de saúde.
