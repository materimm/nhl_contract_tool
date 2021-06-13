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
    print(players)
    return players
