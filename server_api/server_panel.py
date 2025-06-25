import datetime
import json

import requests
import uuid

from decouple import config

class Panel:
    login=config('PANEL_LOGIN')
    password=config('PANEL_PASSWORD')
    host='http://193.43.79.128:60345/HJZqfcu0HnGOagI'

    header=[]
    data={'username': login, 'password': password}
    ses = requests.Session()

    def test_connect(self):
        return self.ses.post(f'{self.host}/login', data=self.data)
    

    def get_list(self):
        resource = self.ses.get(f'{self.host}/panel/api/inbounds/list', json=self.data).json()
        return resource
    
    def add_client(self, user, days):

        epoch = datetime.datetime.utcfromtimestamp(0)
        x_time = int((datetime.datetime.now() - epoch).total_seconds() * 1000)
        x_time += 86400000 * (days + 3) - 10800000

        header = {"Accept": "application/json"}
        
        data1 = {
        "id": 1,
        "settings": json.dumps({
            "clients": [{
                'id': str(uuid.uuid1()),
                'alterId': str(uuid.uuid1()),
                'email': str(user[1]),
                'limitIp': 3,
                'totalGB': 0,
                'flow': 'xtls-rprx-vision',
                'expiryTime': x_time,
                'enable': True,
                'tgId': str(user[2]),
                'subId': ''
            }]
        })
        }
        resource = self.ses.post(f'{self.host}/panel/api/inbounds/addClient', headers=header, json=data1)
        return resource
    
    def get_client(self, user_id):
        
        inbound = json.loads(self.get_list()['obj'][0]['settings'])

        for client in inbound['clients']:
            if client['tgId']==str(user_id):
                return client

    def updateClientDate(self, days, user_id):
        client = self.get_client(user_id)

        epoch = datetime.datetime.utcfromtimestamp(0)
        x_time = int((datetime.datetime.now() - epoch).total_seconds() * 1000)
        x_time += 86400000 * (days + 3) - 10800000

        header = {"Accept": "application/json"}
        data1 = {
        "id": 1,
        "settings": json.dumps({
            "clients": [{
                'id': str(client['id']),
                'alterId': str(client['alterId']),
                'email': str(client['email']),
                'limitIp': client['limitIp'],
                'totalGB': client['totalGB'],
                'flow': str(client['flow']),
                'expiryTime': x_time,
                'enable': True,
                'tgId': str(client['tgId']),
                'subId': str(client['subId'])
            }]
        })
        }

        resource = self.ses.post(f'{self.host}/panel/api/inbounds/updateClient/{client['id']}', headers=header, json=data1)
        return resource
    

    def link(self, user_id: str):
        """
        Получение ссылки!
        :param user_id: str
        :return: str
        """
        client = self.get_client(user_id=user_id)
        server = json.loads(self.get_list()['obj'][0]['streamSettings'])

        val = f"vless://{client['id']}@193.43.79.128:443?type={server['network']}&security={server['security']}&pbk=-u3NJd0hO66GP31UO5MVuriBIbgBzMu7ajsXeuwFeCw&fp=chrome&sni=yahoo.com&sid=e7ec&spx=%2F&flow={client['flow']}#{client['email']}"

        return val


    def del_client(self, user_id):

        client = self.get_client(user_id=user_id)
        server_id = self.get_list()['obj'][0]['id']

        header = {"Accept": "application/json"}

        resource = self.ses.post(f'{self.host}/panel/api/inbounds/{server_id}/delClient/{client['id']}', headers=header)
        return resource


    def time_active(self, user_id: str):
        dict_x = {}
        epoch = datetime.datetime.utcfromtimestamp(0)
        x_time = int((datetime.datetime.now() - epoch).total_seconds() * 1000.0)
        y = json.loads(self.get_list()['obj'][0]['settings'])
        for i in y["clients"]:
            if i['tgId'] == user_id:
                if i['enable'] and i['expiryTime'] > x_time:
                    dict_x[i['id']] = i['expiryTime']
                    return dict_x
                else:
                    dict_x[i['id']] = '0'
                    return dict_x
            if len(dict_x) == 0:
                dict_x['0'] = '0'
        
        return dict_x
    
    def activ(self, user_id: str):
        """
        Проверка активности подписки
        :param user_id: str
        :return: str
        """
        dict_x = {}
        epoch = datetime.datetime.utcfromtimestamp(0)
        x_time = int((datetime.datetime.now() - epoch).total_seconds() * 1000.0)
        y = json.loads(self.get_list()['obj'][0]['settings'])
        for i in y["clients"]:
            if i['tgId'] == user_id:
                if i['enable'] and i['expiryTime'] > x_time:
                    print(i)
                    print(i['enable'])
                    dict_x['activ'] = 'Активен'
                    ts = i['expiryTime']
                    ts /= 1000
                    ts += 10800
                    dict_x['time'] = datetime.datetime.utcfromtimestamp(ts).strftime('%d-%m-%Y %H:%M') + ' МСК'

                else:
                    print(i)
                    print(i['enable'])
                    dict_x['activ'] = 'Не Активен'
                    ts = i['expiryTime']
                    ts /= 1000
                    ts += 10800
                    dict_x['time'] = datetime.datetime.utcfromtimestamp(ts).strftime('%d-%m-%Y %H:%M') + ' МСК'

            else:
                dict_x['activ'] = 'Не зарегистрирован'
                dict_x['time'] = '-'

        return dict_x
