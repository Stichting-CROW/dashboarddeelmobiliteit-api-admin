import requests
import os
import json
from fastapi import HTTPException


def create_consumer(user_id: str):
    base_url_kong_admin = os.getenv("BASE_URL_KONG_ADMIN")
    url = f"{base_url_kong_admin}/consumers"
    payload = json.dumps({
        'username': user_id
    })
    headers = {
        'Content-Type': 'application/json'
    }
    r = requests.request("POST", url, data=payload, headers=headers)
    if r.status_code != 201:
        raise HTTPException(status_code=500, detail="Something went wrong wen creating consumer, probably the consumer already existed.")