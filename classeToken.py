from model import db
class Token():
    def recebe_token(auth):
        try:
            print(auth)
            (tipo, token) = auth.split(' ')
            print(tipo)
            print(token)
            if tipo.lower() != "bearer":
                return None
            else:
                return token
        except AttributeError:
            return None
    
    def retorna_usuario(auth):
        token = Token.recebe_token(auth)
        if (token != None):
            return db.verifica_token(token)
        else:
            return None