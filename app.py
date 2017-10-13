# Optixal

import requests, time
from flask import Flask, url_for, redirect, render_template
from pprint import pprint

app = Flask(__name__)
BASEURL = 'https://2017.gryphonctf.com'

@app.route('/')
def index():
    return redirect(url_for('scoreboard'))

class Latest():
    def __init__(self, teamname, challname, challcat, challpoints, epoch):
        self.teamname = teamname
        self.challname = challname
        self.challcat = challcat
        self.challpoints = challpoints
        self.time = time.strftime('%H:%M', time.localtime(epoch))

def getLatest():
    data = getData()
    teamMap = {team.id : team.name for team in data}
    latestSolves = []
    for team in data:
        for solve in team.solves:
            latestSolves.append(solve)
    latestSolves = list(sorted(latestSolves, key=lambda x: x['time'], reverse=True))[:10]
    pprint(latestSolves)
    finalData = []
    downloadedTeams = {}
    for chall in latestSolves:
        while True:
            try:
                teamName = teamMap[chall['team']]
                if chall['team'] not in downloadedTeams:
                    print('[*] Downloading team {} info for chall {}...'.format(chall['team'], chall['chal']))
                    raw = requests.get('{}/solves/{}'.format(BASEURL, chall['team']), timeout=3)
                    parsed = raw.json()['solves']
                    downloadedTeams[chall['team']] = parsed
                else:
                    print('[*] Re-using team {} info for chall {}...'.format(chall['team'], chall['chal']))
                    parsed = downloadedTeams[chall['team']]
                challName = [x for x in parsed if x['chalid'] == chall['chal']][0]['chal']
                challCat = [x for x in parsed if x['chalid'] == chall['chal']][0]['category']
                l = Latest(teamName, challName, challCat, chall['value'], chall['time'])
                finalData.append(l)
                break
            except Exception as e:
                print(e)
                continue
    print(finalData)
    return finalData

@app.route('/latest')
def latest():
    data = getLatest()
    return render_template('latest.html', data=data)

class Team():
    def __init__(self, teamPosition, teamDict):
        self.position = int(teamPosition)
        self.name = teamDict.get('name', '')
        self.id = teamDict.get('id', '')
        self.solves = [solve for solve in teamDict.get('solves', []) if solve.get('chal')]
        self.solved = len(self.solves)
        self.score = sum([chall.get('value', 0) for chall in self.solves])

def getData():
    data = []
    while True:
        try:
            print('[*] Downloading scoreboard data...')
            raw = requests.get('{}/top/20'.format(BASEURL), timeout=4)
            print('[+] Smexy...')
            parsed = raw.json()['places']
            for teamPosition, teamDict in parsed.items():
                t = Team(teamPosition, teamDict)
                data.append(t)
            break
        except Exception as e:
            print(e)
            continue
    data = sorted(data, key=lambda x: x.position)
    return data

@app.route('/data')
def data():
    data = getData()
    return render_template('data.html', teams=data)

@app.route('/scoreboard')
def scoreboard():
    return render_template('scoreboard.html')

@app.route('/results')
def results():
    return render_template('results.html')

@app.route('/timer')
def timer():
    return render_template('timer.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

