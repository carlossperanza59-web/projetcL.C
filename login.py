import streamlit as st
import sqlite3
import pandas as pd


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


def init_estoque_db():
    conn = sqlite3.connect("estoque.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produtos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            quantidade INTEGER NOT NULL,
            preco REAL NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vendas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id INTEGER,
            quantidade INTEGER,
            total REAL,
            FOREIGN KEY(produto_id) REFERENCES produtos(id)
        )
    ''')
    conn.commit()
    return conn, cursor


def autenticar(cursor, usuario, senha):
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
    return cursor.fetchone()

def registrar_usuario(cursor, conn, usuario, senha):
    try:
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", (usuario, senha))
        conn.commit()
        with open("usuarios.txt", "a", encoding="utf-8") as f:
            f.write(f"Usuário: {usuario} | Senha: {senha}\n")
        return True
    except:
        return False

def login_screen():
    st.title("🔑 Login - Barcaroli Vet")

    tab_login, tab_register = st.tabs(["Entrar", "Registrar"])

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

    with tab_register:
        novo_usuario = st.text_input("Novo Usuário")
        nova_senha = st.text_input("Nova Senha", type="password")
        if st.button("Registrar"):
            if registrar_usuario(cursor, conn, novo_usuario, nova_senha):
                st.success("✅ Usuário registrado! Agora faça login.")
            else:
                st.error("⚠️ Usuário já existe.")


def tela_inicio():
    st.markdown(
        """
        <h1 style='text-align: center;'>🐾 Barcaroli Vet</h1>
        <h3 style='text-align: center; color: gray;'>Sistema de Controle de Estoque</h3>
        <div style='text-align: center; font-size:16px; margin-top:10px;'>
            Agora você pode acessar o sistema!
        </div>
        """,
        unsafe_allow_html=True
    )

def tela_cadastro_produto():
    st.subheader("➕ Cadastro de Produtos")
    nome = st.text_input("Nome do Produto")
    quantidade = st.number_input("Quantidade", min_value=1, step=1)
    preco = st.number_input("Preço (R$)", min_value=0.0, step=0.01)

    if st.button("Adicionar Produto"):
        if nome.strip() != "":
            cursor_estoque.execute(
                "INSERT INTO produtos (nome, quantidade, preco) VALUES (?, ?, ?)", 
                (nome, quantidade, preco)
            )
            conn_estoque.commit()
            st.success(f"✅ Produto '{nome}' adicionado ao estoque!")
        else:
            st.error("⚠️ O nome do produto não pode estar vazio.")

def tela_listar_produtos():
    st.markdown("<h3 style='text-align: center;'>📋 Produtos em Estoque</h3>", unsafe_allow_html=True)

    cursor_estoque.execute("SELECT nome, quantidade, preco FROM produtos")
    produtos = cursor_estoque.fetchall()

    if produtos:
        df = pd.DataFrame(produtos, columns=["Produto", "Quantidade", "Preço (R$)"])
        st.dataframe(
            df.style.set_properties(**{'text-align': 'center'}).format({"Preço (R$)": "R${:,.2f}"}),
            use_container_width=True,
            height=350
        )
    else:
        st.info("Nenhum produto cadastrado ainda.")

def tela_vendas():
    st.subheader("💰 Registrar Venda")

    cursor_estoque.execute("SELECT id, nome, quantidade, preco FROM produtos")
    produtos = cursor_estoque.fetchall()

    if not produtos:
        st.warning("⚠️ Nenhum produto cadastrado para vender.")
        return

    opcoes = {f"{p[1]} (Estoque: {p[2]}) - R${p[3]:.2f}": p for p in produtos}
    escolha = st.selectbox("Selecione o Produto", list(opcoes.keys()))
    produto = opcoes[escolha]

    qtd_venda = st.number_input("Quantidade Vendida", min_value=1, step=1)

    if st.button("Confirmar Venda"):
        if qtd_venda > produto[2]:
            st.error("⚠️ Estoque insuficiente para esta venda.")
        else:
            novo_estoque = produto[2] - qtd_venda
            total = qtd_venda * produto[3]

            cursor_estoque.execute("UPDATE produtos SET quantidade = ? WHERE id = ?", (novo_estoque, produto[0]))
            cursor_estoque.execute("INSERT INTO vendas (produto_id, quantidade, total) VALUES (?, ?, ?)",
                                   (produto[0], qtd_venda, total))
            conn_estoque.commit()

            st.success(f"✅ Venda registrada: {qtd_venda}x {produto[1]} | Total R${total:.2f}")

    st.divider()
    st.subheader("📊 Histórico de Vendas")

    cursor_estoque.execute("""
        SELECT produtos.nome, vendas.quantidade, vendas.total
        FROM vendas
        JOIN produtos ON vendas.produto_id = produtos.id
    """)
    vendas = cursor_estoque.fetchall()

    if vendas:
        df_vendas = pd.DataFrame(vendas, columns=["Produto", "Quantidade", "Total (R$)"])
        st.dataframe(
            df_vendas.style.set_properties(**{'text-align': 'center'}).format({"Total (R$)": "R${:,.2f}"}),
            use_container_width=True,
            height=350
        )
    else:
        st.info("Nenhuma venda registrada ainda.")


conn, cursor = init_user_db()
conn_estoque, cursor_estoque = init_estoque_db()

if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:
    login_screen()
else:
    st.sidebar.title(f"👋 Olá, {st.session_state['usuario']}")
    menu = st.sidebar.radio("Navegação", ["🏠 Início", "➕ Cadastrar Produto", "📦 Produtos", "💰 Vendas"])
    if st.sidebar.button("🐾 Finalizar Sessão"):
        st.session_state["logado"] = False
        st.rerun()

    if menu == "🏠 Início":
        tela_inicio()
    elif menu == "➕ Cadastrar Produto":
        tela_cadastro_produto()
    elif menu == "📦 Produtos":
        tela_listar_produtos()
    elif menu == "💰 Vendas":
        tela_vendas()
