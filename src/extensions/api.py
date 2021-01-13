#Web Server
from sanic import Sanic
from sanic import response
from sanic_session import Session
import jinja2
import websockets
#Util
import json
import logging
import requests
import datetime
#Firebase
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
#Config
import config
import jwt
import importlib
class Webserver():
    def __init__(self):
        importlib.reload(config)
        #FireBase
        try:
            app = firebase_admin.get_app()
        except ValueError as e:
            cred = credentials.Certificate('./cert/firebasecert.json')
            firebase_admin.initialize_app(cred)

        self.db = firestore.client()
        app = Sanic (__name__)
        app.config['JSON_AS_ASCII'] = False
        Session(app)
        app.static('/assets', './assets')
        self.templateEnv = jinja2.Environment( loader=jinja2.FileSystemLoader('templates/'))
        
        @app.route('/')
        async def route_root(request):
            return response.redirect("discord")

        @app.route('/login')
        async def login(request):
            try:
                discordId = request.args['discordId'][0]
                mode = request.args['mode'][0]
                rdict={"cert": config.firebase_web_cert,"discordId":discordId,"mode": mode}
                template = self.templateEnv.get_template('login.twitter.html')
                return response.html(template.render(rdict))
            except Exception as e:
                print(e)
                return response.redirect("/")
            
        @app.route('/discord')
        async def route_discord(request):
            return response.redirect(f"{config.discord_invite}")
        
        @app.route('/introduce')
        async def introduce(request):
            try:
                discordId = request.args['discordId'][0]
                rdict={"cert": config.firebase_web_cert, "discordId":discordId}
                template = self.templateEnv.get_template('introduce.html')
                return response.html(template.render(rdict))
            except Exception as e:
                return response.text("ERROR: "+str(e))
        @app.route("/proceed_register",methods = ['POST'])
        async def proceed_register(request):
            try:
                mode = request.args['mode'][0]
                data = request.form
                discordId = data['discordId'][0]
                dbdoc = self.db.collection(f"users").document(f"{discordId}")
                doc=dbdoc.get()
                ndata = doc.to_dict()
                ndata.pop("updatetime")                
                append_data = {"introduce": {"nickname": data['nickname'][0], "gender": data['gender'][0], "tend": data['tend'][0], "age": data['age'][0]}}
                ndata.update(append_data)
                dbdoc.update(append_data)
                ndata.update({"mode":mode})
                if mode == "register":
                    text = "접수가 완료되었습니다!\n서버 참가자의 투표로 승인 여부가 결정됩니다!\n승인까지 기다려주세요!"
                if mode == "update":
                    text = "자기소개 등록이 완료되었습니다!\n이전과 같이 디스코드에서 즐거운 시간 보내세요!"
                async with websockets.connect("ws://localhost:3000") as websocket:
                    
                    encoded_data=jwt.encode(ndata,config.site_url)
                    await websocket.send(encoded_data)
                    recv = await websocket.recv()
                    print(recv)
                    if recv == "OK":
                        template = self.templateEnv.get_template('success.html')
                        print(text)
                        return response.html(template.render({"text":text}))
                        
            except Exception as e:
                return response.text("ERROR: "+str(e))
            

        @app.route('/tokenlogin',methods = ['GET','POST'])
        async def tokenlogin(request):
            try:
                mode = request.args['mode'][0]
                data = request.form
                userdata = json.loads(data['user'][0])[0]
                id=userdata['uid']
                usertag = requests.get(f"https://api.twitter.com/1.1/users/show.json?user_id={id}", headers={"Authorization": config.TwitterApiKey}).json()['screen_name']
                ndata = {}
                ndata.update({"id":str(id)})
                ndata.update({"usertag": "@" + usertag})
                ndata.update({"discordId":data['discordId'][0]})
                ndata.update({"token":data['token'][0]})
                ndata.update({"secret":data['secret'][0]})
                ndata.update({"displayname":userdata['displayName']})
                ndata.update({"photoURL": userdata['photoURL']})
                ndata.update({"email": userdata['email']})
                ndata.update({"updatetime": datetime.datetime.utcnow()})
                dbdoc = self.db.collection(f"users").document(f"{data['discordId'][0]}")
                dbdoc.set(ndata)
                return response.redirect(f"/introduce?discordId={data['discordId'][0]}&mode={mode}")
            except Exception as e:
                return response.text("ERROR: "+str(e))
        ssl_context ={"cert":"./cert/fullchain.pem",'key': "./cert/privkey.pem"}
        app.run(host='0.0.0.0', port=config.site_port, ssl=ssl_context, debug=False)

        
        
        