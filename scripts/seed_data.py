import asyncio
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.asset import Asset
from app.models.work_order import WorkOrder
from uuid import uuid4
from datetime import datetime, timedelta

async def seed_database():
    print("🌱 Inserindo dados de exemplo...")
    
    async with AsyncSessionLocal() as db:
        company_id = str(uuid4())
        
        # 1. Criar usuários
        print("📝 Criando usuários...")
        
        users = [
            User(
                id=str(uuid4()),
                company_id=company_id,
                email="admin@industria.com",
                username="admin",
                full_name="Administrador",
                hashed_password=get_password_hash("admin123"),
                is_superuser=True,
                role="admin",
                user_type="admin"
            ),
            User(
                id=str(uuid4()),
                company_id=company_id,
                email="joao.silva@industria.com",
                username="joao.silva",
                full_name="João Silva",
                hashed_password=get_password_hash("123456"),
                user_type="manutentor",
                specialty="Elétrica",
                hourly_rate=45.0,
                phone="(11) 99999-1111"
            ),
            User(
                id=str(uuid4()),
                company_id=company_id,
                email="maria.santos@industria.com",
                username="maria.santos",
                full_name="Maria Santos",
                hashed_password=get_password_hash("123456"),
                user_type="manutentor",
                specialty="Mecânica",
                hourly_rate=50.0,
                phone="(11) 99999-2222"
            ),
            User(
                id=str(uuid4()),
                company_id=company_id,
                email="carlos.pereira@industria.com",
                username="carlos.pereira",
                full_name="Carlos Pereira",
                hashed_password=get_password_hash("123456"),
                user_type="engenheiro",
                department="Engenharia",
                phone="(11) 99999-3333"
            ),
            User(
                id=str(uuid4()),
                company_id=company_id,
                email="solicitante@industria.com",
                username="solicitante",
                full_name="Solicitante Geral",
                hashed_password=get_password_hash("123456"),
                user_type="solicitante",
                department="Produção"
            ),
        ]
        
        for user in users:
            db.add(user)
        
        await db.commit()
        
        # Buscar IDs dos usuários
        manutentor_ids = [u.id for u in users if u.user_type == "manutentor"]
        engenheiro_ids = [u.id for u in users if u.user_type == "engenheiro"]
        solicitante_ids = [u.id for u in users if u.user_type == "solicitante"]
        
        # 2. Criar Ativos (hierarquia)
        print("🏭 Criando ativos...")
        
        # Ativos principais
        assets = [
            Asset(
                id=str(uuid4()),
                company_id=company_id,
                code="PRENSA-001",
                name="Prensa Hidráulica 500T",
                asset_type="equipment",
                manufacturer="Bosch",
                model="PH-5000",
                location="APU Pump - Cabecote",
                department="Produção",
                installation_date=datetime(2022, 3, 15),
                total_operating_hours=3420,
                failure_count=3,
                critical_level=5,
                status="active"
            ),
            Asset(
                id=str(uuid4()),
                company_id=company_id,
                code="ESTEIRA-002",
                name="Esteira Transportadora",
                asset_type="machine",
                manufacturer="Siemens",
                model="ET-1000",
                location="APU Pump - Montagem",
                department="Logística",
                installation_date=datetime(2023, 1, 10),
                total_operating_hours=1850,
                failure_count=1,
                critical_level=3,
                status="active"
            ),
            Asset(
                id=str(uuid4()),
                company_id=company_id,
                code="COMPRESSOR-003",
                name="Compressor de Ar",
                asset_type="equipment",
                manufacturer="Atlas Copco",
                model="GA-30",
                location="APU Pump - Teste",
                department="Utilidades",
                installation_date=datetime(2021, 8, 20),
                total_operating_hours=5200,
                failure_count=5,
                critical_level=4,
                status="active"
            ),
            Asset(
                id=str(uuid4()),
                company_id=company_id,
                code="CALDEIRA-004",
                name="Caldeira Industrial",
                asset_type="equipment",
                manufacturer="Foster Wheeler",
                model="CW-200",
                location="APU Pump - Acabamento",
                department="Utilidades",
                installation_date=datetime(2020, 5, 10),
                total_operating_hours=6800,
                failure_count=2,
                critical_level=5,
                status="maintenance"
            ),
            Asset(
                id=str(uuid4()),
                company_id=company_id,
                code="INJETORA-005",
                name="Injetora Plástica",
                asset_type="machine",
                manufacturer="Arburg",
                model="ALLROUNDER",
                location="Alumínio - Setor A",
                department="Produção",
                installation_date=datetime(2023, 6, 1),
                total_operating_hours=920,
                failure_count=0,
                critical_level=3,
                status="active"
            ),
        ]
        
        for asset in assets:
            db.add(asset)
        
        await db.commit()
        
        asset_ids = [a.id for a in assets]
        
        # 3. Criar Ordens de Serviço
        print("📋 Criando ordens de serviço...")
        
        work_orders = []
        
        # Ordens Planejadas (Verde)
        for i in range(1, 4):
            wo = WorkOrder(
                id=str(uuid4()),
                company_id=company_id,
                asset_id=asset_ids[i % len(asset_ids)],
                code=f"PLN-2024-{i:03d}",
                title=f"Manutenção Planejada - {['Revisão','Lubrificação','Calibração'][i-1]}",
                description="Manutenção programada conforme plano anual",
                order_type="planned",
                color_code="verde",
                priority=2,
                requested_by=solicitante_ids[0] if solicitante_ids else None,
                scheduled_date=datetime.now() + timedelta(days=i*7),
                planned_hours=4.0,
                status="opened" if i < 3 else "in_progress",
                is_closed=False
            )
            work_orders.append(wo)
        
        # Ordens Preventivas (Azul)
        for i in range(1, 4):
            wo = WorkOrder(
                id=str(uuid4()),
                company_id=company_id,
                asset_id=asset_ids[i % len(asset_ids)],
                code=f"PRV-2024-{i:03d}",
                title=f"Preventiva - {['Troca de Óleo','Filtragem','Alinhamento'][i-1]}",
                description="Manutenção preventiva conforme periodicidade",
                order_type="preventive",
                color_code="azul",
                priority=3,
                requested_by=solicitante_ids[0] if solicitante_ids else None,
                scheduled_date=datetime.now() + timedelta(days=i*3),
                planned_hours=6.0,
                status="opened",
                is_closed=False
            )
            work_orders.append(wo)
        
        # Ordens Corretivas (Vermelha) - algumas já fechadas
        corrective_data = [
            ("COR-2024-001", "Falha na Prensa Hidráulica", "Vazamento de óleo na junta", 5, 8.5, True),
            ("COR-2024-002", "Esteira parou", "Motor superaquecendo", 4, 3.0, True),
            ("COR-2024-003", "Compressor com ruído", "Rolamento desgastado", 4, 0, False),
            ("COR-2024-004", "Caldeira pressão baixa", "Queimador sujo", 3, 0, False),
        ]
        
        for code, title, problem, priority, hours, is_closed in corrective_data:
            wo = WorkOrder(
                id=str(uuid4()),
                company_id=company_id,
                asset_id=asset_ids[abs(hash(code)) % len(asset_ids)],
                code=code,
                title=title,
                description=problem,
                order_type="corrective",
                color_code="vermelha",
                priority=priority,
                requested_by=solicitante_ids[0] if solicitante_ids else None,
                requested_date=datetime.now() - timedelta(days=5),
                reported_problem=problem,
                actual_hours=hours,
                status="completed" if is_closed else "opened",
                is_closed=is_closed,
                closed_at=datetime.now() - timedelta(days=2) if is_closed else None,
                solution_applied="Substituído componente" if is_closed else None,
                downtime_hours=hours
            )
            work_orders.append(wo)
        
        for wo in work_orders:
            db.add(wo)
        
        await db.commit()
        
        print("\n" + "="*60)
        print("✅ DADOS DE EXEMPLO INSERIDOS COM SUCESSO!")
        print("="*60)
        print(f"\n📊 RESUMO:")
        print(f"   👥 Usuários: {len(users)}")
        print(f"   🏭 Ativos: {len(assets)}")
        print(f"   📋 Ordens de Serviço: {len(work_orders)}")
        print(f"      - Planejadas (Verde): 3")
        print(f"      - Preventivas (Azul): 3")
        print(f"      - Corretivas (Vermelha): 4")
        print("\n🔑 ACESSO:")
        print(f"   Admin: admin@industria.com / admin123")
        print(f"   Manutentores: joao.silva / 123456")
        print(f"   Engenheiro: carlos.pereira / 123456")
        print(f"   Solicitante: solicitante / 123456")
        print("\n🌐 ACESSE: https://seu-servico.onrender.com")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(seed_database())