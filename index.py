import asyncio
import threading
from roop import core
from flask import Flask, request, jsonify
from flask_cors import CORS
from threading import Thread
import base64
import requests
import os


app = Flask(__name__)
CORS(app)

async def createDeepFake(source, target):
    return(core.run(source, target, "./assets/outputs"))

async def process(code, video, source, target, phone):
    await createDeepFake(source, target)
    with open("./assets/outputs/{}.mp4".format(code + video), "rb") as fh:
        data = base64.b64encode(fh.read()).decode('utf-8')
    requests.post("http://localhost:3000/ready", json={
        "phone": phone,
        "video": data,
    })
    os.remove(source)
    os.remove("./assets/outputs/{}.mp4".format(code + video))
    print("{} enviado!".format(code + video))

@app.route('/roop', methods=['POST'])
def goRoop():
    data = request.get_json()
    imagedata = data.get('image').split(",")[1]

    source = "./assets/sources/{}.png".format(data.get('code'))
    target = "./assets/targets/{}.mp4".format(data.get('video'))

    with open(source, "wb") as fh:
        fh.write(base64.b64decode(imagedata))

    def workStart(code, video, source, target, phone):
        asyncio.run(process(code, video, source, target, phone))

    thread = Thread(target=workStart, kwargs={
        "code": data.get('code'),
        "video": data.get('video'),
        "source": source,
        "target": target,
        "phone": data.get('phone')
    }, name=data.get('code'))
    thread.start()
    return data

@app.route('/getRunning', methods=['GET'])
def getRunning():
    threads = []

    for thread in threading.enumerate():
        threads.append(thread.name)


    return jsonify({
        "actives": threading.active_count(),
        "threads": threads
    })

app.run(port=5000, host='localhost', debug=True)
