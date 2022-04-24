import os
import sys
import time
import json
import yaml
import shutil
import hashlib
import os
import zipfile
import base64
import uuid

from cli_passthrough import cli_passthrough

import click
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

VERSION = "0.1"
version = "0.2"
api_spec_version = "0.1"
status = 'good'

test = {
        'status': status,
        }

info = {
        'status': status,
        'version': version,
        'api-spec-version': api_spec_version,
        }

@app.route('/api/v1.0/post/echo', methods=['POST'])
def post():
    return jsonify(request.json)

def remove(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        if os.path.isdir(path):
            shutil.rmtree(path)

version = "0.2"
api_spec_version = "0.1"

host = "http://127.0.0.1"
port = "5555"

def call_server():
    r = requests.post(host + ':' + port + '/api/v1.0/post/echo', json = {"username":"xyz","password":"xyz"})
    print(r.text)


def test():
    app.run(debug=True, port=5555)

def cli():
    test()
    call_server()

def progressbar(it, prefix="", size=60, file=sys.stdout):
    count = len(it)
    def show(j):
        x = int(size*j/count)
        file.write("%s[%s%s] %i/%i\r" % (prefix, "#"*x, "."*(size-x), j, count))
        file.flush()
    show(0)
    for i, item in enumerate(it):
        yield item
        show(i+1)
    file.write("\n")
    file.flush()

PROJECT_NAME = "jobrunner"

context_settings = {"help_option_names": ["-h", "--help"]}


@click.group(context_settings=context_settings)
@click.version_option(prog_name=PROJECT_NAME.capitalize(), version=VERSION)
@click.pass_context
def cli(ctx):
    pass

@click.group(name="client")
def client_group():
    pass

@click.group(name="server")
def server_group():
    pass

@server_group.command("serve")
def serve_cmd():
    app.run(debug=True, port=5555)

@client_group.command("call")
def call_cmd():
    for i in progressbar(range(1), "Computing: ", 40):
        time.sleep(0.1)

    uuid_name = uuid.uuid4().hex

    def zipdir(path, ziph):
        # ziph is zipfile handle
        for root, dirs, files in os.walk(path):
            for file in files:
                ziph.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           os.path.join(path, '..')))
    dirName = ".tmp/"
    if not os.path.exists(".tmp/"):
        os.mkdir(dirName)
    dirName = ".tmp/up"
    if not os.path.exists(".tmp/up"):
        os.mkdir(dirName)
    dirName = ".tmp/down"
    if not os.path.exists(".tmp/down"):
        os.mkdir(dirName)
    with zipfile.ZipFile(".tmp/up/" + uuid_name +  ".zip", "w", zipfile.ZIP_DEFLATED) as zipf:
        zipdir('input/raycaster', zipf)

    with open(".tmp/up/" + uuid_name +  ".zip", "rb") as image_file:
        bytes_data = bytes(image_file.read())
        encoded_data = base64.b64encode(bytes_data)

    with open(".tmp/up/" + uuid_name +  ".base64", 'wb') as f:
        f.write(encoded_data)

    with open(".tmp/up/" + uuid_name +  ".base64", "rb") as image_file:
        bytes_data = bytes(image_file.read())

    def to_message(bytes_payload, uuid_name, jobid, metadata):
        message = {
            "payload": bytes_payload.decode("utf-8"),
            "uuid_name": uuid_name,
            "jobid": jobid,
            "metadata": metadata
        }
        return json.dumps(message)

    def from_message(message):
        payload_obj = json.loads(message)
        payload_obj["payload"] = bytes(base64.b64decode(payload_obj["payload"]))
        return payload_obj


    message = to_message(bytes_data, uuid_name, jobid=5, metadata={"pattern": "full"})
    payload_obj = from_message(message)

    with open('.tmp/down/' + payload_obj["uuid_name"] + '.zip', 'wb') as f:
        f.write(payload_obj["payload"])

    remove("output/cythone/raycaster")
    with zipfile.ZipFile('.tmp/down/' + payload_obj["uuid_name"] + '.zip', 'r') as zip_ref:
        zip_ref.extractall('output/cythone')

cli.add_command(client_group)
cli.add_command(server_group)
cli
