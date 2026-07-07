from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    sobrenome = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    cidade_id = db.Column(db.Integer, db.ForeignKey("cidades.id"), nullable=True)
    cidade = db.relationship("Cidade", backref=db.backref("usuarios", lazy=True))

    perfis = db.relationship("Perfil", backref="usuario", lazy=True, cascade="all, delete-orphan")

    @property
    def tipo_perfil(self):
        if self.perfis:
            return self.perfis[0].tipo_perfil
        return "Cliente"

    def set_senha(self, senha_plana):
        self.senha = generate_password_hash(senha_plana)

    def verificar_senha(self, senha_plana):
        return check_password_hash(self.senha, senha_plana)

    def __repr__(self):
        return f"<Usuario {self.username}>"



class Cidade(db.Model):
    __tablename__ = "cidades"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    estado = db.Column(db.String(2), nullable=False)


class Perfil(db.Model):
    __tablename__ = "perfis"

    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    tipo_perfil = db.Column(db.String(50), nullable=False)
    ativo = db.Column(db.Boolean, default=True)


class Categoria(db.Model):
    __tablename__ = "categorias"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False, unique=True)
    descricao = db.Column(db.String(255))


class Chamado(db.Model):
    __tablename__ = "chamados"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    prioridade = db.Column(db.String(20), nullable=False, default="Média")  # Baixa, Média, Alta
    status = db.Column(db.String(20), nullable=False, default="Aberto")  # Aberto, Em Andamento, Resolvido, Fechado
    data_criacao = db.Column(db.DateTime, nullable=False, default=db.func.now())

    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    usuario = db.relationship("Usuario", backref=db.backref("chamados", lazy=True))

    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias.id"), nullable=True)
    categoria = db.relationship("Categoria", backref=db.backref("chamados", lazy=True))



class Worklog(db.Model):
    __tablename__ = "worklogs"

    id = db.Column(db.Integer, primary_key=True)
    chamado_id = db.Column(db.Integer, db.ForeignKey("chamados.id"), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=False)
    mensagem = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=db.func.now())

    chamado = db.relationship("Chamado", backref=db.backref("worklogs", lazy=True, cascade="all, delete-orphan"))
    usuario = db.relationship("Usuario", backref=db.backref("worklogs", lazy=True))


