from acl import acl
import os
import requests
from fastapi import HTTPException

def call_delete_apikey(username: str, apikey_id):
    base_url_kong_admin = os.getenv("BASE_URL_KONG_ADMIN")
    url = f"{base_url_kong_admin}/consumers/{username}/key-auth/{apikey_id}"
    r = requests.request("DELETE", url)
    if r.status_code == 404:
        raise HTTPException(status_code=404, detail="apikey doesn't exists or doesn't belong to this user.")
    if r.status_code != 204:
        raise HTTPException(status_code=r.status_code, detail=r.text)

def delete_apikey(acl: acl.ACL, apikey_id: str):
    call_delete_apikey(acl.user_id, apikey_id)