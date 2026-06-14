from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from app import db
from app.models.lead import Lead, LeadStatus
from wtforms import StringField, TextAreaField, FloatField, SelectField, validators
from wtforms.validators import Optional

leads_bp = Blueprint('leads', __name__, url_prefix='/leads')


class LeadForm(FlaskForm):
    """Formulário para criar/editar leads"""
    company_name = StringField('Nome da Empresa', [
        validators.DataRequired(message='Nome da empresa é obrigatório'),
        validators.Length(min=3, max=120)
    ])
    company_email = StringField('Email da Empresa', [
        validators.DataRequired(),
        validators.Email(message='Email inválido')
    ])
    company_phone = StringField('Telefone da Empresa', [Optional()])
    website = StringField('Website', [Optional()])
    
    contact_name = StringField('Nome do Contato', [
        validators.DataRequired(message='Nome do contato é obrigatório'),
        validators.Length(min=3, max=120)
    ])
    contact_position = StringField('Cargo do Contato', [Optional()])
    contact_email = StringField('Email do Contato', [
        validators.DataRequired(),
        validators.Email(message='Email inválido')
    ])
    contact_phone = StringField('Telefone do Contato', [Optional()])
    
    industry = StringField('Setor/Indústria', [Optional()])
    company_size = SelectField('Tamanho da Empresa', [Optional()], choices=[
        ('', 'Selecione...'),
        ('1-10', '1-10 pessoas'),
        ('11-50', '11-50 pessoas'),
        ('51-200', '51-200 pessoas'),
        ('201-500', '201-500 pessoas'),
        ('500+', 'Mais de 500 pessoas')
    ])
    status = SelectField('Status', [validators.DataRequired()], choices=[
        (status.value, status.value.capitalize()) for status in LeadStatus
    ])
    
    description = TextAreaField('Descrição/Notas', [Optional()])
    estimated_value = FloatField('Valor Estimado (R$)', [Optional()])


@leads_bp.route('/list')
@login_required
def list_leads():
    """Lista todos os leads do usuário autenticado"""
    page = request.args.get('page', 1, type=int)
    status_filter = request.args.get('status', '', type=str)
    search_query = request.args.get('search', '', type=str)
    
    query = Lead.query.filter_by(user_id=current_user.id)
    
    # Filtrar por status
    if status_filter and status_filter != 'all':
        try:
            status_enum = LeadStatus(status_filter)
            query = query.filter_by(status=status_enum)
        except ValueError:
            pass
    
    # Buscar por empresa ou contato
    if search_query:
        search = f"%{search_query}%"
        query = query.filter(
            (Lead.company_name.ilike(search)) |
            (Lead.contact_name.ilike(search)) |
            (Lead.company_email.ilike(search))
        )
    
    # Paginação
    pagination = query.order_by(Lead.created_at.desc()).paginate(page=page, per_page=10)
    leads = pagination.items
    
    return render_template(
        'leads/list.html',
        leads=leads,
        pagination=pagination,
        status_filter=status_filter,
        search_query=search_query,
        statuses=LeadStatus
    )


@leads_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_lead():
    """Criar novo lead"""
    form = LeadForm(request.form)
    
    if request.method == 'POST' and form.validate():
        try:
            # Escapar dados para evitar XSS
            lead = Lead(
                user_id=current_user.id,
                company_name=form.company_name.data.strip(),
                company_email=form.company_email.data.strip().lower(),
                company_phone=form.company_phone.data or None,
                website=form.website.data or None,
                contact_name=form.contact_name.data.strip(),
                contact_position=form.contact_position.data or None,
                contact_email=form.contact_email.data.strip().lower(),
                contact_phone=form.contact_phone.data or None,
                industry=form.industry.data or None,
                company_size=form.company_size.data or None,
                status=LeadStatus(form.status.data),
                description=form.description.data or None,
                estimated_value=form.estimated_value.data or None
            )
            
            db.session.add(lead)
            db.session.commit()
            
            flash(f'Lead "{lead.company_name}" criado com sucesso!', 'success')
            return redirect(url_for('leads.list_leads'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar lead: {str(e)}', 'danger')
    
    return render_template('leads/create.html', form=form, statuses=LeadStatus)


@leads_bp.route('/<int:lead_id>/view')
@login_required
def view_lead(lead_id):
    """Visualizar detalhes de um lead"""
    lead = Lead.query.get_or_404(lead_id)
    
    # Validar propriedade do lead
    if lead.user_id != current_user.id:
        flash('Você não tem permissão para acessar este lead.', 'danger')
        return redirect(url_for('leads.list_leads'))
    
    return render_template('leads/view.html', lead=lead)


@leads_bp.route('/<int:lead_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_lead(lead_id):
    """Editar um lead"""
    lead = Lead.query.get_or_404(lead_id)
    
    # Validar propriedade do lead
    if lead.user_id != current_user.id:
        flash('Você não tem permissão para editar este lead.', 'danger')
        return redirect(url_for('leads.list_leads'))
    
    form = LeadForm(request.form)
    
    if request.method == 'GET':
        # Carregar dados do lead no formulário
        form.company_name.data = lead.company_name
        form.company_email.data = lead.company_email
        form.company_phone.data = lead.company_phone
        form.website.data = lead.website
        form.contact_name.data = lead.contact_name
        form.contact_position.data = lead.contact_position
        form.contact_email.data = lead.contact_email
        form.contact_phone.data = lead.contact_phone
        form.industry.data = lead.industry
        form.company_size.data = lead.company_size or ''
        form.status.data = lead.status.value
        form.description.data = lead.description
        form.estimated_value.data = lead.estimated_value
    
    elif form.validate():
        try:
            lead.company_name = form.company_name.data.strip()
            lead.company_email = form.company_email.data.strip().lower()
            lead.company_phone = form.company_phone.data or None
            lead.website = form.website.data or None
            lead.contact_name = form.contact_name.data.strip()
            lead.contact_position = form.contact_position.data or None
            lead.contact_email = form.contact_email.data.strip().lower()
            lead.contact_phone = form.contact_phone.data or None
            lead.industry = form.industry.data or None
            lead.company_size = form.company_size.data or None
            lead.status = LeadStatus(form.status.data)
            lead.description = form.description.data or None
            lead.estimated_value = form.estimated_value.data or None
            
            db.session.commit()
            
            flash(f'Lead "{lead.company_name}" atualizado com sucesso!', 'success')
            return redirect(url_for('leads.view_lead', lead_id=lead.id))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao editar lead: {str(e)}', 'danger')
    
    return render_template('leads/edit.html', form=form, lead=lead, statuses=LeadStatus)


@leads_bp.route('/<int:lead_id>/delete', methods=['POST'])
@login_required
def delete_lead(lead_id):
    """Deletar um lead"""
    lead = Lead.query.get_or_404(lead_id)
    
    # Validar propriedade do lead
    if lead.user_id != current_user.id:
        flash('Você não tem permissão para deletar este lead.', 'danger')
        return redirect(url_for('leads.list_leads'))
    
    try:
        company_name = lead.company_name
        db.session.delete(lead)
        db.session.commit()
        
        flash(f'Lead "{company_name}" deletado com sucesso!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao deletar lead: {str(e)}', 'danger')
    
    return redirect(url_for('leads.list_leads'))


@leads_bp.route('/api/statistics')
@login_required
def statistics():
    """API para obter estatísticas dos leads do usuário"""
    leads = Lead.query.filter_by(user_id=current_user.id)
    
    total_leads = leads.count()
    by_status = {}
    total_value = 0.0
    
    for status in LeadStatus:
        count = leads.filter_by(status=status).count()
        by_status[status.value] = count
    
    total_value = sum([lead.estimated_value or 0 for lead in leads])
    
    return jsonify({
        'total_leads': total_leads,
        'by_status': by_status,
        'total_estimated_value': round(total_value, 2)
    })
