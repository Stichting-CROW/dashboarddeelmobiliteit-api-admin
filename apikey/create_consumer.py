import requests
import os
import json

def create_consumer(user_id: str):
    base_url_kong_admin = os.getenv("BASE_URL_KONG_ADMIN")
    url = base_url_kong_admin + "/consumers"
    payload = json.dumps({
        'username': user_id
    })
    headers = {
        'Content-Type': 'application/json'
    }
    r = requests.request("POST", url, payload=payload, headers=headers)
    if r.status_code != 201:
        raise HTTPException(status_code=500, detail="Something went wrong wen creating consumer, probably the consumer already existed.")