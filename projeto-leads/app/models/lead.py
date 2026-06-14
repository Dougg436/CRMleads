from app import db
from datetime import datetime
from enum import Enum


class LeadStatus(Enum):
    """Estados possíveis de um lead"""
    NOVO = 'novo'
    CONTATADO = 'contatado'
    QUALIFICADO = 'qualificado'
    NEGOCIAÇÃO = 'negociação'
    CONVERTIDO = 'convertido'
    PERDIDO = 'perdido'


class Lead(db.Model):
    """Modelo de lead/empresa"""
    
    __tablename__ = 'leads'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Informações da empresa
    company_name = db.Column(db.String(120), nullable=False, index=True)
    company_email = db.Column(db.String(120), nullable=False)
    company_phone = db.Column(db.String(20), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    
    # Informações do contato
    contact_name = db.Column(db.String(120), nullable=False)
    contact_position = db.Column(db.String(100), nullable=True)
    contact_email = db.Column(db.String(120), nullable=False)
    contact_phone = db.Column(db.String(20), nullable=True)
    
    # Informações comerciais
    industry = db.Column(db.String(100), nullable=True)
    company_size = db.Column(db.String(50), nullable=True)  # ex: 1-10, 11-50, 51-200, etc
    status = db.Column(db.Enum(LeadStatus), default=LeadStatus.NOVO, nullable=False)
    
    # Detalhes do lead
    description = db.Column(db.Text, nullable=True)
    estimated_value = db.Column(db.Float, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contact = db.Column(db.DateTime, nullable=True)
    
    def to_dict(self):
        """Serializa o lead para dicionário"""
        return {
            'id': self.id,
            'company_name': self.company_name,
            'company_email': self.company_email,
            'company_phone': self.company_phone,
            'website': self.website,
            'contact_name': self.contact_name,
            'contact_position': self.contact_position,
            'contact_email': self.contact_email,
            'contact_phone': self.contact_phone,
            'industry': self.industry,
            'company_size': self.company_size,
            'status': self.status.value if self.status else None,
            'description': self.description,
            'estimated_value': self.estimated_value,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<Lead {self.company_name}>'
