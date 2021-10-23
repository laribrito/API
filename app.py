from flask import Flask, redirect, url_for, session, request, render_template
from model import db
from passlib.hash import sha256_crypt
import os
from flask import jsonify
from flask_restful import Api
from classes.CADASTRO import Cadastrar




app = Flask(__name__)
api = Api(app)
api.add_resource(Cadastrar, '/api/cadastro')

app.secret_key = b'jhdakjrtyfuygiuhijebson145shsOhkhhujk666'
@app.route("/")
def index():
    if "usuario" in session: #Verifica se "usuario" existe na sessão
        return render_template("PAGINAINICIAL.html", logado=session["usuario"])
    else:
        return render_template("LOGIN.html")

@app.route("/autenticacao/", methods=["POST"])
def autenticacao():
    usuario = db.busca_usuario(request.form["login"])
    if usuario == None:
        return render_template("LOGIN.html", erro="Erro de autenticação")
    elif sha256_crypt.verify(request.form["senha"], usuario["senha"]): #testa com uma função do hash se a senha está correta
        session["usuario"] = request.form["login"]
        session["nome"] = usuario["nome"]
        return redirect(url_for("index"))
    else:
        return render_template("LOGIN.html", erro="Erro de autenticação")
    
@app.route("/cadastro/", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        if request.form["senha1"] == request.form["senha2"]: #confima se as senhas digitadas são iguais
            senha_hash = sha256_crypt.hash(request.form["senha1"]) #efetua o hash na senha
            db.cadastra_usuario(request.form["login"], \
            senha_hash, request.form["nome"])
            return render_template("LOGIN.html", mensagem="Usuário cadastrado")
        else:
            return render_template("CADASTRO.html", erro="As senhas não coincidem")
    else:
        return render_template("CADASTRO.html")

@app.route("/perfil/<nome>")
@app.route("/perfil")
def perfil(nome=None):
    if nome == session["usuario"] or not nome:
        user = db.busca_usuario(session["usuario"])
        return render_template("PERFIL.html", user=user, logado=session["usuario"], usuario=True)
    else:
        user = db.busca_usuario(nome)
        return render_template("PERFIL.html", user=user, logado=session["usuario"], usuario=False)

@app.route("/perfil/edicao",methods = ['get'])
def edicao():
    user = db.busca_usuario(session['usuario'])
    return render_template("EDICAO.html", logado=session["usuario"],user = user)

@app.route("/perfil/editar_nome", methods=["post"])
def editar_nome():
    db.altera_nome(session["usuario"], request.form["nome"])
    user = db.busca_usuario(session["usuario"])
    return render_template("PERFIL.html", user=user, logado=session["usuario"], usuario=True, mensagem="Nome editado com sucesso")

@app.route("/perfil/editar_senha", methods=["post"])
def editar_senha():
    if request.form["senha1"] == request.form["senha2"]: #confima se as senhas digitadas são iguais
        senha_hash = sha256_crypt.hash(request.form["senha1"])
        db.altera_senha(session["usuario"], senha_hash) #efetua o hash na senha
        user = db.busca_usuario(session["usuario"])
        return render_template("PERFIL.html", user=user, logado=session["usuario"], usuario=True, mensagem="Senha alterada com sucesso")
    else:
        user = db.busca_usuario(session['usuario'])
        return render_template("EDICAO.html", logado=session["usuario"],user = user, erro="As senhas não coincidem")

# Pasta com as imagens
app.config['PERFIL_FOLDER'] = 'static/imagens/perfil'
@app.route('/perfil/avatar/<login>')
def perfil_avatar(login):
    # Verifica se o arquivo existe
    if os.path.isfile(f"{app.config['PERFIL_FOLDER']}/{login}"):
        return redirect(f"/{app.config['PERFIL_FOLDER']}/{login}")
    # Se não, exibe o avatar padrão
    else:
        return redirect("/static/imagens/padrao.png")

@app.route('/perfil/foto', methods=["POST"])
def perfil_foto():
    if "foto" not in request.files:
        user = db.busca_usuario(session["usuario"])
        return render_template("PERFIL.html", user=user, logado=session["usuario"], usuario=True, erro="Nenhum arquivo enviado")
    arquivo = request.files["foto"]
    if arquivo.filename == '':
        user = db.busca_usuario(session["usuario"])
        return render_template("PERFIL.html", user=user, logado=session["usuario"], usuario=True, erro="Nenhum arquivo selecionado")
    if arquivo_permitido(arquivo.filename):
        arquivo.save(os.path.join(app.config['PERFIL_FOLDER'],
        session["usuario"]))
        user = db.busca_usuario(session["usuario"])
        return render_template("PERFIL.html", user=user, logado=session["usuario"], usuario=True, mensagem="Foto de perfil alterada com sucesso")

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def arquivo_permitido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/sair") #Remove "usuario" da sessão
def sair():
    del(session["usuario"])
    del(session["nome"])
    return redirect(url_for("index"))
 

@app.route('/api/teste', methods=["POST"])
def CAD_POST():
    resposta = {}
        
    resposta1 = "A aplicação gravou seu nome e sua idade."
    resposta2 = "Faltam alguns dados." 
    resposta3 = 'Cadastro efetuado.'
    resposta4 = 'As senhas não coincidem.'
    
    try: 
        nome = request.form['nome']
        login = request.form['login']
        senha1 = request.form['senha1']
        senha2 = request.form['senha2']
        
        if nome and login and senha1 and senha2 != None:
            if request.form["senha1"] == request.form["senha2"]:
                senha_hash = sha256_crypt.hash(request.form["senha1"])
                db.cadastra_usuario(request.form["login"],
                request.form["nome"],
                request.form["senha1"],
                request.form["senha2"],
                )        
                return jsonify(resposta3)            
            else:
                return jsonify(resposta4)                                   
    except KeyError: 
        return(resposta2)

@app.route('/api/login',methods=['GET'])
def login():
    resposta1 = "Login Efetuado com sucesso!"
    resposta2 = 'Senha Inválida, tente novamente.'
    resposta3 = 'Senha ou Login Inválidos, tente novamente.'
    resposta4 = 'Usuário não cadastrado, cadastre-se agora.'
    resposta5 = 'Preencha os campos de login e senha para entrar no site.'

    login = request.form['login']
    senha1 = request.form['senha1']
                   
    try:
        if login and senha1 != None:
            db.busca_usuario(request.form['login']) 
            return(resposta1) 

        elif login or senha1 == None:
            return(resposta5)   
    except:
        pass