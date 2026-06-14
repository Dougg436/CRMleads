# LeadCRM - Sistema de Gerenciamento de Leads

Sistema web para gerenciamento de leads de empresas, desenvolvido com Flask.

## Funcionalidades

- ✓ Autenticação e login seguro
- ✓ CRUD completo de leads
- ✓ 6 status diferentes (Novo, Contatado, Qualificado, Negociação, Convertido, Perdido)
- ✓ Busca e filtro por status
- ✓ Dashboard com estatísticas
- ✓ Proteção contra SQL Injection, XSS e CSRF
- ✓ Interface responsiva com Bootstrap

## Tecnologias

- **Backend**: Python, Flask, SQLAlchemy
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Banco**: MySQL/PostgreSQL/SQLite
- **Segurança**: Senhas hash, proteção CSRF, validação de entrada

## Instalação

### 1. Ambiente Virtual
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

### 2. Dependências
```bash
pip install -r requirements.txt
```

### 3. Configuração
```bash
copy .env.example .env
# Edite .env com seus dados (database_url, chaves, etc)
```

### 4. Inicie
```bash
python run.py
```

Acesse: **http://localhost:5000**

## Estrutura

```
projeto-leads/
├── app/
│   ├── models/       → Usuário e Lead
│   ├── auth/         → Login/Register
│   ├── leads/        → CRUD de leads
│   ├── main/         → Dashboard
│   ├── templates/    → HTML (Bootstrap)
│   └── static/       → CSS/JS
├── config.py         → Configurações
├── run.py            → Inicia aplicação
└── requirements.txt  → Dependências
```

## Segurança Implementada

- Autenticação com Flask-Login
- Senhas com hash PBKDF2:SHA256
- Proteção CSRF em formulários
- SQL Injection: SQLAlchemy parametrizado
- XSS: Escapamento Jinja2
- Validação de entrada em todos os campos
- Controle de acesso por usuário

## Criar e Testar

### Registrar
1. Acesse http://localhost:5000
2. Clique em "Registrar"
3. Preencha dados e confirme

### Usar o Sistema
1. Faça login com suas credenciais
2. Clique em "Novo Lead"
3. Preencha informações da empresa e contato
4. Veja seus leads no dashboard

## Testes

```bash
python -m unittest tests.py -v
```

---

**Desenvolvido como projeto acadêmico para a disciplina de Desenvolvimento Web 2.**
