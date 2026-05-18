import streamlit as st
import pandas as pd
import random
from datetime import datetime

# =============================================================================
# 1. CONFIGURAÇÃO INICIAL E SESSION STATE (PERSISTÊNCIA)
# =============================================================================

def inicializar_estado():
    """Inicializa todas as chaves do session_state se não existirem.
       Isso garante que os dados não sumam entre reruns."""
    
    # Dados principais (simulam o banco de dados)
    if "dados_ativos" not in st.session_state:
        # Fallback seguro: dados iniciais vazios ou exemplo
        st.session_state.dados_ativos = []
        # Exemplo opcional para teste visual:
        # st.session_state.dados_ativos = [
        #     {"id": 1, "codigo": "MAQ-001", "nome": "Prensa", "status": "Ativo"},
        #     {"id": 2, "codigo": "EST-002", "nome": "Esteira", "status": "Ativo"},
        # ]

    if "dados_os" not in st.session_state:
        st.session_state.dados_os = []

    if "mensagem_erro" not in st.session_state:
        st.session_state.mensagem_erro = None

# =============================================================================
# 2. FUNÇÕES SIMULADAS DE BACKEND (COM TRATAMENTO DE EXCEÇÕES)
# =============================================================================

def carregar_ativos():
    """Simula consulta ao banco - retorna lista de ativos (com fallback seguro)."""
    try:
        # Aqui entraria sua lógica real de BD: SELECT * FROM ativos
        # Exemplo com dados locais (troque pela sua consulta real)
        # Por enquanto, retorna o que está no session_state
        return st.session_state.dados_ativos
    except Exception as e:
        st.session_state.mensagem_erro = f"Erro ao carregar ativos: {str(e)}"
        return []  # Fallback: lista vazia evita quebra do layout

def salvar_ativo(novo_ativo):
    """Simula INSERT no banco e atualiza session_state."""
    try:
        # Validação básica
        if not novo_ativo.get("codigo") or not novo_ativo.get("nome"):
            raise ValueError("Código e nome são obrigatórios")
        
        # Geração de ID fictício (substitua pelo serial do BD)
        novo_id = random.randint(1000, 9999)
        novo_ativo["id"] = novo_id
        novo_ativo["data_criacao"] = datetime.now()
        
        # Adiciona ao estado (simula commit)
        st.session_state.dados_ativos.append(novo_ativo)
        
        # Aqui você chamaria seu banco real: INSERT INTO ativos...
        # Exemplo: db.insert("ativos", novo_ativo)
        
        return True, "Ativo salvo com sucesso!"
    except Exception as e:
        st.session_state.mensagem_erro = f"Erro ao salvar ativo: {str(e)}"
        return False, str(e)

# =============================================================================
# 3. FUNÇÃO QUE CONSTRÓI O HTML DINAMICAMENTE A PARTIR DO ESTADO
# =============================================================================

def gerar_html_tabs():
    """Monta o HTML inteiro usando os dados atuais do session_state.
       Essa função é chamada a cada rerun, mas não perde dados porque
       os dados estão salvos no estado."""
    
    # Carrega os dados mais recentes (do estado, ou do BD se quiser)
    ativos = carregar_ativos()
    
    # Gerar linhas da tabela de ativos dinamicamente (Loop Python → HTML)
    linhas_html = ""
    if ativos:
        for ativo in ativos:
            linhas_html += f"""
            <tr>
                <td>{ativo.get('codigo', '-')}</td>
                <td>{ativo.get('nome', '-')}</td>
                <td>{ativo.get('status', 'Ativo')}</td>
                <td><button class='btn-detalhe' onclick='alert("Em desenvolvimento")'>Detalhes</button></td>
            </tr>
            """
    else:
        linhas_html = "<tr><td colspan='3' style='text-align:center'>Nenhum ativo cadastrado</td></tr>"
    
    # HTML completo (com as mesmas classes/estilos que você já tem)
    html_completo = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{ font-family: 'Inter', sans-serif; background: #FFFFFF; }}
            .card {{ background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 20px; padding: 1.5rem; }}
            .btn-primary {{ background: linear-gradient(135deg, #2563EB, #8B5CF6); color: white; padding: 8px 20px; border-radius: 12px; border: none; cursor: pointer; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #E2E8F0; }}
            th {{ color: #64748B; font-weight: 500; }}
            .tabs-container {{ margin-bottom: 20px; }}
            .tab-btn {{ padding: 10px 20px; background: #F1F5F9; border: none; cursor: pointer; margin-right: 5px; border-radius: 10px; }}
            .tab-btn.active {{ background: #2563EB; color: white; }}
            .tab-content {{ display: none; }}
            .tab-content.active {{ display: block; }}
            .toast {{ position: fixed; bottom: 20px; right: 20px; background: #1E293B; color: white; padding: 12px 20px; border-radius: 8px; z-index: 1000; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2 style="font-size:1.5rem; margin-bottom:1rem;">📋 Ativos Cadastrados</h2>
            <table>
                <thead>
                    <tr><th>Código</th><th>Nome</th><th>Status</th><th>Ações</th></tr>
                </thead>
                <tbody>
                    {linhas_html}
                </tbody>
            </table>
            <div style="margin-top: 1rem;">
                <button onclick="parent.postMessage({{type: 'abrirModal'}}, '*')" class="btn-primary">+ Novo Ativo</button>
            </div>
        </div>

        <script>
            // Exemplo de comunicação com Streamlit via JavaScript
            window.addEventListener('message', (event) => {{
                if (event.data.type === 'abrirModal') {{
                    // Aqui você poderia chamar Streamlit.setComponentValue
                    console.log('Abrir modal solicitado pelo HTML');
                }}
            }});
        </script>
    </body>
    </html>
    """
    return html_completo

# =============================================================================
# 4. FUNÇÃO DE RENDERIZAÇÃO DO COMPONENTE (SUBSTITUI O HTML ESTÁTICO)
# =============================================================================

def renderizar_html():
    """Renderiza o componente HTML com os dados mais recentes do estado."""
    html = gerar_html_tabs()
    st.components.v1.html(html, height=400, scrolling=True)

# =============================================================================
# 5. FUNÇÃO PARA TRATAR O FORMULÁRIO DE CADASTRO (COM st.form)
# =============================================================================

def formulario_novo_ativo():
    """Exibe formulário Streamlit para adicionar novo ativo.
       Este formulário fica fora do HTML, pois o Streamlit gerencia o estado melhor assim."""
    with st.form("form_novo_ativo"):
        col1, col2 = st.columns(2)
        with col1:
            codigo = st.text_input("Código do Ativo *", placeholder="Ex: MAQ-001")
        with col2:
            nome = st.text_input("Nome do Ativo *", placeholder="Ex: Prensa Hidráulica")
        
        status = st.selectbox("Status", ["Ativo", "Em Manutenção", "Inativo"])
        submitted = st.form_submit_button("💾 Salvar Ativo", use_container_width=True)
        
        if submitted:
            if not codigo or not nome:
                st.error("Preencha código e nome do ativo")
                return
            
            novo = {"codigo": codigo, "nome": nome, "status": status}
            sucesso, msg = salvar_ativo(novo)
            if sucesso:
                st.success(msg)
                st.rerun()  # Força o rerun para atualizar o HTML
            else:
                st.error(msg)

# =============================================================================
# 6. FUNÇÃO PRINCIPAL (LAYOUT DO STREAMLIT)
# =============================================================================

def main():
    # Inicializa o estado da aplicação (só roda uma vez)
    inicializar_estado()
    
    # Exibe mensagem de erro global, se houver (sem quebrar layout)
    if st.session_state.mensagem_erro:
        st.error(st.session_state.mensagem_erro)
        st.session_state.mensagem_erro = None  # limpa após exibir
    
    # Cria abas nativas do Streamlit (opcional, mas evita perder estado)
    tab1, tab2 = st.tabs(["📊 Dashboard", "➕ Adicionar Ativo"])
    
    with tab1:
        # Renderiza o HTML dinâmico (sempre usando dados do session_state)
        renderizar_html()
    
    with tab2:
        formulario_novo_ativo()

# =============================================================================
# 7. PONTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    main()
