"""
Tests - LeadCRM

Testes automatizados para validação da aplicação
"""

import unittest
from app import create_app, db
from app.models.user import User
from app.models.lead import Lead, LeadStatus


class AuthTestCase(unittest.TestCase):
    """Testes de autenticação"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        """Limpeza após cada teste"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_register_user(self):
        """Teste de registrar novo usuário"""
        response = self.client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'full_name': 'Test User',
            'password': 'password123',
            'confirm': 'password123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'sucesso', response.data.lower())
    
    def test_register_duplicate_username(self):
        """Teste de registro com username duplicado"""
        # Primeiro registro
        self.client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test1@example.com',
            'full_name': 'Test User 1',
            'password': 'password123',
            'confirm': 'password123'
        })
        
        # Segundo registro com mesmo username
        response = self.client.post('/auth/register', data={
            'username': 'testuser',
            'email': 'test2@example.com',
            'full_name': 'Test User 2',
            'password': 'password123',
            'confirm': 'password123'
        })
        
        self.assertIn(b'j', response.data)
    
    def test_login(self):
        """Teste de login"""
        # Registrar usuário
        with self.app.app_context():
            user = User(
                username='testuser',
                email='test@example.com',
                full_name='Test User'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        # Fazer login
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
    
    def test_login_invalid_password(self):
        """Teste de login com senha inválida"""
        with self.app.app_context():
            user = User(
                username='testuser',
                email='test@example.com'
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
        
        response = self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        self.assertIn(b'incorretos', response.data)


class LeadTestCase(unittest.TestCase):
    """Testes de CRUD de leads"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Criar usuário de teste
            self.user = User(
                username='testuser',
                email='test@example.com'
            )
            self.user.set_password('password123')
            db.session.add(self.user)
            db.session.commit()
            
            self.user_id = self.user.id
        
        # Fazer login
        self.client.post('/auth/login', data={
            'username': 'testuser',
            'password': 'password123'
        })
    
    def tearDown(self):
        """Limpeza após cada teste"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_create_lead(self):
        """Teste de criar novo lead"""
        response = self.client.post('/leads/create', data={
            'company_name': 'Test Company',
            'company_email': 'company@test.com',
            'contact_name': 'John Doe',
            'contact_email': 'john@test.com',
            'status': 'novo'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'sucesso', response.data.lower())
        
        # Verificar no banco
        with self.app.app_context():
            lead = Lead.query.filter_by(
                company_name='Test Company'
            ).first()
            self.assertIsNotNone(lead)
            self.assertEqual(lead.contact_name, 'John Doe')
    
    def test_list_leads(self):
        """Teste de listar leads"""
        # Criar alguns leads
        with self.app.app_context():
            for i in range(3):
                lead = Lead(
                    user_id=self.user_id,
                    company_name=f'Company {i}',
                    company_email=f'company{i}@test.com',
                    contact_name=f'Contact {i}',
                    contact_email=f'contact{i}@test.com'
                )
                db.session.add(lead)
            db.session.commit()
        
        response = self.client.get('/leads/list')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Company 0', response.data)
        self.assertIn(b'Company 1', response.data)
        self.assertIn(b'Company 2', response.data)
    
    def test_edit_lead(self):
        """Teste de editar lead"""
        # Criar lead
        with self.app.app_context():
            lead = Lead(
                user_id=self.user_id,
                company_name='Old Name',
                company_email='old@test.com',
                contact_name='Old Contact',
                contact_email='old@contact.com'
            )
            db.session.add(lead)
            db.session.commit()
            lead_id = lead.id
        
        # Editar lead
        response = self.client.post(f'/leads/{lead_id}/edit', data={
            'company_name': 'New Name',
            'company_email': 'new@test.com',
            'contact_name': 'New Contact',
            'contact_email': 'new@contact.com',
            'status': 'contatado'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar mudanças
        with self.app.app_context():
            lead = Lead.query.get(lead_id)
            self.assertEqual(lead.company_name, 'New Name')
            self.assertEqual(lead.status, LeadStatus.CONTATADO)
    
    def test_delete_lead(self):
        """Teste de deletar lead"""
        # Criar lead
        with self.app.app_context():
            lead = Lead(
                user_id=self.user_id,
                company_name='Test Company',
                company_email='test@company.com',
                contact_name='Test Contact',
                contact_email='test@contact.com'
            )
            db.session.add(lead)
            db.session.commit()
            lead_id = lead.id
        
        # Deletar lead
        response = self.client.post(f'/leads/{lead_id}/delete',
                                   follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        
        # Verificar se foi deletado
        with self.app.app_context():
            lead = Lead.query.get(lead_id)
            self.assertIsNone(lead)


class SecurityTestCase(unittest.TestCase):
    """Testes de segurança"""
    
    def setUp(self):
        """Configuração antes de cada teste"""
        self.app = create_app('testing')
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
            
            # Criar dois usuários
            self.user1 = User(username='user1', email='user1@test.com')
            self.user1.set_password('password123')
            
            self.user2 = User(username='user2', email='user2@test.com')
            self.user2.set_password('password123')
            
            db.session.add(self.user1)
            db.session.add(self.user2)
            db.session.commit()
            
            # Lead do user1
            self.lead = Lead(
                user_id=self.user1.id,
                company_name='User1 Company',
                company_email='user1@company.com',
                contact_name='User1 Contact',
                contact_email='user1@contact.com'
            )
            db.session.add(self.lead)
            db.session.commit()
    
    def tearDown(self):
        """Limpeza após cada teste"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_unauthorized_access(self):
        """Teste: user2 não consegue acessar lead de user1"""
        # Login como user2
        self.client.post('/auth/login', data={
            'username': 'user2',
            'password': 'password123'
        })
        
        # Tentar acessar lead de user1
        response = self.client.get(f'/leads/{self.lead.id}/view',
                                  follow_redirects=True)
        
        # Deve conter mensagem de erro
        self.assertIn(b'permiss', response.data.lower())
    
    def test_password_hash(self):
        """Teste: senhas são armazenadas com hash"""
        with self.app.app_context():
            user = User.query.filter_by(username='user1').first()
            
            # Senha nunca está em texto plano
            self.assertNotEqual(user.password_hash, 'password123')
            
            # Verificação funciona
            self.assertTrue(user.check_password('password123'))
            self.assertFalse(user.check_password('wrongpassword'))


if __name__ == '__main__':
    unittest.main()
