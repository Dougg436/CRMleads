from flask import Blueprint, render_template
from flask_login import current_user
from app.models.lead import Lead
from app.models.lead import LeadStatus

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Página inicial/dashboard"""
    
    if current_user.is_authenticated:
        # Dashboard para usuários autenticados
        total_leads = Lead.query.filter_by(user_id=current_user.id).count()
        leads_by_status = {}
        
        for status in LeadStatus:
            leads_by_status[status.value] = Lead.query.filter_by(
                user_id=current_user.id,
                status=status
            ).count()
        
        recent_leads = Lead.query.filter_by(user_id=current_user.id).order_by(
            Lead.created_at.desc()
        ).limit(5).all()
        
        return render_template(
            'index.html',
            total_leads=total_leads,
            leads_by_status=leads_by_status,
            recent_leads=recent_leads
        )
    else:
        # Landing page para usuários não autenticados
        return render_template('landing.html')


@main_bp.route('/about')
def about():
    """Página sobre o projeto"""
    return render_template('about.html')
