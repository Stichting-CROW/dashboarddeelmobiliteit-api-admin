from acl import acl
import os
import requests
from fastapi import HTTPException

def call_delete_consumer(username: str):
    base_url_kong_admin = os.getenv("BASE_URL_KONG_ADMIN")
    url = f"{base_url_kong_admin}/consumers/{username}"
    print(url)
    r = requests.request("DELETE", url)
    print(r.text)
    if r.status_code != 204:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    print(r.text)

def delete_consumer(username: str):
    call_delete_consumer(username)