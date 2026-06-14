from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from flask_wtf import FlaskForm
from app import db
from app.models.user import User
from wtforms import StringField, PasswordField, validators

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


class RegistrationForm(FlaskForm):
    """Formulário de registro com validação CSRF"""
    username = StringField('Usuário', [
        validators.Length(min=4, max=80, message='Usuário deve ter entre 4 e 80 caracteres'),
        validators.Regexp('^[a-zA-Z0-9_]*$', message='Usuário pode conter apenas letras, números e underscore')
    ])
    email = StringField('Email', [
        validators.Email(message='Email inválido'),
        validators.Length(max=120)
    ])
    full_name = StringField('Nome Completo', [
        validators.Length(min=3, max=120)
    ])
    password = PasswordField('Senha', [
        validators.DataRequired(message='Senha é obrigatória'),
        validators.Length(min=6, message='Senha deve ter no mínimo 6 caracteres')
    ])
    confirm = PasswordField('Confirmar Senha', [
        validators.DataRequired(),
        validators.EqualTo('password', message='Senhas devem ser iguais')
    ])


class LoginForm(FlaskForm):
    """Formulário de login com validação CSRF"""
    username = StringField('Usuário', [validators.DataRequired()])
    password = PasswordField('Senha', [validators.DataRequired()])


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Rota de registro de novo usuário"""
    
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = RegistrationForm(request.form)
    
    if request.method == 'POST' and form.validate():
        # Verificar se usuário já existe
        if User.query.filter_by(username=form.username.data).first():
            flash('Usuário já existe. Escolha outro.', 'danger')
            return redirect(url_for('auth.register'))
        
        if User.query.filter_by(email=form.email.data).first():
            flash('Email já cadastrado.', 'danger')
            return redirect(url_for('auth.register'))
        
        try:
            # Criar novo usuário
            user = User(
                username=form.username.data,
                email=form.email.data,
                full_name=form.full_name.data
            )
            user.set_password(form.password.data)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registro realizado com sucesso! Faça login para continuar.', 'success')
            return redirect(url_for('auth.login'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao registrar: {str(e)}', 'danger')
    
    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Rota de login"""
    
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    form = LoginForm(request.form)
    
    if request.method == 'POST' and form.validate():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=request.form.get('remember_me', False))
            next_page = request.args.get('next')
            
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            
            flash(f'Bem-vindo, {user.username}!', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Usuário ou senha incorretos.', 'danger')
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Rota de logout"""
    logout_user()
    flash('Você saiu da aplicação.', 'info')
    return redirect(url_for('main.index'))


@auth_bp.route('/profile')
@login_required
def profile():
    """Rota do perfil do usuário"""
    return render_template('auth/profile.html', user=current_user)


@auth_bp.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Atualizar perfil do usuário"""
    try:
        current_user.full_name = request.form.get('full_name', current_user.full_name)
        
        # Validar email
        new_email = request.form.get('email', current_user.email)
        if new_email != current_user.email:
            if User.query.filter_by(email=new_email).first():
                flash('Email já cadastrado.', 'danger')
                return redirect(url_for('auth.profile'))
            current_user.email = new_email
        
        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao atualizar perfil: {str(e)}', 'danger')
    
    return redirect(url_for('auth.profile'))
