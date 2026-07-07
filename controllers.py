from flask import render_template, request, redirect, url_for, flash, session
from models import db, Usuario, Chamado, Perfil, Worklog, Categoria, Cidade

def index_controller():
    if 'user_id' in session:
        if session.get('tipo_perfil') == 'Admin':
            return redirect(url_for('list_users'))
        return redirect(url_for('list_tickets'))
    return redirect(url_for('login'))

def login_controller():
    if 'user_id' in session:
        return redirect(url_for('list_users'))

    if request.method == 'POST':
        username_or_email = request.form.get('username_or_email').strip()
        senha = request.form.get('senha')

        # Busca por username ou email
        usuario = Usuario.query.filter(
            (Usuario.username == username_or_email) | (Usuario.email == username_or_email)
        ).first()

        if usuario and usuario.verificar_senha(senha):
            session['user_id'] = usuario.id
            session['username'] = usuario.username
            session['tipo_perfil'] = usuario.tipo_perfil
            flash(f'Bem-vindo, {usuario.nome}! Login realizado com sucesso.', 'success')
            # Admins vão para a lista de usuários, outros vão para lista de chamados
            if usuario.tipo_perfil == 'Admin':
                return redirect(url_for('list_users'))
            return redirect(url_for('list_tickets'))
        else:
            flash('Usuário/E-mail ou senha incorretos.', 'danger')

    return render_template('login.html')

def logout_controller():
    session.clear()
    flash('Você saiu do sistema.', 'info')
    return redirect(url_for('login'))

def register_controller():
    cidades = Cidade.query.all()
    if request.method == 'POST':
        nome = request.form.get('nome').strip()
        sobrenome = request.form.get('sobrenome').strip()
        email = request.form.get('email').strip().lower()
        username = request.form.get('username').strip().lower()
        senha = request.form.get('senha')

        # Validações básicas
        if Usuario.query.filter_by(email=email).first():
            flash('Este endereço de e-mail já está cadastrado.', 'danger')
            return render_template('register.html', cidades=cidades)
        
        if Usuario.query.filter_by(username=username).first():
            flash('Este nome de usuário já está em uso.', 'danger')
            return render_template('register.html', cidades=cidades)

        # Somente admins podem definir perfis diferentes de Cliente e preencher Cidade/Estado
        if session.get('tipo_perfil') == 'Admin':
            tipo_perfil = request.form.get('tipo_perfil', 'Cliente')
            cidade_id = request.form.get('cidade_id')
            if cidade_id == "":
                cidade_id = None
            else:
                cidade_id = int(cidade_id)
        else:
            tipo_perfil = 'Cliente'
            cidade_id = None

        # Criar novo usuário
        novo_usuario = Usuario(
            nome=nome,
            sobrenome=sobrenome,
            email=email,
            username=username,
            cidade_id=cidade_id
        )
        novo_usuario.set_senha(senha)

        # Adicionar o perfil ao novo usuário
        novo_perfil = Perfil(tipo_perfil=tipo_perfil)
        novo_usuario.perfis.append(novo_perfil)

        try:
            db.session.add(novo_usuario)
            db.session.commit()
            flash('Conta criada com sucesso! Faça login para continuar.', 'success')
            if 'user_id' in session:
                return redirect(url_for('list_users'))
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash('Ocorreu um erro ao salvar o usuário. Tente novamente.', 'danger')

    return render_template('register.html', cidades=cidades)

def list_users_controller():
    usuarios = Usuario.query.all()
    return render_template('users.html', usuarios=usuarios)

def edit_user_controller(user_id):
    usuario = Usuario.query.get_or_404(user_id)
    cidades = Cidade.query.all()

    if request.method == 'POST':
        nome = request.form.get('nome').strip()
        sobrenome = request.form.get('sobrenome').strip()
        email = request.form.get('email').strip().lower()
        username = request.form.get('username').strip().lower()
        senha = request.form.get('senha')

        # Verifica duplicidade de email/username se mudaram
        if email != usuario.email and Usuario.query.filter_by(email=email).first():
            flash('Este endereço de e-mail já está em uso por outro usuário.', 'danger')
            return render_template('user_edit.html', usuario=usuario, cidades=cidades)
        
        if username != usuario.username and Usuario.query.filter_by(username=username).first():
            flash('Este nome de usuário já está em uso por outro usuário.', 'danger')
            return render_template('user_edit.html', usuario=usuario, cidades=cidades)

        tipo_perfil = request.form.get('tipo_perfil')
        cidade_id = request.form.get('cidade_id')
        if cidade_id == "":
            cidade_id = None
        else:
            cidade_id = int(cidade_id)

        usuario.nome = nome
        usuario.sobrenome = sobrenome
        usuario.email = email
        usuario.cidade_id = cidade_id
        
        if usuario.id == session.get('user_id'):
            if username != usuario.username:
                session['username'] = username
            session['tipo_perfil'] = tipo_perfil
        usuario.username = username

        if senha:
            usuario.set_senha(senha)

        # Atualiza ou cria o perfil correspondente
        perfil = Perfil.query.filter_by(usuario_id=usuario.id).first()
        if perfil:
            perfil.tipo_perfil = tipo_perfil
        else:
            novo_perfil = Perfil(usuario_id=usuario.id, tipo_perfil=tipo_perfil)
            db.session.add(novo_perfil)

        try:
            db.session.commit()
            flash('Usuário atualizado com sucesso!', 'success')
            return redirect(url_for('list_users'))
        except Exception as e:
            db.session.rollback()
            flash('Ocorreu um erro ao atualizar o usuário.', 'danger')

    return render_template('user_edit.html', usuario=usuario, cidades=cidades)

def delete_user_controller(user_id):
    usuario = Usuario.query.get_or_404(user_id)
    is_self = (usuario.id == session.get('user_id'))

    try:
        db.session.delete(usuario)
        db.session.commit()
        if is_self:
            session.clear()
            flash('Sua conta foi excluída com sucesso.', 'info')
            return redirect(url_for('login'))
        else:
            flash(f'Usuário {usuario.nome} excluído com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao tentar excluir o usuário.', 'danger')

    return redirect(url_for('list_users'))

def list_tickets_controller():
    usuario = Usuario.query.get(session.get('user_id'))
    if usuario and usuario.tipo_perfil == 'Cliente':
        chamados = Chamado.query.filter_by(usuario_id=usuario.id).all()
    else:
        chamados = Chamado.query.all()
    return render_template('tickets.html', chamados=chamados)

def create_ticket_controller():
    categorias = Categoria.query.all()
    if request.method == 'POST':
        titulo = request.form.get('titulo').strip()
        descricao = request.form.get('descricao').strip()
        prioridade = request.form.get('prioridade')
        categoria_id = request.form.get('categoria_id')

        if not titulo or not descricao:
            flash('Título e descrição são campos obrigatórios.', 'danger')
            return render_template('ticket_new.html', categorias=categorias)

        # Tratar categoria_id vazio
        if categoria_id == "":
            categoria_id = None
        else:
            categoria_id = int(categoria_id)

        novo_chamado = Chamado(
            titulo=titulo,
            descricao=descricao,
            prioridade=prioridade,
            categoria_id=categoria_id,
            usuario_id=session.get('user_id')
        )

        try:
            db.session.add(novo_chamado)
            db.session.commit()
            flash('Chamado aberto com sucesso!', 'success')
            return redirect(url_for('list_tickets'))
        except Exception as e:
            db.session.rollback()
            flash('Ocorreu um erro ao abrir o chamado. Tente novamente.', 'danger')

    return render_template('ticket_new.html', categorias=categorias)

def ticket_details_controller(ticket_id):
    chamado = Chamado.query.get_or_404(ticket_id)
    usuario = Usuario.query.get(session.get('user_id'))

    # Clientes só podem ver os seus próprios chamados
    if usuario.tipo_perfil == 'Cliente' and chamado.usuario_id != usuario.id:
        flash('Você não tem permissão para visualizar este chamado.', 'danger')
        return redirect(url_for('list_tickets'))

    return render_template('ticket_details.html', chamado=chamado, usuario=usuario)

def add_worklog_controller(ticket_id):
    chamado = Chamado.query.get_or_404(ticket_id)
    usuario = Usuario.query.get(session.get('user_id'))

    # Clientes só podem responder a seus próprios chamados
    if usuario.tipo_perfil == 'Cliente' and chamado.usuario_id != usuario.id:
        flash('Você não tem permissão para atualizar este chamado.', 'danger')
        return redirect(url_for('list_tickets'))

    mensagem = request.form.get('mensagem', '').strip()
    if not mensagem:
        flash('A mensagem da atualização não pode estar vazia.', 'danger')
        return redirect(url_for('ticket_details', ticket_id=ticket_id))

    # Técnicos e Admins podem atualizar o status do chamado
    if usuario.tipo_perfil in ['Técnico', 'Admin']:
        novo_status = request.form.get('status')
        if novo_status and novo_status in ['Aberto', 'Em Andamento', 'Resolvido', 'Fechado']:
            if chamado.status != novo_status:
                chamado.status = novo_status
                # Registrar a mudança de status também no worklog
                status_log = Worklog(
                    chamado_id=chamado.id,
                    usuario_id=usuario.id,
                    mensagem=f"Alterou o status para: {novo_status}"
                )
                db.session.add(status_log)

    novo_worklog = Worklog(
        chamado_id=chamado.id,
        usuario_id=usuario.id,
        mensagem=mensagem
    )

    try:
        db.session.add(novo_worklog)
        db.session.commit()
        flash('Atualização registrada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu um erro ao salvar o histórico. Tente novamente.', 'danger')

    return redirect(url_for('ticket_details', ticket_id=ticket_id))

def profile_controller():
    usuario = Usuario.query.get(session.get('user_id'))

    if request.method == 'POST':
        nome = request.form.get('nome').strip()
        sobrenome = request.form.get('sobrenome').strip()
        email = request.form.get('email').strip().lower()
        username = request.form.get('username').strip().lower()
        senha = request.form.get('senha')

        # Validações de duplicidade
        if email != usuario.email and Usuario.query.filter_by(email=email).first():
            flash('Este endereço de e-mail já está em uso por outro usuário.', 'danger')
            return render_template('profile.html', usuario=usuario)

        if username != usuario.username and Usuario.query.filter_by(username=username).first():
            flash('Este nome de usuário já está em uso por outro usuário.', 'danger')
            return render_template('profile.html', usuario=usuario)

        usuario.nome = nome
        usuario.sobrenome = sobrenome
        usuario.email = email
        usuario.username = username
        
        # Atualiza a sessão
        session['username'] = username

        if senha:
            usuario.set_senha(senha)

        try:
            db.session.commit()
            flash('Seu perfil foi atualizado com sucesso!', 'success')
            return redirect(url_for('user_profile'))
        except Exception as e:
            db.session.rollback()
            flash('Ocorreu um erro ao atualizar seu perfil.', 'danger')

    return render_template('profile.html', usuario=usuario)

def list_categories_controller():
    categorias = Categoria.query.all()
    return render_template('categories.html', categorias=categorias)

def create_category_controller():
    nome = request.form.get('nome', '').strip()
    descricao = request.form.get('descricao', '').strip()

    if not nome:
        flash('O nome da categoria é obrigatório.', 'danger')
        return redirect(url_for('list_categories'))

    if Categoria.query.filter_by(nome=nome).first():
        flash('Esta categoria já existe.', 'danger')
        return redirect(url_for('list_categories'))

    nova_categoria = Categoria(nome=nome, descricao=descricao)
    try:
        db.session.add(nova_categoria)
        db.session.commit()
        flash(f'Categoria "{nome}" criada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu um erro ao criar a categoria.', 'danger')

    return redirect(url_for('list_categories'))

def delete_category_controller(category_id):
    categoria = Categoria.query.get_or_404(category_id)
    try:
        # Desassocia os chamados dessa categoria antes de excluir para evitar erro de integridade
        for chamado in categoria.chamados:
            chamado.categoria_id = None
        db.session.delete(categoria)
        db.session.commit()
        flash(f'Categoria "{categoria.nome}" excluída com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu um erro ao excluir a categoria.', 'danger')

    return redirect(url_for('list_categories'))

def ticket_feedback_controller(ticket_id):
    chamado = Chamado.query.get_or_404(ticket_id)
    usuario = Usuario.query.get(session.get('user_id'))

    # Somente o dono do chamado pode dar feedback
    if chamado.usuario_id != usuario.id:
        flash('Você não tem permissão para responder a este chamado.', 'danger')
        return redirect(url_for('list_tickets'))

    satisfacao = request.form.get('satisfacao')
    if satisfacao == 'Sim':
        chamado.status = 'Fechado'
        feedback_log = Worklog(
            chamado_id=chamado.id,
            usuario_id=usuario.id,
            mensagem="O cliente confirmou a solução. Chamado fechado."
        )
        db.session.add(feedback_log)
        flash('Obrigado! O chamado foi marcado como Concluído/Fechado.', 'success')
    elif satisfacao == 'Não':
        chamado.status = 'Aberto'
        feedback_log = Worklog(
            chamado_id=chamado.id,
            usuario_id=usuario.id,
            mensagem="O cliente informou que a solução NÃO atendeu ao problema. Chamado reaberto."
        )
        db.session.add(feedback_log)
        flash('O chamado foi reaberto e a equipe técnica será notificada.', 'info')
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('Erro ao processar sua resposta.', 'danger')

    return redirect(url_for('ticket_details', ticket_id=ticket_id))

def list_cities_controller():
    cidades = Cidade.query.all()
    return render_template('cities.html', cidades=cidades)

def create_city_controller():
    nome = request.form.get('nome', '').strip()
    estado = request.form.get('estado', '').strip().upper()

    if not nome or not estado:
        flash('Nome da cidade e Estado (UF) são obrigatórios.', 'danger')
        return redirect(url_for('list_cities'))

    if Cidade.query.filter_by(nome=nome).first():
        flash('Esta cidade já está cadastrada.', 'danger')
        return redirect(url_for('list_cities'))

    nova_cidade = Cidade(nome=nome, estado=estado)
    try:
        db.session.add(nova_cidade)
        db.session.commit()
        flash(f'Cidade "{nome} - {estado}" cadastrada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu um erro ao cadastrar a cidade.', 'danger')

    return redirect(url_for('list_cities'))

def delete_city_controller(city_id):
    cidade = Cidade.query.get_or_404(city_id)
    try:
        # Desassocia os usuários dessa cidade antes de excluir
        for usuario in cidade.usuarios:
            usuario.cidade_id = None
        db.session.delete(cidade)
        db.session.commit()
        flash(f'Cidade "{cidade.nome} - {cidade.estado}" excluída com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Ocorreu um erro ao excluir a cidade.', 'danger')

    return redirect(url_for('list_cities'))


