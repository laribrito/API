from re import I
from flask import Flask, redirect, url_for, session, request, render_template
from model import db
from passlib.hash import sha256_crypt
import os
from flask import jsonify
from classes.CADASTRO import Cadastrar
import secrets
from passlib.context import CryptPolicy
from classeToken import Token

app = Flask(__name__)

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
            db.cadastra_usuario(request.form["login"], senha_hash, request.form["nome"])
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
 

##########################################API##################################################################################################################

@app.route('/api/cadastro', methods=["POST"])
def CAD_POST():
    
    try: 
        nome = request.form['nome']
        login = request.form['login']
        senha1 = request.form['senha1']
        senha2 = request.form['senha2']
        
        if nome or login or senha1 or senha2 != "":
            if request.form["senha1"] == request.form["senha2"]:
                senha_hash = sha256_crypt.hash(request.form["senha1"])
                db.cadastra_usuario(request.form["login"], senha_hash, request.form["nome"])
                return jsonify({"status": 0, "msg": 'Cadastro efetuado.'})            
        
            else:
                return jsonify({"status": 2, "msg": 'As senhas não coincidem.'})  
        else:
            return jsonify({'status': 2, 'msg': 'Faltam campos a serem preenchidos.'})                                         
    
    except KeyError: 
        return jsonify({"status": 1, "msg": "Faltam alguns dados."})

@app.route('/api/login',methods=['POST'])
def login():
    try:             
        usuario = db.busca_usuario(request.form["login"])
        senha1 = request.form['senha1']
        login = request.form['login']
        
        if login or senha1 != "":
            if usuario == None:
                return jsonify({"status": 2, 'msg': 'Falha na Autenticação.'})
    
            if sha256_crypt.verify(senha1, usuario["senha"]):
                token = secrets.token_hex(128)
                db.adiciona_token(login, token)
                return {'status': 0, 'token': token}
            
            else:
                return jsonify({'status': 1, 'msg': 'Falha de autenticação.'})
            
        else:
            return jsonify({'status': 2, 'msg': 'Faltam campos a serem preenchidos.'})   
   
    except KeyError:
        return jsonify({'status': 1, 'msg': "Faltam alguns dados." })

@app.route("/api/perfil/<login>", methods=["GET"])
def retornaPerfil(login):
    #Captura o token que vem do Header
    auth = request.headers.get('Authorization')
    #Testa se tem algum usuario cadastrado com esse token
    usuario = Token.retorna_usuario(auth)
    if (usuario == None):
        #ERRO: Não tem esse token no banco de dados
        return {'status': -1, 'msg': 'Token inválido.'}
    ##########################################################################
    
    #Busca pelo usuario
    perfil = db.busca_usuario(login)

    if (perfil == None):
        #ERRO: Não tem usuario cadastrado
        return {'status': 1, 'msg': 'Perfil não encontrado.'}
    else:
        #SUCESSO
        return {'status': 0, 'login': login, 'nome': usuario['nome']}

@app.route('/api/editarsenha', methods = ['POST'])
def edit_senha():
    
    try: 
        login = db.busca_usuario(request.form["login"])
        senha = db.busca_usuario(request.form['senha1'])
        senha1 = request.form['senha1']
        senha2 = request.form['senha2']
        auth = request.headers.get('Authorization')    
        usuario = Token.retorna_usuario(auth)
        print(usuario)
        if (login and senha1 and senha2) != "":
            if (usuario == None):
                #ERRO: Não tem esse token no banco de dados
                    return {'status': -1, 'msg': 'Token inválido.'}                    
                
            if request.form['senha1'] == request.form['senha2']:                                         
                senha_hash = sha256_crypt.hash(request.form["senha1"])
                db.altera_senha(usuario['login'], senha_hash) #efetua o hash na senha
                return jsonify({'status': 0, 'msg': 'Senha Alterada.'})

            else:
                return {'status': 0, 'msg': 'Senhas não coincidem.'}                  
                                                  
        else:
            return jsonify({'status': -1, 'msg': 'Há campos a serem preenchidos.'})
    except KeyError: 
        return jsonify({"status": 1, "msg": "Faltam alguns dados."})


@app.route('/api/editarnome', methods =["POST"])        
def edit_nome():
    try:
        auth = request.headers.get('Authorization')
        nome = request.form['nome']
        login = db.busca_usuario(request.form['login'])
        auth = request.headers.get('Authorization')    
        usuario = Token.retorna_usuario(auth)
                  
        if nome and login != "": 
            if (login != None):                                                                                                               
                db.altera_nome(request.form['login'],request.form['nome'])
                return jsonify({'status': 0, 'msg': 'Nome alterado'})               
            if (usuario == None):
            #ERRO: Não tem esse token no banco de dados
                return {'status': -1, 'msg': 'Token inválido.'}
            else:
                return jsonify({'status':1, 'msg': 'Usuário Não cadastrado.',})                

        else:
            return jsonify({'status': 2, 'msg': 'Há campos a serem preenchidos. '})
        
    except KeyError:
        return jsonify({'status': 1, 'msg': 'Erro de auteticação'})


@app.route('/api/foto/<login>', methods = ['GET', "POST"])
def retorna_foto(login):
    if request.method == "GET":
        #Captura o token que vem do Header
        auth = request.headers.get('Authorization')
        #Testa se tem algum usuario cadastrado com esse token
        usuario = Token.retorna_usuario(auth)
        if (usuario == None):
            #ERRO: Não tem esse token no banco de dados
            return {'status': -1, 'msg': 'Token inválido.'}
        ##########################################################################

        # Verifica se o arquivo existe
        if os.path.isfile(f"{app.config['PERFIL_FOLDER']}/{login}"):
            return {"status": 0, "url": f"{request.host_url}{app.config['PERFIL_FOLDER']}/{login}"}
        # Se não, exibe o avatar padrão
        else:
            return {"status": 0, "url": f"{request.host_url}/static/imagens/padrao.png"}
    else:
        #Captura o token que vem do Header
        auth = request.headers.get('Authorization')
        #Testa se tem algum usuario cadastrado com esse token
        usuario = Token.retorna_usuario(auth)
        if (usuario == None):
            #ERRO: Não tem esse token no banco de dados
            return {'status': -1, 'msg': 'Token inválido.'}
        ##########################################################################

        #verifica se a foto esta sendo alterada do usuário cadastrado
        if usuario["login"] == login:
            arq = open(os.path.join(app.config['PERFIL_FOLDER'], usuario["login"]), "wb")
            arq.write(request.data)
            arq.close()

            return {"status": 0, "msg": "Foto alterada com sucesso"}
        else:
            return {"status": 2, "msg": "Você não pode alterar esse perfil"}


#db.altera_nome(request.form["login"], request.form["nome"])
#return jsonify({'status': 0, 'msg': 'Nome alterado com sucesso.'})

@app.route('/api/Postagem', methods=["POST"])
def postar_msg():
    login = Token.retorna_usuario(request.headers.get('Authorization'))
    
    if (login == None):
        return {'status': -1, 'msg': 'Token Inválido!' }
  
    try: 
        texto = request.form['corpo']

        if texto == "":
            return {'status': 2 , 'msg': "Mensagem Vazia!"}

        db.posta_mensagem(login['id'], texto)
        return {'status': 0, 'msg': "Mensagem Postada."}                            
    
    except KeyError: 
        return jsonify({"status": 1, "msg": "Mensagem Não digitada."})


@app.route('/api/buscar_msg/<login>', methods = ["GET"])
def buscar_msg(self,login):
    usuario = Token.retorna_usuario(request.headers.get('Authorization'))

    if usuario == (None):
        return {'status': -1, 'msg': 'Token Inválido!'}       

    perfil = db.busca_usuario(login)
    postagens = db.listar_mensagem(perfil['id'])
    lista = []
    for mensagem in postagens:
        lista.append(mensagem)
  
    return {'status': 0,  'lista': lista}
