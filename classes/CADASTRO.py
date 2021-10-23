from flask_restful import Resource
from flask import request
from flask import jsonify
from kivy.lang import Builder
from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.network.urlrequest import UrlRequest
from urllib.parse import urlencode
from model import db
from passlib.hash import sha256_crypt


class Cadastrar(Resource):
    def POST(self):       
        pass
                
                        
                  
    
        

