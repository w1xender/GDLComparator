from flask import Flask, render_template, request, jsonify, make_response
import requests
import pycountry
from re import sub
app = Flask(__name__)
def fetchData(username):
    usersResponse = requests.get('https://api.demonlist.org/leaderboard/user/list', params={'search': username})
    usersData = usersResponse.json()['data']['users']
    for user in usersData:
        if username.lower() == user['username'].lower():
            userResponse = requests.get('https://api.demonlist.org/user/get', params={'id': user['id']})
            userData = userResponse.json()['data']
            userRecordsResponse = requests.get('https://api.demonlist.org/user/record/list', params={'user_id': user['id']})
            userRecordsData = userRecordsResponse.json()['data']
            hardestLevelResponse = requests.get('https://api.demonlist.org/level/classic/get', params={'placement': userData['levels']['hardest']['placement']})
            hardestLevelCreator = hardestLevelResponse.json()['data']['creator']
            hardestLevelCreator = sub(r'\band\b', '&', hardestLevelCreator.replace('&amp;', '&'))
            hardestLevelCreator = sub(r'\bM\b', 'more', hardestLevelCreator)
            verifiedData = userData['levels']['verified']
            hardestVerifiedLevelCreator = None
            if verifiedData:
                hardestVerifiedLevelResponse = requests.get('https://api.demonlist.org/level/classic/get', params={'placement': verifiedData[0]['placement']})
                hardestVerifiedLevelCreator = hardestVerifiedLevelResponse.json()['data']['creator']
                hardestVerifiedLevelCreator = sub(r'\band\b', '&', hardestVerifiedLevelCreator.replace('&amp;', '&'))
                hardestVerifiedLevelCreator = sub(r'\bM\b', 'more', hardestVerifiedLevelCreator)
            stats = {
                'country': f'<img src=https://flagcdn.com/40x30/{pycountry.countries.search_fuzzy(user["country"].replace("-", " "))[0].alpha_2.lower()}.png>',
                'username': user['username'],
                'placement': userData['placement'],
                'points': float(userData['points']),
                'hardestLevelName': userData['levels']['hardest']['name'],
                'hardestLevelCreator': hardestLevelCreator,
                'hardestLevelPlacement': userData['levels']['hardest']['placement'],
                'cleared': userRecordsData['completed_count'],
                'notCleared': userRecordsData['total_count'] - userRecordsData['completed_count'],
                'verifiedCount': len(verifiedData) if verifiedData else 0,
                'hardestVerifiedLevelName': verifiedData[0]['name'] if verifiedData else None,
                'hardestVerifiedLevelCreator': hardestVerifiedLevelCreator if verifiedData else None,
                'hardestVerifiedLevelPlacement': verifiedData[0]['placement'] if verifiedData else None
            }
            return stats
    return None
def compareUsers(stats):
    scores = [0, 0]
    results = []
    if stats[0]['points'] > stats[1]['points']:
        difference = round(stats[0]['points'] - stats[1]['points'], 2)
        results.append(f'+1! {stats[0]["username"]} has more points than {stats[1]["username"]} ({difference} points)')
        scores[0] += 1
    elif stats[1]['points'] > stats[0]['points']:
        difference = round(stats[1]['points'] - stats[0]['points'], 2)
        results.append(f'+1! {stats[1]["username"]} has more points than {stats[0]["username"]} ({difference} points)')
        scores[1] += 1
    if stats[0]['hardestLevelPlacement'] < stats[1]['hardestLevelPlacement']:
        results.append(f'+1! {stats[0]["username"]}\'s hardest is harder than {stats[1]["hardestLevelName"]} (#{stats[1]["hardestLevelPlacement"]})')
        scores[0] += 1
    elif stats[1]['hardestLevelPlacement'] < stats[0]['hardestLevelPlacement']:
        results.append(f'+1! {stats[1]["username"]}\'s hardest is harder than {stats[0]["hardestLevelName"]} (#{stats[0]["hardestLevelPlacement"]})')
        scores[1] += 1
    if stats[0]['cleared'] > stats[1]['cleared']:
        difference = stats[0]['cleared'] - stats[1]['cleared']
        results.append(f'+1! {stats[0]["username"]} has completed more levels than {stats[1]["username"]} ({difference} levels)')
        scores[0] += 1
    elif stats[1]['cleared'] > stats[0]['cleared']:
        difference = stats[1]['cleared'] - stats[0]['cleared']
        results.append(f'+1! {stats[1]["username"]} has completed more levels than {stats[0]["username"]} ({difference} levels)')
        scores[1] += 1
    if stats[0]['hardestVerifiedLevelPlacement'] is not None and stats[1]['hardestVerifiedLevelPlacement'] is not None:
        if stats[0]['hardestVerifiedLevelPlacement'] < stats[1]['hardestVerifiedLevelPlacement']:
            results.append(f'+1! {stats[0]["username"]}\'s hardest verified level is harder than {stats[1]["hardestVerifiedLevelName"]} (#{stats[1]["hardestVerifiedLevelPlacement"]})')
            scores[0] += 1
        elif stats[1]['hardestVerifiedLevelPlacement'] < stats[0]['hardestVerifiedLevelPlacement']:
            results.append(f'+1! {stats[1]["username"]}\'s hardest verified level is harder than {stats[0]["hardestVerifiedLevelName"]} (#{stats[0]["hardestVerifiedLevelPlacement"]})')
            scores[1] += 1
    results.append(f'{stats[0]["username"]}: {scores[0]} points')
    results.append(f'{stats[1]["username"]}: {scores[1]} points')
    if scores[0] > scores[1]:
        results.append(f'{stats[0]["username"]} wins!')
    elif scores[1] > scores[0]:
        results.append(f'{stats[1]["username"]} wins!')
    else:
        results.append('Tie!')
    return {'results': results, 'scores': scores}
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/compare', methods=['POST'])
def compare():
    data = request.get_json()
    usernames = data.get('usernames', [])
    if len(usernames) != 2 or not usernames[0] or not usernames[1] or usernames[0] == usernames[1]:
        return make_response('', 400)
    stats = []
    for username in usernames:
        result = fetchData(username)
        stats.append(result)
    if None in stats:
        return make_response('', 400)
    comparison = compareUsers(stats)
    return jsonify({
        'users': stats,
        'comparison': comparison
    })
if __name__ == '__main__':
    app.run()
