import os
import yaml
import shutil
import hashlib

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

@app.route('/system/test', methods=['GET'])
def std_system_test():
    return jsonify(test)

@app.route('/system/info', methods=['GET'])
def std_system_general_info():
    return jsonify(info)

@app.route('/api/v1.0/system/test', methods=['GET'])
def system_test():
    return jsonify(test)

@app.route('/api/v1.0/system/info', methods=['GET'])
def system_general_info():
    return jsonify(info)

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
    r = requests.get(host + ':' + port + '/system/test')
    print(r.text)

    r = requests.get(host + ':' + port + '/system/info')
    print(r.text)

    r = requests.get(host + ':' + port + '/api/v1.0/system/test')
    print(r.text)

    r = requests.get(host + ':' + port + '/api/v1.0/system/info')
    print(r.text)

    r = requests.post(host + ':' + port + '/api/v1.0/post/echo', json = {"username":"xyz","password":"xyz"})
    print(r.text)


def test():
    app.run(debug=True, port=5555)

def cli():
    test()
    call_server()

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
    call_server()

cli.add_command(client_group)
cli.add_command(server_group)
cli
