import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import json

# =============================================================================
# CONFIGURAÇÃO DA PÁGINA
# =============================================================================
st.set_page_config(
    page_title="Nexus PCM - Manutenção Industrial",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# INICIALIZAÇÃO DO SESSION STATE (PERSISTÊNCIA)
# =============================================================================
def init_session_state():
    """Inicializa todas as variáveis de estado"""
    if 'ativos' not in st.session_state:
        st.session_state.ativos = []
    if 'ordens' not in st.session_state:
        st.session_state.ordens = []
    if 'usuarios' not in st.session_state:
        st.session_state.usuarios = []
    if 'pagina_atual' not in st.session_state:
        st.session_state.pagina_atual = "Dashboard"

init_session_state()

# =============================================================================
# FUNÇÕES AUXILIARES (COM TRATAMENTO DE ERRO)
# =============================================================================
def try_request(url, method='GET', data=None):
    """Função segura para requisições - não quebra o layout"""
    try:
        if method == 'GET':
            response = requests.get(url, timeout=5)
        elif method == 'POST':
            response = requests.post(url, json=data, timeout=5)
        elif method == 'DELETE':
            response = requests.delete(url, timeout=5)
        else:
            return None
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Erro de conexão: {str(e)}")
        return None

# =============================================================================
# CSS PERSONALIZADO (MESMO ESTILO DO SEU HTML)
# =============================================================================
st.markdown("""
<style>
    /* Cores da marca */
    :root {
        --primary-blue: #2563EB;
        --secondary-blue: #60A5FA;
        --purple: #8B5CF6;
        --pink: #EC4899;
    }
    
    /* Cards */
    .stCard {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 20px;
        padding: 1.5rem;
        transition: all 0.3s;
    }
    .stCard:hover {
        transform: translateY(-4px);
        border-color: var(--primary-blue);
        box-shadow: 0 10px 25px -5px rgba(0,0,0,0.05);
    }
    
    /* Badges */
    .badge-green { background: #ECFDF5; color: #059669; padding: 4px 12px; border-radius: 20px; font-size: 12px; }
    .badge-blue { background: #EFF6FF; color: var(--primary-blue); padding: 4px 12px; border-radius: 20px; font-size: 12px; }
    .badge-red { background: #FEF2F2; color: #DC2626; padding: 4px 12px; border-radius: 20px; font-size: 12px; }
    .badge-yellow { background: #FEF3C7; color: #D97706; padding: 4px 12px; border-radius: 20px; font-size: 12px; }
    .badge-purple { background: #F3E8FF; color: var(--purple); padding: 4px 12px; border-radius: 20px; font-size: 12px; }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-blue), var(--purple));
        color: white;
        border: none;
        border-radius: 12px;
        padding: 8px 20px;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 10px 20px -5px rgba(37,99,235,0.3);
    }
    
    /* Títulos */
    .gradient-text {
        background: linear-gradient(135deg, var(--secondary-blue), var(--purple), var(--pink));
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }
    
    /* Tabelas */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #F8FAFC;
        border-right: 1px solid #E2E8F0;
    }
</style>
""", unsafe_allow_html=True)

# =============================================================================
# SIDEBAR - MENU PRINCIPAL
# =============================================================================
with st.sidebar:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 32px;">
        <div style="width: 40px; height: 40px; background: linear-gradient(135deg, #2563EB, #8B5CF6); border-radius: 12px; display: flex; align-items: center; justify-content: center;">
            <span style="color: white; font-size: 20px;">🔧</span>
        </div>
        <div>
            <h1 style="font-size: 24px; font-weight: bold; margin: 0;">NEXUS</h1>
            <p style="font-size: 10px; color: #60A5FA; margin: 0;">PCM - Manutenção</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Menu com ícones
    menu_options = {
        "Dashboard": "📊",
        "Ativos": "🏭",
        "Ordens Planejadas (Verde)": "📅",
        "Ordens Preventivas (Azul)": "🛡️",
        "Ordens Corretivas (Vermelha)": "⚠️",
        "RH / Usuários": "👥",
        "Tee Card": "🃏",
        "Calendário MP": "📆",
        "Falha de Equipamento": "🐛",
        "Indicadores (MTBF/MTTR)": "📈",
        "Relatórios": "📄"
    }
    
    for option, icon in menu_options.items():
        if st.button(f"{icon} {option}", key=option, use_container_width=True):
            st.session_state.pagina_atual = option
            st.rerun()
    
    st.markdown("---")
    st.caption("© 2024 Nexus PCM - R$ 397/mês")

# =============================================================================
# DASHBOARD PRINCIPAL
# =============================================================================
def dashboard():
    st.markdown('<h1 class="gradient-text">Dashboard</h1>', unsafe_allow_html=True)
    st.markdown("Visão geral do sistema de manutenção")
    
    # Buscar dados reais
    ativos = st.session_state.ativos
    ordens = st.session_state.ordens
    
    # Cards de métricas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="stCard" style="text-align: center;">
            <div style="font-size: 32px; font-weight: bold; color: #2563EB;">{len(ativos)}</div>
            <div style="color: #64748B;">Ativos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        abertas = len([o for o in ordens if not o.get('is_closed', False)])
        st.markdown(f"""
        <div class="stCard" style="text-align: center;">
            <div style="font-size: 32px; font-weight: bold; color: #D97706;">{abertas}</div>
            <div style="color: #64748B;">OS Abertas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        fechadas = len([o for o in ordens if o.get('is_closed', False)])
        st.markdown(f"""
        <div class="stCard" style="text-align: center;">
            <div style="font-size: 32px; font-weight: bold; color: #059669;">{fechadas}</div>
            <div style="color: #64748B;">OS Fechadas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stCard" style="text-align: center;">
            <div style="font-size: 32px; font-weight: bold; color: #7C3AED;">{len(st.session_state.usuarios)}</div>
            <div style="color: #64748B;">Usuários</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Últimos ativos
    st.markdown("---")
    st.subheader("📋 Últimos Ativos")
    
    if ativos:
        df = pd.DataFrame(ativos[-5:])
        df = df[['codigo', 'nome', 'tipo', 'localizacao']] if 'codigo' in df.columns else df
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum ativo cadastrado ainda. Use o menu 'Ativos' para começar.")

# =============================================================================
# ATIVOS (CRUD COMPLETO)
# =============================================================================
def ativos_page():
    st.markdown('<h1 class="gradient-text">Ativos</h1>', unsafe_allow_html=True)
    st.markdown("Gestão de ativos industriais")
    
    # Formulário de cadastro
    with st.expander("➕ Novo Ativo", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            codigo = st.text_input("Código", placeholder="Ex: MAQ-001")
            nome = st.text_input("Nome", placeholder="Ex: Prensa Hidráulica")
        with col2:
            tipo = st.selectbox("Tipo", ["equipment", "machine", "vehicle"])
            localizacao = st.text_input("Localização (APU)", placeholder="Ex: APU Pump - Cabecote")
        
        if st.button("💾 Salvar Ativo", use_container_width=True):
            if codigo and nome:
                novo = {
                    "id": len(st.session_state.ativos) + 1,
                    "codigo": codigo,
                    "nome": nome,
                    "tipo": tipo,
                    "localizacao": localizacao,
                    "status": "Ativo",
                    "horas_operacao": 0,
                    "falhas": 0,
                    "criado_em": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.ativos.append(novo)
                st.success(f"Ativo {codigo} criado com sucesso!")
                st.rerun()
            else:
                st.error("Preencha código e nome")
    
    # Lista de ativos
    st.markdown("---")
    st.subheader("📋 Lista de Ativos")
    
    if st.session_state.ativos:
        df = pd.DataFrame(st.session_state.ativos)
        
        # Configurar colunas para exibição
        colunas = ['codigo', 'nome', 'tipo', 'localizacao', 'status', 'horas_operacao', 'falhas']
        df_display = df[[c for c in colunas if c in df.columns]]
        
        # Botões de ação
        st.dataframe(df_display, use_container_width=True)
        
        # Botão de exclusão
        with st.expander("🗑️ Excluir Ativo"):
            codigo_excluir = st.selectbox("Selecione o código do ativo", [a['codigo'] for a in st.session_state.ativos])
            if st.button("Excluir", use_container_width=True):
                st.session_state.ativos = [a for a in st.session_state.ativos if a['codigo'] != codigo_excluir]
                st.success(f"Ativo {codigo_excluir} excluído")
                st.rerun()
    else:
        st.info("Nenhum ativo cadastrado")

# =============================================================================
# ORDENS DE SERVIÇO (GENÉRICO COM ABAS)
# =============================================================================
def ordens_page(tipo, cor, titulo):
    st.markdown(f'<h1 class="gradient-text">{titulo}</h1>', unsafe_allow_html=True)
    st.markdown(f"Ordens {cor}")
    
    # Filtrar ordens
    ordens_tipo = [o for o in st.session_state.ordens if o.get('tipo') == tipo]
    
    # Abas Abertas/Fechadas
    tab1, tab2 = st.tabs([f"📋 Abertas", f"✅ Fechadas"])
    
    with tab1:
        abertas = [o for o in ordens_tipo if not o.get('is_closed', False)]
        if abertas:
            df = pd.DataFrame(abertas)
            st.dataframe(df, use_container_width=True)
        else:
            st.info(f"Nenhuma ordem {tipo} aberta")
    
    with tab2:
        fechadas = [o for o in ordens_tipo if o.get('is_closed', False)]
        if fechadas:
            df = pd.DataFrame(fechadas)
            st.dataframe(df, use_container_width=True)
        else:
            st.info(f"Nenhuma ordem {tipo} fechada")
    
    # Formulário de nova OS
    with st.expander(f"➕ Nova OS {cor}", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            codigo = st.text_input("Código", placeholder=f"OS-{tipo[:3].upper()}-001")
            titulo_os = st.text_input("Título", placeholder="Ex: Manutenção preventiva")
        with col2:
            ativos_opcoes = [f"{a['codigo']} - {a['nome']}" for a in st.session_state.ativos]
            ativo_selecionado = st.selectbox("Ativo", ativos_opcoes)
            prioridade = st.selectbox("Prioridade", ["1 - Baixa", "2 - Normal", "3 - Média", "4 - Alta", "5 - Urgente"])
        
        descricao = st.text_area("Descrição", height=100)
        
        if st.button("💾 Criar OS", use_container_width=True):
            if codigo and titulo_os:
                ativo_id = st.session_state.ativos[ativos_opcoes.index(ativo_selecionado)]['id']
                nova = {
                    "id": len(st.session_state.ordens) + 1,
                    "codigo": codigo,
                    "titulo": titulo_os,
                    "tipo": tipo,
                    "asset_id": ativo_id,
                    "descricao": descricao,
                    "prioridade": prioridade,
                    "status": "Aberta",
                    "is_closed": False,
                    "criado_em": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.ordens.append(nova)
                st.success(f"OS {codigo} criada com sucesso!")
                st.rerun()
            else:
                st.error("Preencha código e título")

# =============================================================================
# RH / USUÁRIOS
# =============================================================================
def rh_usuarios():
    st.markdown('<h1 class="gradient-text">RH / Usuários</h1>', unsafe_allow_html=True)
    st.markdown("Gestão de manutentores, engenheiros e solicitantes")
    
    with st.expander("➕ Novo Usuário", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome Completo")
            email = st.text_input("E-mail")
        with col2:
            tipo = st.selectbox("Tipo", ["manutentor", "engenheiro", "solicitante", "admin"])
            senha = st.text_input("Senha", type="password", value="123456")
        
        if st.button("💾 Salvar Usuário", use_container_width=True):
            if nome and email:
                novo = {
                    "id": len(st.session_state.usuarios) + 1,
                    "nome": nome,
                    "email": email,
                    "tipo": tipo,
                    "ativo": True,
                    "criado_em": datetime.now().strftime("%Y-%m-%d %H:%M")
                }
                st.session_state.usuarios.append(novo)
                st.success(f"Usuário {nome} criado!")
                st.rerun()
            else:
                st.error("Preencha nome e e-mail")
    
    st.markdown("---")
    st.subheader("📋 Lista de Usuários")
    
    if st.session_state.usuarios:
        df = pd.DataFrame(st.session_state.usuarios)
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum usuário cadastrado")

# =============================================================================
# TEE CARD
# =============================================================================
def tee_card():
    st.markdown('<h1 class="gradient-text">Tee Card</h1>', unsafe_allow_html=True)
    st.markdown("Desempenho diário dos manutentores")
    
    visualizacao = st.radio("Visualização", ["Diária", "Semanal", "Mensal", "Anual"], horizontal=True)
    
    manutentores = [u for u in st.session_state.usuarios if u.get('tipo') == 'manutentor']
    
    if manutentores:
        for m in manutentores:
            with st.container():
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.write(f"**{m['nome']}**")
                with col2:
                    horas = st.number_input(f"Horas", key=f"horas_{m['id']}", min_value=0, step=1, label_visibility="collapsed")
                with col3:
                    st.button(f"Registrar", key=f"btn_{m['id']}")
                st.markdown("---")
    else:
        st.info("Nenhum manutentor cadastrado")

# =============================================================================
# CALENDÁRIO MP
# =============================================================================
def calendario_mp():
    st.markdown('<h1 class="gradient-text">Calendário MP</h1>', unsafe_allow_html=True)
    st.markdown("Manutenção Planejada")
    
    ordens_planejadas = [o for o in st.session_state.ordens if o.get('tipo') == 'planned']
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stCard" style="text-align: center;">
            <div style="font-size: 48px; font-weight: bold; color: #059669;">{len(ordens_planejadas)}</div>
            <div>MP's Pendentes</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stCard" style="text-align: center;">
            <div style="font-size: 48px; font-weight: bold; color: #2563EB;">{len([o for o in ordens_planejadas if o.get('is_closed')])}</div>
            <div>MP's Concluídas</div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# FALHA DE EQUIPAMENTO
# =============================================================================
def falha_equipamento():
    st.markdown('<h1 class="gradient-text">Falha de Equipamento</h1>', unsafe_allow_html=True)
    st.markdown("Registro de falhas e acompanhamento")
    
    falhas = [o for o in st.session_state.ordens if o.get('tipo') == 'corrective']
    abertas = [f for f in falhas if not f.get('is_closed', False)]
    fechadas = [f for f in falhas if f.get('is_closed', False)]
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stCard" style="text-align: center; border-left: 4px solid #DC2626;">
            <div style="font-size: 32px; font-weight: bold; color: #DC2626;">{len(abertas)}</div>
            <div>⚠️ Equipamentos em Falha</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stCard" style="text-align: center; border-left: 4px solid #059669;">
            <div style="font-size: 32px; font-weight: bold; color: #059669;">{len(fechadas)}</div>
            <div>✅ Falhas Finalizadas</div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# INDICADORES (MTBF/MTTR)
# =============================================================================
def indicadores():
    st.markdown('<h1 class="gradient-text">MTBF / MTTR</h1>', unsafe_allow_html=True)
    st.markdown("Indicadores de performance da manutenção")
    
    # Cálculo simulado
    total_horas = sum([a.get('horas_operacao', 0) for a in st.session_state.ativos])
    total_falhas = sum([a.get('falhas', 0) for a in st.session_state.ativos])
    
    mtbf = total_horas / total_falhas if total_falhas > 0 else 0
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="stCard" style="text-align: center;">
            <div style="font-size: 48px; font-weight: bold; color: #2563EB;">{mtbf:.0f}</div>
            <div>MTBF (horas entre falhas)</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stCard" style="text-align: center;">
            <div style="font-size: 48px; font-weight: bold; color: #7C3AED;">-</div>
            <div>MTTR (em desenvolvimento)</div>
        </div>
        """, unsafe_allow_html=True)

# =============================================================================
# RELATÓRIOS
# =============================================================================
def relatorios():
    st.markdown('<h1 class="gradient-text">Relatórios</h1>', unsafe_allow_html=True)
    st.markdown("Exportação de dados")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📊 Relatório de Ativos", use_container_width=True):
            if st.session_state.ativos:
                df = pd.DataFrame(st.session_state.ativos)
                st.download_button("Download CSV", df.to_csv(index=False), "ativos.csv", "text/csv")
            else:
                st.warning("Nenhum dado disponível")
    
    with col2:
        if st.button("📋 Relatório de OS", use_container_width=True):
            if st.session_state.ordens:
                df = pd.DataFrame(st.session_state.ordens)
                st.download_button("Download CSV", df.to_csv(index=False), "ordens.csv", "text/csv")
            else:
                st.warning("Nenhum dado disponível")

# =============================================================================
# ROTEAMENTO DAS PÁGINAS
# =============================================================================
pagina = st.session_state.pagina_atual

if pagina == "Dashboard":
    dashboard()
elif pagina == "Ativos":
    ativos_page()
elif pagina == "Ordens Planejadas (Verde)":
    ordens_page("planned", "Verde", "Ordens Planejadas (Verde)")
elif pagina == "Ordens Preventivas (Azul)":
    ordens_page("preventive", "Azul", "Ordens Preventivas (Azul)")
elif pagina == "Ordens Corretivas (Vermelha)":
    ordens_page("corrective", "Vermelha", "Ordens Corretivas (Vermelha)")
elif pagina == "RH / Usuários":
    rh_usuarios()
elif pagina == "Tee Card":
    tee_card()
elif pagina == "Calendário MP":
    calendario_mp()
elif pagina == "Falha de Equipamento":
    falha_equipamento()
elif pagina == "Indicadores (MTBF/MTTR)":
    indicadores()
elif pagina == "Relatórios":
    relatorios()
