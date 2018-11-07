from flask import Flask, request, Response, render_template, jsonify
import json, hashlib, random, subprocess
from config import websockify_run
from functools import wraps
app =  Flask(__name__)

labconfig = "" #This is where lab configuration is stored
lab_status = False #Lab status is false by default, it's not running

import dbcontrol, mmcontrol, mmstart
def startlab():
    dbcontrol.drop_sim_info()
    dbcontrol.create_db()
    mmstart.startmm(labconfig)

def stoplab():
    mmcontrol.stop_mm()
    dbcontrol.drop_sim_info()

#Login check for admin panel
#Source: http://flask.pocoo.org/snippets/8/
def check_auth(username, password):
    return ((username == "admin" and password == "admin"))

def authenticate():
    return Response(
    'Could not verify your access level for that URL.\n'
    'You have to login with proper credentials', 401,
    {'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

#API
@app.route("/")
def index():
    return jsonify({"Server":"Running"})

#Handle file upload
@app.route("/upload", methods=["POST"])
@requires_auth
def upload():
    global labconfig
    try:
        if request.files:
            labconfig = json.loads(request.files["file"].read())
            return jsonify({"upload":True})
        else:
            return jsonify({"upload":False})
    except Exception as err:
        return jsonify({"upload":"Something broke","error":err})

@app.route("/info")
@requires_auth
def info():
    global labconfig
    try:
        if labconfig:
            return jsonify({"info":labconfig})
        else:
            return jsonify({"info":False})
    except Exception as err:
        return jsonify({"info":"Something broke","error":err})

@app.route("/on")
@requires_auth
def on():
    global lab_status
    global websockify_process
    try:
        if lab_status:
            return jsonify({"on":"Already on"})
        else:
            if labconfig:
                startlab()
                passwordsjson = {"passwords":dbcontrol.vm_info()}
                tokenfile = open("tokenfile","w")
                for vm in passwordsjson['passwords']:
                    tokenfile.write("%s: localhost:%s\n" % (vm['vm_name'],vm['vncport']))
                tokenfile.close()
                websockify_process = subprocess.Popen([websockify_run,"--target-config=tokenfile","1338"])
                lab_status = True
                return jsonify({"on":True})
            else:
                return jsonify({"on":"Configs not provided"})
    except Exception as err:
        return jsonify({"on":"Something broke","error":err})

@app.route("/off")
@requires_auth
def off():
    global lab_status
    global websockify_process
    try:
        if lab_status:
            stoplab()
            websockify_process.kill()
            lab_status = False
            return jsonify({"off":True})
        else:
            return jsonify({"off":"Already off"})
    except Exception as err:
        return jsonify({"off":"Something broke","error":err})

@app.route("/status")
@requires_auth
def sim_status():
    global lab_status
    try:
        return jsonify({"status":lab_status})
    except Exception as err:
        return jsonify({"status":"Something broke","error":err})

@app.route("/passwords")
@requires_auth
def passwords():
    global lab_status
    try:
        if lab_status:
            return jsonify({"passwords":dbcontrol.vm_info()})
        else:
            return jsonify({"passwords":False})
    except Exception as err:
        return jsonify({"passwords":"Something broke","error":err})

@app.route("/changepassword/<string:vmname>")
@requires_auth
def changepasswords(vmname):
    global lab_status
    try:
        if lab_status:
            password = hashlib.md5(str(random.random())).hexdigest()[:6]
            mmcontrol.set_password(vmname, password)
            dbcontrol.update_password(vmname, password)
            return jsonify({"change":True})
        else:
            return jsonify({"change":False})
    except Exception as err:
        return jsonify({"change":"Something broke","error":err})

@app.route("/reboot/<string:vmname>")
@requires_auth
def reboot(vmname):
    global lab_status
    try:
        if lab_status:
            mmcontrol.vm_reboot(vmname, dbcontrol.get_password(vmname))
            return jsonify({"reboot":True})
        else:
            return jsonify({"reboot":False})
    except Exception as err:
        return jsonify({"reboot":"Something broke","error":err})

@app.route("/webui")
@requires_auth
def webui():
    return render_template("webui.html")

@app.route("/webupload")
@requires_auth
def webupload():
    return render_template("webupload.html")

@app.route("/control")
@requires_auth
def control():
    global lab_status
    header = '<table border="1"><tbody>'
    footer = '</tbody></table>'
    try:
        if lab_status:
            links = "<tr><th>VM</th><th>VNC Port</th><th>VNC Password</th><th>Reset Password</th><th>Reboot</th><th>NoVNC</th></tr>"
            passwordsjson = {"passwords":dbcontrol.vm_info()}
            for vm in passwordsjson['passwords']:
                vmname = vm['vm_name']
                vncport = vm['vncport']
                vncpassword = vm['password']
                links = links + '<tr><td>%s</td><td>%s</td><td>%s</td><td><a target="_blank" href="/changepassword/%s">Reset PW</a></td><td><a target="_blank" href="/reboot/%s">Reboot</a></td><td><a target="_blank" href="/static/vnc.html?port=1338&password=%s&path=?token=%s">NoVNC</a></td></tr>' % (vmname, vncport, vncpassword, vmname, vmname,vncpassword,vmname)
            return header + links + footer
        else:
            return jsonify({"control":False})
    except Exception as err:
        return jsonify({"control":"Something broke","error":err})

#Start the web server
if __name__ == "__main__":
    app.debug = False
    app.run(host="0.0.0.0", port=1337, threaded=True)
