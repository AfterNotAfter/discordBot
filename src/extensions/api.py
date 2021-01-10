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
class Webserver():
    def __init__(self):
        #FireBase
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
                rdict={"cert": config.firebase_web_cert, "storeconfig": config,"discordId":discordId}
                template = self.templateEnv.get_template('login.twitter.html')
                return response.html(template.render(rdict))
            except:
                return response.redirect("discord")
            
        @app.route('/discordinvite')
        async def route_discord(request):
            return response.redirect(f"{config.discord_invite}")
        
        @app.route('/tokenlogin',methods = ['GET','POST'])
        async def tokenlogin(request):
            try:
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
                encoded_data=jwt.encode(ndata,config.site_url)
                ndata.update({"updatetime": datetime.datetime.utcnow()})
                dbdoc = self.db.collection(f"users").document(f"{id}")
                dbdoc.set(ndata)
                async with websockets.connect("ws://localhost:3000") as websocket:
                    await websocket.send(encoded_data)
                    recv = await websocket.recv()
                    if recv == "OK":
                        return response.html("""
                        <script>
                        window.close()
                        self.close()
                        window.open('','_self').close();
                        window.location.href = window.location.origin + "/"
                        </script>
                        
                        
                        """)
                    else:
                        return response.redirect("/")
            except Exception as e:
                return response.text("ERROR: "+str(e))
        ssl_context ={"cert":"./cert/fullchain.pem",'key': "./cert/privkey.pem"}
        app.run(host='0.0.0.0', port=443, ssl=ssl_context, debug=False)

        
        
        