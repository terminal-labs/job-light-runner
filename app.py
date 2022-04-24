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
from pathlib import Path

import requests
import click
from flask import Flask, jsonify, request

from cli_passthrough import cli_passthrough

VERSION = "0.1"
version = "0.2"
api_spec_version = "0.1"
status = 'good'

host = "http://127.0.0.1"
port = "5555"

client_up = '.tmp/client/up/'
client_down = '.tmp/client/down/'
server_up = '.tmp/server/up/'
server_down = '.tmp/server/down/'
server_jobs = '.tmp/server/jobs/'

PROJECT_NAME = "jobrunner"
context_settings = {"help_option_names": ["-h", "--help"]}
test = {'status': status,}
info = {'status': status,'version': version,'api-spec-version': api_spec_version,}

def create_dirs(dirs):
    for dir in dirs:
        if not os.path.exists(dir):
            os.mkdir(dir)

def remove(path):
    if os.path.exists(path):
        if os.path.isfile(path):
            os.remove(path)
        if os.path.isdir(path):
            shutil.rmtree(path)

def read_tmp_base64file(filepath):
    with open(filepath, "rb") as image_file:
        encoded_data = bytes(image_file.read())
        return encoded_data

def write_tmp_base64file(filepath, data):
    with open(filepath, 'wb') as f:
        if isinstance(data, str):
            f.write(bytes(data, encoding='utf8'))
        elif isinstance(data, bytes):
            f.write(data)

def extractzip(tmp_zipfilename, outputdir):
    with zipfile.ZipFile(tmp_zipfilename, 'r') as zip_ref:
        zip_ref.extractall(outputdir)

def creatzip(tmp_zipfilename, inputdir):
    with zipfile.ZipFile(tmp_zipfilename, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipdir(inputdir, zipf)

def readzip(tmp_zipfilename):
    with open(tmp_zipfilename, "rb") as image_file:
        data = image_file.read()
        if isinstance(data, str):
            return bytes(image_file.read())
        elif isinstance(data, bytes):
            return data

def writefile(tmp_zipfilename, bytes_data):
    with open(tmp_zipfilename, 'wb') as f:
        f.write(bytes_data)

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

def sanitise_json(message):
    data = json.loads(message)
    assert isinstance(data["payload"], str)
    assert isinstance(data["uuid_name"], str)
    assert isinstance(data["jobid"], int)
    assert isinstance(data["metadata"], dict)
    return message

def to_message(bytes_payload, uuid_name, jobid, metadata):
    assert isinstance(bytes_payload, bytes)
    message = {
        "payload": bytes_payload.decode("utf-8"),
        "uuid_name": uuid_name,
        "jobid": jobid,
        "metadata": metadata
    }
    data = json.dumps(message)
    data = sanitise_json(data)
    return data

def from_message(message):
    payload_obj = json.loads(message)
    payload_obj["payload"] == bytes(payload_obj["payload"], encoding='utf8')
    return payload_obj

def zipdir(path, ziph):
    for root, dirs, files in os.walk(path):
        for file in files:
            ziph.write(os.path.join(root, file),
            os.path.relpath(os.path.join(root, file),
            os.path.join(path, '..')))

def send_zip_local(inputdir, uuid_name, jobid):
    create_dirs([
        ".tmp/",
        ".tmp/client",
        client_up,
        client_down,
        ]
    )

    tmp_zipfilename = client_up + uuid_name +  ".zip"
    tmp_base64filename = client_up + uuid_name +  ".base64"

    creatzip(tmp_zipfilename, inputdir)
    bytes_data = readzip(tmp_zipfilename)
    encoded_data = base64.b64encode(bytes_data)
    assert isinstance(bytes_data, bytes)
    assert isinstance(encoded_data, bytes)
    write_tmp_base64file(tmp_base64filename, encoded_data)
    bytes_data = read_tmp_base64file(tmp_base64filename)
    return to_message(bytes_data, uuid_name, jobid, metadata={"pattern": "full"})

def get_zip_local(message, outputdir, uuid_name, jobid):
    remove(outputdir)

    tmp_zipfilename = client_down + uuid_name +  ".zip"
    tmp_base64filename = client_down + uuid_name +  ".base64"

    payload_obj = from_message(message)
    write_tmp_base64file(tmp_base64filename, payload_obj["payload"])
    encoded_data = read_tmp_base64file(tmp_base64filename)
    bytes_data = base64.b64decode(encoded_data)
    assert isinstance(encoded_data, bytes)
    assert isinstance(bytes_data, bytes)
    writefile(tmp_zipfilename, bytes_data)
    extractzip(tmp_zipfilename, outputdir)

def process_zip_local():
    create_dirs([
        ".tmp/",
        ".tmp/server",
        server_up,
        server_down,
        server_jobs,
        ]
    )

def call_server():
    r = requests.post(host + ':' + port + '/api/v1.0/post/echo', json = {"username":"xyz","password":"xyz"})
    print(r.text)

def test():
    app.run(debug=True, port=5555)

def cli():
    test()
    call_server()

app = Flask(__name__)

@app.route('/api/v1.0/post/echo', methods=['POST'])
def post():
    return jsonify(request.json)

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
    # for i in progressbar(range(1), "Computing: ", 40):
    #     time.sleep(0.1)

    uuid_name = uuid.uuid4().hex
    jobid = 8
    message = send_zip_local("input/raycaster", uuid_name, jobid)
    print(message)
    process_zip_local()
    get_zip_local(message, "output/cythone", uuid_name, jobid)

cli.add_command(client_group)
cli.add_command(server_group)
