import requests
import json

credential_file = 'credentials.txt'


class player:

    def __init__(self):
        # read in credentials from file
        self.__credentials = dict()
        f = open(credential_file, 'r')
        for line in f.readlines():
            if line.rstrip() == '':
                continue
            [key, val] = line.rstrip().split('=')
            self.__credentials[key] = val
        self.login()

    def login(self):
        url = ('https://api.preguntados.com/api/users/' + self.__credentials['usernumber']
               + '/dashboard?app_config_version=' +
               self.__credentials['app_config_version']
               )
        header = {
            'Accept':           'application/json',
            'Cookie':           'ap_session=' + self.__credentials['ap_session'],
            'Accept-Encoding':  'gzip',
            'User-Agent':       self.__credentials['useragent'],
            'Eter-Agent':       self.__credentials['eteragent'],
            'Host':             'api.preguntados.com',
            'Connection':       'Keep-Alive',
        }
        r = requests.get(url, headers=header)
        self.__login_response = json.loads(r.text)

    def answer(self, game_number, question_id, category, answer,
               answer_type="NORMAL", requested_crown=None):
        url = 'https://api.preguntados.com/api/users/' + \
            self.__credentials['usernumber'] + \
            '/games/' + str(game_number) + '/answers'

        header = {
            'Accept':           'application/json',
            'Content-Type':     'application/json;charset=UTF-8',
            'Cookie':           'ap_session=' + self.__credentials['ap_session'],
            'Accept-Encoding':  'gzip',
            'User-Agent':       self.__credentials['useragent'],
            'Eter-Agent':       self.__credentials['eteragent'],
            'Content-Length':   '79',
            'Host':             'api.preguntados.com',
            'Connection':       'Keep-Alive',
        }
        payload = {
            "answers": [
                {
                    "answer": answer,
                    "category": category,
                    "id": question_id
                }
            ],
            "type": answer_type
        }
        if requested_crown is not None:
            payload['requested_crown'] = requested_crown

        r = requests.post(url, data=json.dumps(payload), headers=header)
        return json.loads(r.text)

    # Given specification of gamestate, return answer.
    def solve(self, game_spec):
        if not game_spec['my_turn']:
            return None

        entry = dict()

        entry['game_number'] = game_spec['id']

        if 'spins_data' not in game_spec:
            return entry
        else:
            spins = game_spec['spins_data']['spins']

        entry['question_id'] = \
            spins[0]['questions'][0]['question']['id']
        entry["category"] = \
            spins[0]['questions'][0]['question']['category']
        entry['answer'] = \
            spins[0]['questions'][0]['question']['correct_answer']
        entry["answer_type"] = spins[0]['type']

        if entry['answer_type'] == 'CROWN':
            entry['requested_crown'] = entry['category']

        return entry

    # Return list of games from login page
    def game_list(self):
        return self.__login_response['list']


joe = player()

# for solution in joe.solutions():
#     print "SOLUTION:", solution
#     if solution['answer_type'] == 'NORMAL':
#         print "submitted."
#         print joe.answer(**solution)

#     else:

for game in joe.game_list():

    solution = joe.solve(game)

    print "Solution", solution

    if solution is not None and len(solution.keys() ) > 3:
        print "submitted..."
        joe.answer(**solution)
    else:
        print game
        print "failed."
