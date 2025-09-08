import streamlit as st
import sqlite3

# ========================
# Conexão com o banco de usuários
# ========================
def init_user_db():
    conn = sqlite3.connect("usuarios.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            senha TEXT NOT NULL
        )
    ''')
    conn.commit()
    return conn, cursor

# ========================
# Funções de autenticação
# ========================
def autenticar(cursor, usuario, senha):
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
    return cursor.fetchone()

def registrar_usuario(cursor, conn, usuario, senha):
    try:
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha))
        conn.commit()
        return True
    except:
        return False

# ========================
# Tela de login/registro
# ========================
def login_screen():
    st.title("🔑 Login - MK5STORE")

    tab_login, tab_register = st.tabs(["Entrar", "Registrar"])

    # Aba de Login
    with tab_login:
        usuario = st.text_input("Usuário")
        senha = st.text_input("Senha", type="password")
        if st.button("Entrar"):
            if autenticar(cursor, usuario, senha):
                st.session_state["logado"] = True
                st.session_state["usuario"] = usuario
                st.success(f"✅ Bem-vindo, {usuario}!")
                st.rerun()
            else:
                st.error("⚠️ Usuário ou senha inválidos.")

    # Aba de Registro
    with tab_register:
        novo_usuario = st.text_input("Novo Usuário")
        nova_senha = st.text_input("Nova Senha", type="password")
        if st.button("Registrar"):
            if registrar_usuario(cursor, conn, novo_usuario, nova_senha):
                st.success("✅ Usuário registrado! Agora faça login.")
            else:
                st.error("⚠️ Usuário já existe.")

# ========================
# Inicialização
# ========================
conn, cursor = init_user_db()

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    login_screen()
else:
    st.sidebar.success(f"👋 Olá, {st.session_state['usuario']}")
    if st.sidebar.button("🚪 Logout"):
        st.session_state["logado"] = False
        st.rerun()

    # Aqui entra o que só aparece depois do login
    st.title("🛒 MK5STORE")
    st.write("Agora você pode acessar o sistema!")
