from flask import Flask, jsonify, request, render_template, redirect, url_for
import backend.api as api

app = Flask(__name__)

@app.route('/')
def index():
    return redirect(url_for('contracts'))

@app.route('/contracts')
def contracts():
    return render_template('contracts.html', **locals())


##############
##   APIs   ##
##############

@app.route('/get_players', methods=['GET'])
def get_players(team=None):
    team = request.args.get('team')
    players = api.get_players(team)
    return players


@app.route('/get_contract', methods=['GET'])
def get_contract(team=None, player=None):
    team = request.args.get('team')
    player = request.args.get('player')
    obj = api.get_contract(team, player)
    return obj
