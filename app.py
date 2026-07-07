import os
from flask import Flask, session, redirect, url_for, flash
from functools import wraps
from models import db, Usuario
import controllers

app = Flask(__name__)

# Configurações básicas
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tickets.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-super-secret-key-12345')

# Inicialização do banco de dados
db.init_app(app)

# Cria as tabelas do banco se não existirem
with app.app_context():
    db.create_all()

# Decorator para exigir login nas rotas protegidas
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorator para exigir perfil admin nas rotas de usuários
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Você precisa fazer login para acessar esta página.', 'danger')
            return redirect(url_for('login'))
        usuario = Usuario.query.get(session['user_id'])
        if not usuario or usuario.tipo_perfil != 'Admin':
            flash('Acesso negado: esta página é restrita para administradores.', 'danger')
            return redirect(url_for('list_tickets'))
        return f(*args, **kwargs)
    return decorated_function

# Rota principal
@app.route('/')
def index():
    return controllers.index_controller()

# Rota de Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    return controllers.login_controller()

# Rota de Logout
@app.route('/logout')
def logout():
    return controllers.logout_controller()

# Rota de Cadastro de Usuário (Criação - "C" do CRUD)
@app.route('/register', methods=['GET', 'POST'])
def register():
    return controllers.register_controller()

# Rota de Listagem de Usuários (Leitura - "R" do CRUD)
@app.route('/users')
@admin_required
def list_users():
    return controllers.list_users_controller()

# Rota de Edição de Usuário (Atualização - "U" do CRUD)
@app.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    return controllers.edit_user_controller(user_id)

# Rota de Exclusão de Usuário (Remoção - "D" do CRUD)
@app.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    return controllers.delete_user_controller(user_id)

# Rota de Listagem de Chamados
@app.route('/tickets')
@login_required
def list_tickets():
    return controllers.list_tickets_controller()

# Rota de Pesquisa de Chamados
@app.route('/tickets/search')
@login_required
def search_tickets():
    return controllers.search_tickets_controller()


# Rota de Abertura de Chamado
@app.route('/tickets/new', methods=['GET', 'POST'])
@login_required
def create_ticket():
    return controllers.create_ticket_controller()

# Rota de Detalhes do Chamado
@app.route('/tickets/<int:ticket_id>')
@login_required
def ticket_details(ticket_id):
    return controllers.ticket_details_controller(ticket_id)

# Rota para Adicionar Worklog/Atualização ao Chamado
@app.route('/tickets/<int:ticket_id>/worklog', methods=['POST'])
@login_required
def add_worklog(ticket_id):
    return controllers.add_worklog_controller(ticket_id)

# Rota de Edição do Próprio Perfil
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    return controllers.profile_controller()

# Rotas de Categorias de Chamados (Restrito ao Admin)
@app.route('/categories')
@admin_required
def list_categories():
    return controllers.list_categories_controller()

@app.route('/categories/new', methods=['POST'])
@admin_required
def create_category():
    return controllers.create_category_controller()

# Rota para Processar Feedback de Resolução do Cliente
@app.route('/tickets/<int:ticket_id>/feedback', methods=['POST'])
@login_required
def ticket_feedback(ticket_id):
    return controllers.ticket_feedback_controller(ticket_id)

@app.route('/categories/<int:category_id>/delete', methods=['POST'])
@admin_required
def delete_category(category_id):
    return controllers.delete_category_controller(category_id)

# Rotas de Cidades (Restrito ao Admin)
@app.route('/cities')
@admin_required
def list_cities():
    return controllers.list_cities_controller()

@app.route('/cities/new', methods=['POST'])
@admin_required
def create_city():
    return controllers.create_city_controller()

@app.route('/cities/<int:city_id>/delete', methods=['POST'])
@admin_required
def delete_city(city_id):
    return controllers.delete_city_controller(city_id)


if __name__ == '__main__':


    app.run(debug=True)
