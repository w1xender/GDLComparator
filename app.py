from flask import Flask, render_template, request, jsonify
import requests
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
            hardestLevelCreator = hardestLevelResponse.json()['data']['creator'].replace('&amp;', 'and')
            verifiedData = userData['levels']['verified']
            hardestVerifiedLevelCreator = None
            if verifiedData:
                hardestVerifiedLevelResponse = requests.get('https://api.demonlist.org/level/classic/get', params={'placement': verifiedData[0]['placement']})
                hardestVerifiedLevelCreator = hardestVerifiedLevelResponse.json()['data']['creator'].replace('&amp;', 'and')
            displayInfo = {
                'country': user['country'].replace('-', ' '),
                'username': user['username'],
                'badge': userData['badge'],
                'placement': userData['placement'],
                'points': float(userData['points']),
                'hardestLevelName': userData['levels']['hardest']['name'],
                'hardestLevelCreator': hardestLevelCreator,
                'hardestLevelPlacement': userData['levels']['hardest']['placement'],
                'cleared': userRecordsData['completed_count'],
                'notCleared': userRecordsData['total_count'] - userRecordsData['completed_count'],
                'verifiedCount': len(verifiedData) if verifiedData else 0,
                'hasVerified': bool(verifiedData),
                'hardestVerifiedLevelName': verifiedData[0]['name'] if verifiedData else None,
                'hardestVerifiedLevelCreator': hardestVerifiedLevelCreator if verifiedData else None,
                'hardestVerifiedLevelPlacement': verifiedData[0]['placement'] if verifiedData else None
            }
            return {
                'displayInfo': displayInfo,
                'stats': {
                    'username': user['username'],
                    'points': float(userData['points']),
                    'hardest': userData['levels']['hardest']['placement'],
                    'cleared': userRecordsData['completed_count'],
                    'hardestVerified': verifiedData[0]['placement'] if verifiedData else None
                }
            }
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
    if stats[0]['hardest'] < stats[1]['hardest']:
        results.append(f'+1! {stats[0]["username"]}\'s hardest is harder than {stats[1]["hardest"]}')
        scores[0] += 1
    elif stats[1]['hardest'] < stats[0]['hardest']:
        results.append(f'+1! {stats[1]["username"]}\'s hardest is harder than {stats[0]["hardest"]}')
        scores[1] += 1
    if stats[0]['cleared'] > stats[1]['cleared']:
        difference = stats[0]['cleared'] - stats[1]['cleared']
        results.append(f'+1! {stats[0]["username"]} has completed more levels than {stats[1]["username"]} ({difference} levels)')
        scores[0] += 1
    elif stats[1]['cleared'] > stats[0]['cleared']:
        difference = stats[1]['cleared'] - stats[0]['cleared']
        results.append(f'+1! {stats[1]["username"]} has completed more levels than {stats[0]["username"]} ({difference} levels)')
        scores[1] += 1
    if stats[0]['hardestVerified'] is not None and stats[1]['hardestVerified'] is not None:
        if stats[0]['hardestVerified'] < stats[1]['hardestVerified']:
            results.append(f'+1! {stats[0]["username"]}\'s hardest verified level is harder than {stats[1]["hardest"]}')
            scores[0] += 1
        elif stats[1]['hardestVerified'] < stats[0]['hardestVerified']:
            results.append(f'+1! {stats[1]["username"]}\'s hardest verified level is harder than {stats[0]["hardest"]}')
            scores[1] += 1
    results.append(f'{stats[0]["username"]}: {scores[0]} points')
    results.append(f'{stats[1]["username"]}: {scores[1]} points')
    if scores[0] > scores[1]:
        results.append(f'{stats[0]["username"]} wins!')
        winner = stats[0]['username']
    elif scores[1] > scores[0]:
        results.append(f'{stats[1]["username"]} wins!')
        winner = stats[1]['username']
    else:
        results.append('Tie!')
        winner = None
    return {'results': results, 'scores': scores, 'winner': winner}
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/compare', methods=['POST'])
def compare():
    data = request.get_json()
    usernames = data.get('usernames', [])
    if len(usernames) != 2:
        return jsonify({'error': 'Please provide exactly 2 usernames.'}), 400
    stats = []
    usersStats = []
    for username in usernames:
        result = fetchData(username)
        if result is None:
            return jsonify({'error': f'User {username} not found.'})
        stats.append(result['stats'])
        usersStats.append(result['displayInfo'])
    comparison = compareUsers(stats)
    return jsonify({
        'users': usersStats,
        'comparison': comparison
    })
if __name__ == '__main__':
    app.run()
