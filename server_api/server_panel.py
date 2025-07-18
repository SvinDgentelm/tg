import datetime
import json

import requests
import uuid

from decouple import config

class Panel:
    login=config('PANEL_LOGIN')
    password=config('PANEL_PASSWORD')
    hosts=config('HOSTS').split('||')
    header=[]
    data={'username': login, 'password': password}
    ses = requests.Session()
    self_link=config('SELF_LINK')

    def connect(self):
        
        for host in self.hosts:
            try:
                response = self.ses.post(f'{host}/login', data=self.data)
            except:
                print(f'ERROR CONNECTION TO {host}')

        return response
    

    def get_list(self):

        self.connect()
        resource = self.ses.get(f'{self.hosts[0]}/panel/api/inbounds/list', json=self.data).json()
        return resource
    
    def get_lists(self):

        response = []
        self.connect()

        for host in self.hosts:
            try:
                response.append((self.ses.get(f'{host}/panel/api/inbounds/list', json=self.data).json(),host.split('/')[2]))
            except:
                print(f"ERROR GET LISTS OF {host}")

        return response
    
    def add_client(self, user, days):

        self.connect()
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
                'subId': str(uuid.uuid1())
            }]
        })
        }
        
    
        
        for host in self.hosts:
            server_id = self.ses.get(f'{self.hosts[0]}/panel/api/inbounds/list', json=self.data).json()['obj'][0]['id']
            data1['id'] = server_id
            resource = self.ses.post(f'{host}/panel/api/inbounds/addClient', headers=header, json=data1)
        return resource
    
    def get_client(self, user_id):
        
        inbound = json.loads(self.get_list()['obj'][0]['settings'])

        for client in inbound['clients']:
            if client['tgId']==str(user_id):
                return client
            
    def get_client_by_subId(self, client_subId):
        
        inbound = json.loads(self.get_list()['obj'][0]['settings'])

        for client in inbound['clients']:
            if client['subId']==str(client_subId):
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
        
        for host in self.hosts:
            resource = self.ses.post(f"{host}/panel/api/inbounds/updateClient/{client['id']}", headers=header, json=data1)

        return resource
    

    def link(self, user_id: str):
        """
        Получение ссылки!
        :param user_id: str
        :return: str
        """
        client = self.get_client(user_id=user_id)

        val = f"{self.self_link}/connect_link/{client['subId']}/prestige_vpn"

        return val


    def del_client(self, user_id):

        client = self.get_client(user_id=user_id)
        server_id = self.get_list()['obj'][0]['id']

        header = {"Accept": "application/json"}

        for host in self.hosts:
            resource = self.ses.post(f"{host}/panel/api/inbounds/{server_id}/delClient/{client['id']}", headers=header)

        return resource
