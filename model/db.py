import sqlite3
from flask import g

#abre o banco de dados
def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect("model/dados.db", \
        detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
    return g.db

#fecha o banco de dados
def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

#busca um usuário pelo login
def busca_usuario(login):
    con = get_db()
    return con.execute("SELECT * FROM usuario WHERE login = ?",[login]).fetchone()

# Cadastra um usuário no banco
def cadastra_usuario(login, senha, nome):
    con = get_db()
    con.execute("INSERT INTO usuario VALUES(NULL, ?, ?, ?)", \
    [login, senha, nome])
    con.commit()

# Altera o nome de um usuário
def altera_nome(login, nome):
    con = get_db()
    con.execute("UPDATE usuario SET nome = ? WHERE login = ?",[nome, login])
    con.commit()
    
# Altera a senha de um usuário
def altera_senha(login, senha):
    con = get_db()
    con.execute("UPDATE usuario SET senha = ? WHERE login = ?",[senha, login])
    con.commit()

def adiciona_token(login, token):
    con = get_db()
    usuario = con.execute("SELECT id FROM usuario WHERE login = ?",
    [login]).fetchone()
    con.execute("INSERT INTO tokens VALUES(NULL, ?, ?)",
    [usuario['id'], token])
    con.commit()    

def verifica_token(token):
    con = get_db()
    dados = con.execute("SELECT * FROM tokens WHERE token = ?",[token]).fetchone()
    if (dados != None):
        return con.execute("SELECT * FROM usuario WHERE id = ?",[dados['id_usuario']]).fetchone()
    else:
        return None

def remove_token(token):
    con = get_db()
    con.execute("DELETE FROM tokens WHERE token = ?", [token])
    con.commit()
    return None 

def posta_mensagem(id_user, trend):
    con = get_db()
    con.execute("INSERT INTO postagem (id_user,corpo) VALUES(? , ?)",[id_user, trend])
    con.commit()

def listar_mensagem(id_user):
    con = get_db()
    return con.execute("SELECT * FROM postagem WHERE id_user = ?",[id_user]).fetchall()


