import requests
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
            print(f'[{user["country"].replace("-", " ")}] {user["username"]}')
            if userData['badge'] == 'former_cheater':
                print('Former cheater')
            print(f'Placement: #{userData["placement"]}')
            print(f'Points: {userData["points"]}')
            print(f'Hardest level: {userData["levels"]["hardest"]["name"]} by {hardestLevelCreator} (#{userData["levels"]["hardest"]["placement"]})')
            print(f'Cleared {userRecordsData["completed_count"]} levels ({userRecordsData["total_count"] - userRecordsData["completed_count"]} non-100% records)') if userRecordsData["total_count"] - userRecordsData["completed_count"] != 0 else print(f'Cleared {userRecordsData["completed_count"]} levels')
            if verifiedData:
                print(f'Verified {len(verifiedData)} levels')
                print(f'Hardest verified level: {verifiedData[0]["name"]} by {hardestVerifiedLevelCreator} (#{verifiedData[0]["placement"]})')
            else:
                print('No verified levels')
            return {
                'username': user['username'],
                'points': userData['points'],
                'hardest': userData['levels']['hardest']['placement'],
                'cleared': userRecordsData['completed_count'],
                'hardestVerified': verifiedData[0]['placement'] if verifiedData else None
            }
    return None
def compareUsers(stats):
    scores = [0, 0]
    if stats[0]['points'] > stats[1]['points']:
        difference = round(float(stats[0]['points']) - float(stats[1]['points']), 2)
        print(f'+1! {stats[0]["username"]} has more points than {stats[1]["username"]} ({difference} points)')
        scores[0] += 1
    elif stats[1]['points'] > stats[0]['points']:
        difference = round(float(stats[1]['points']) - float(stats[0]['points']), 2)
        print(f'+1! {stats[1]["username"]} has more points than {stats[0]["username"]} ({difference} points)')
        scores[1] += 1
    if stats[0]['hardest'] < stats[1]['hardest']:
        print(f'+1! {stats[0]["username"]}\'s hardest is harder than {stats[1]["hardest"]}')
        scores[0] += 1
    elif stats[1]['hardest'] < stats[0]['hardest']:
        print(f'+1! {stats[1]["username"]}\'s hardest is harder than {stats[0]["hardest"]}')
        scores[1] += 1
    if stats[0]['cleared'] > stats[1]['cleared']:
        difference = stats[0]['cleared'] - stats[1]['cleared']
        print(f'+1! {stats[0]["username"]} has completed more levels than {stats[1]["username"]} ({difference} levels)')
        scores[0] += 1
    elif stats[1]['cleared'] > stats[0]['cleared']:
        difference = stats[1]['cleared'] - stats[0]['cleared']
        print(f'+1! {stats[1]["username"]} has completed more levels than {stats[0]["username"]} ({difference} levels)')
        scores[1] += 1
    if stats[0]['hardestVerified'] is not None and stats[1]['hardestVerified'] is not None:
        if stats[0]['hardestVerified'] < stats[1]['hardestVerified']:
            print(f'+1! {stats[0]["username"]}\'s hardest verified level is harder than {stats[1]["hardest"]}')
            scores[0] += 1
        elif stats[1]['hardestVerified'] < stats[0]['hardestVerified']:
            print(f'+1! {stats[1]["username"]}\'s hardest verified level is harder than {stats[0]["hardest"]}')
            scores[1] += 1
    print(f'\n{stats[0]["username"]}: {scores[0]} points')
    print(f'{stats[1]["username"]}: {scores[1]} points')
    if scores[0] > scores[1]:
        print(f'{stats[0]["username"]} wins!')
    elif scores[1] > scores[0]:
        print(f'{stats[1]["username"]} wins!')
    else:
        print('Tie!')
while True:
    username = input('Type two users: ').strip()
    if not username:
        break
    if ',' in username:
        usernames = [user.strip() for user in username.split(',')]
    else:
        print('Separate usernames with a comma.')
        continue
    if len(usernames) != 2:
        continue
    stats = []
    for username in usernames:
        print()
        userStats = fetchData(username)
        if userStats is None:
            print(f'User {username} not found.')
            break
        stats.append(userStats)
    if len(stats) == 2:
        print()
        compareUsers(stats)
        print()