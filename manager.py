#!/usr/bin/env python
"""Nexus PCM - Gerenciamento de Clientes"""

import os
import json
import hashlib
import asyncio
from pathlib import Path
from datetime import datetime
from uuid import uuid4

CLIENTS_DIR = Path("clients")
CLIENTS_FILE = CLIENTS_DIR / "clients.json"

def init_dirs():
    CLIENTS_DIR.mkdir(exist_ok=True)
    if not CLIENTS_FILE.exists():
        with open(CLIENTS_FILE, "w") as f:
            json.dump({}, f)

def print_banner():
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║     NEXUS PCM - SISTEMA DE MANUTENÇÃO INDUSTRIAL            ║
    ║     Versão 1.0                                              ║
    ║     Preço: R$ 397/mês                                       ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)

def load_clients():
    if not CLIENTS_FILE.exists():
        return {}
    with open(CLIENTS_FILE, "r") as f:
        return json.load(f)

def save_clients(clients):
    with open(CLIENTS_FILE, "w") as f:
        json.dump(clients, f, indent=2)

def listar_clientes():
    clients = load_clients()
    if not clients:
        print("\n📭 Nenhum cliente cadastrado.\n")
        return
    
    print("\n" + "="*80)
    print("📋 CLIENTES CADASTRADOS")
    print("="*80)
    print(f"{'ID':<10} {'EMPRESA':<35} {'STATUS':<10} {'DATA':<12}")
    print("-"*80)
    
    for client_id, client in clients.items():
        status_icon = "🟢" if client.get("status") == "ativo" else "🔴"
        print(f"{client_id:<10} {client.get('empresa', '')[:35]:<35} {status_icon} {client.get('status', ''):<10} {client.get('data_criacao', '')[:10]}")
    
    print("="*80)

async def init_client_database(db_path):
    try:
        from sqlalchemy.ext.asyncio import create_async_engine
        from sqlalchemy import text
        
        db_url = f"sqlite+aiosqlite:///{db_path}"
        engine = create_async_engine(db_url, echo=False)
        
        async with engine.begin() as conn:
            # Tabela users
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(36) PRIMARY KEY,
                    company_id VARCHAR(36) NOT NULL,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    full_name VARCHAR(255) NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    is_superuser BOOLEAN DEFAULT 0,
                    role VARCHAR(50) DEFAULT 'user',
                    company_name VARCHAR(200),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Tabela assets
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS assets (
                    id VARCHAR(36) PRIMARY KEY,
                    company_id VARCHAR(36) NOT NULL,
                    code VARCHAR(50) NOT NULL UNIQUE,
                    name VARCHAR(200) NOT NULL,
                    description TEXT,
                    asset_type VARCHAR(50),
                    manufacturer VARCHAR(100),
                    model VARCHAR(100),
                    serial_number VARCHAR(100),
                    location VARCHAR(200),
                    department VARCHAR(100),
                    total_operating_hours FLOAT DEFAULT 0,
                    failure_count INTEGER DEFAULT 0,
                    status VARCHAR(50) DEFAULT 'active',
                    critical_level INTEGER DEFAULT 3,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """))
            
            # Tabela work_orders
            await conn.execute(text("""
                CREATE TABLE IF NOT EXISTS work_orders (
                    id VARCHAR(36) PRIMARY KEY,
                    company_id VARCHAR(36) NOT NULL,
                    asset_id VARCHAR(36) NOT NULL,
                    code VARCHAR(50) NOT NULL UNIQUE,
                    title VARCHAR(200) NOT NULL,
                    description TEXT,
                    maintenance_type VARCHAR(50),
                    priority INTEGER DEFAULT 1,
                    requested_date DATETIME,
                    scheduled_date DATETIME,
                    status VARCHAR(50) DEFAULT 'opened',
                    assigned_team VARCHAR(200),
                    labor_hours FLOAT DEFAULT 0,
                    parts_cost FLOAT DEFAULT 0,
                    total_cost FLOAT DEFAULT 0,
                    downtime_hours FLOAT DEFAULT 0,
                    reported_problem TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (asset_id) REFERENCES assets(id)
                )
            """))
            
            # Criar usuário admin
            admin_id = str(uuid4())
            company_id = str(uuid4())
            password_hash = hashlib.sha256("admin123".encode()).hexdigest()
            
            await conn.execute(text("""
                INSERT INTO users (id, company_id, email, username, full_name, hashed_password, is_superuser, role, company_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """), (admin_id, company_id, "admin@cliente.com", "admin", "Administrador", password_hash, 1, "admin", "Empresa Demo"))
            
            # Criar ativo de exemplo
            asset_id = str(uuid4())
            await conn.execute(text("""
                INSERT INTO assets (id, company_id, code, name, asset_type, manufacturer, model, location, critical_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """), (asset_id, company_id, "MAQ-001", "Prensa Hidráulica 500T", "equipment", "Bosch", "PH-5000", "Setor A - Linha 1", 5))
        
        await engine.dispose()
        return True
    except Exception as e:
        print(f"Erro: {e}")
        return False

def criar_cliente():
    print("\n" + "="*60)
    print("➕ NOVO CLIENTE - NEXUS PCM")
    print("="*60)
    
    nome_empresa = input("\nNome da Empresa: ").strip()
    if not nome_empresa:
        print("❌ Nome obrigatório")
        return
    
    contato = input("E-mail de contato: ").strip()
    
    print("\n📦 PLANOS DISPONÍVEIS:")
    print("   1. PCM Basic - R$ 397/mês")
    print("   2. PCM Pro - R$ 597/mês")
    print("   3. PCM Enterprise - R$ 997/mês")
    
    plano_opcao = input("\nEscolha o plano (1-3): ").strip()
    planos = {"1": "basic", "2": "pro", "3": "enterprise"}
    plano = planos.get(plano_opcao, "basic")
    
    precos = {"basic": 397, "pro": 597, "enterprise": 997}
    preco = precos.get(plano, 397)
    
    print(f"\n💰 Valor: R$ {preco}/mês")
    
    confirmar = input("\nConfirmar criação? (s/n): ").strip().lower()
    if confirmar != 's':
        print("❌ Cancelado")
        return
    
    print("\n🔄 Criando cliente...")
    
    client_id = str(uuid4())[:8]
    client_dir = CLIENTS_DIR / f"cliente_{client_id}"
    client_dir.mkdir(exist_ok=True)
    
    db_path = client_dir / f"{client_id}.db"
    
    api_key = hashlib.sha256(f"{client_id}{nome_empresa}{datetime.now().isoformat()}".encode()).hexdigest()[:48]
    
    client_config = {
        "id": client_id,
        "empresa": nome_empresa,
        "contato": contato,
        "plano": plano,
        "preco": preco,
        "data_criacao": datetime.now().isoformat(),
        "status": "ativo",
        "database": str(db_path),
        "api_key": api_key
    }
    
    with open(client_dir / "config.json", "w") as f:
        json.dump(client_config, f, indent=2)
    
    clients = load_clients()
    clients[client_id] = {
        "id": client_id,
        "empresa": nome_empresa,
        "plano": plano,
        "preco": preco,
        "status": "ativo",
        "data_criacao": datetime.now().isoformat(),
        "contato": contato
    }
    save_clients(clients)
    
    print("📦 Inicializando banco de dados...")
    success = asyncio.run(init_client_database(db_path))
    
    if success:
        print("\n" + "="*60)
        print("✅ CLIENTE CRIADO COM SUCESSO!")
        print("="*60)
        print(f"\n📋 INFORMAÇÕES DO CLIENTE:")
        print(f"   ID: {client_id}")
        print(f"   Empresa: {nome_empresa}")
        print(f"   Plano: {plano.upper()} - R$ {preco}/mês")
        print(f"\n🔑 API KEY: {api_key}")
        print(f"\n👤 ACESSO ADMIN:")
        print(f"   Usuário: admin")
        print(f"   Senha: admin123")
        print(f"\n🌐 URL: http://localhost:8000")
        print("="*60)
        
        cred_file = client_dir / "credenciais.txt"
        with open(cred_file, "w", encoding="utf-8") as f:
            f.write(f"""
NEXUS PCM - CREDENCIAIS
=======================
Empresa: {nome_empresa}
ID: {client_id}
Plano: {plano.upper()}
Valor: R$ {preco}/mês

API KEY: {api_key}

ACESSO ADMIN:
Usuário: admin
Senha: admin123

URL: http://localhost:8000
""")
        print(f"\n📄 Credenciais salvas em: {cred_file}")
    else:
        print("\n❌ ERRO ao criar banco de dados!")

def main():
    init_dirs()
    
    while True:
        print_banner()
        print("📌 MENU PRINCIPAL")
        print("═" * 40)
        print("  1. 📋 Listar clientes")
        print("  2. ➕ Criar novo cliente")
        print("  3. 🚪 Sair")
        print("═" * 40)
        
        opcao = input("\n👉 Escolha (1-3): ").strip()
        
        if opcao == "1":
            listar_clientes()
            input("\nPressione ENTER...")
        elif opcao == "2":
            criar_cliente()
            input("\nPressione ENTER...")
        elif opcao == "3":
            print("\n👋 Encerrando...\n")
            break
        else:
            print("\n❌ Opção inválida!")
            input("\nPressione ENTER...")

if __name__ == "__main__":
    main()