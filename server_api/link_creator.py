from fastapi import FastAPI, Response
from server_api.server_panel import Panel
import json

app = FastAPI()
panel = Panel()

@app.get("/connect_link/{client_subId}")
async def read_item(client_subId):

    links = []
    client = panel.get_client_by_subId(client_subId=client_subId)
    servers = panel.get_lists()

    for item in servers:     
        server = json.loads(item[0]['obj'][0]['streamSettings'])
        ip = item[1].split(':')[0]
        
        links.append(f"vless://{client['id']}@{ip}:443?type={server['network']}&security={server['security']}&pbk={server['realitySettings']['settings']['publicKey']}&fp={server['realitySettings']['settings']['fingerprint']}&sni=yahoo.com&sid={server['realitySettings']['shortIds'][0]}&spx=%2F&flow={client['flow']}#{client['email']} ")
        response = '\n'.join(links)

    return Response(content=response, media_type="text/plain")