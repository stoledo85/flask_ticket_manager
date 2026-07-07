# Flask Ticket Manager 🎫

Um sistema de gerenciamento de chamados (helpdesk/suporte) moderno e elegante, construído com Python, Flask e SQLite. O sistema conta com controle de acesso baseado em perfis, gerenciamento de categorias e cidades por administradores, histórico de atualizações (worklogs) e um fluxo interativo de encerramento de chamados com avaliação de satisfação do cliente.

---

## 🚀 Funcionalidades

### 👥 Perfis de Usuários e Permissões
O sistema divide os usuários em três perfis com privilégios específicos:
* **Cliente**: 
  * Abre chamados.
  * Responde ao histórico/worklog dos seus próprios chamados.
  * Avalia e confirma se a solução resolveu o problema (fechando ou reabrindo o chamado).
* **Técnico**: 
  * Cria chamados.
  * Responde a chamados.
  * Atualiza o status e worklogs de qualquer chamado no sistema.
* **Administrador (Admin)**: 
  * Acesso total ao sistema.
  * Gerenciamento de usuários (criar, editar Cidade/Estado, alterar perfil e redefinir senhas).
  * Gerenciamento de **Categorias de Chamados**.
  * Gerenciamento de **Cidades** (para associar aos usuários).

### 🛠️ Funcionalidades de Negócio
* **Cadastro Público Restrito**: A tela de registro público cria automaticamente usuários com o perfil de *Cliente*. Perfis de *Técnico* ou *Admin* só podem ser criados a partir do painel de administração.
* **Redefinição de Perfil e Senha**: Usuários podem editar seus próprios dados e alterar sua senha de acesso a qualquer momento.
* **Filtros e Detalhes de Localidade (Cidade - UF)**: Administradores cadastram cidades e estados em uma lista centralizada, disponibilizada como um menu suspenso (dropdown) na criação e edição de usuários.
* **Fluxo de Satisfação do Cliente (Feedback)**:
  * Quando um técnico ou administrador altera o status de um chamado para **Resolvido**, um banner interativo é exibido na tela de detalhes do chamado para o cliente autor do ticket.
  * O cliente pode responder se a solução o atendeu (**Sim**) ou não (**Não**).
  * **Sim**: O chamado é atualizado para o status **Fechado** definitivamente.
  * **Não**: O chamado é automaticamente reaberto voltando para o status **Aberto**, gerando uma notificação no histórico de worklogs.

---

## 💻 Tecnologias Utilizadas

* **Backend**: Python 3, Flask, Flask-SQLAlchemy (ORM)
* **Banco de Dados**: SQLite
* **Frontend**: HTML5, Vanilla CSS3 (com um visual premium inspirado em Dark Glassmorphism, efeitos de transparência e transições suaves), JavaScript (para interações e máscaras de formulário)
* **Ícones**: FontAwesome 6

---

## ⚙️ Instalação e Execução

### Pré-requisitos
* Python 3 instalado
* Git

### Passos para Rodar Localmente

1. **Clonar o Repositório**:
   ```bash
   git clone https://github.com/stoledo85/flask_ticket_manager.git
   cd flask_ticket_manager
   ```

2. **Criar e Ativar Ambiente Virtual**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # No Windows: .venv\Scripts\activate
   ```

3. **Instalar Dependências**:
   ```bash
   pip install -r requirements.txt
   ```
   *(Nota: Se o arquivo `requirements.txt` não estiver presente, instale manualmente os pacotes principais: `pip install flask flask-sqlalchemy`)*

4. **Executar a Aplicação**:
   ```bash
   flask --app app run --debug
   ```

Acesse a aplicação no seu navegador em: [http://127.0.0.1:5000](http://127.0.0.1:5000).

---

## 🗃️ Estrutura do Banco de Dados

* **usuarios**: Armazena nome, e-mail, username, hash de senha criptografada e o relacionamento com a cidade.
* **perfis**: Controla o nível de acesso (Cliente, Técnico, Admin).
* **cidades**: Cadastro de cidades e UFs gerenciadas pelo administrador.
* **categorias**: Cadastro de categorias para classificação dos tickets.
* **chamados**: Registra os tickets com título, descrição, prioridade (Baixa, Média, Alta), status (Aberto, Em Andamento, Resolvido, Fechado) e categoria correspondente.
* **worklogs**: Linha do tempo contendo todas as mensagens, atualizações de status e respostas inseridas nos chamados.
