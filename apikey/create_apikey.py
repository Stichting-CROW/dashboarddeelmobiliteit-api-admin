from acl import acl
import os
import requests
from fastapi import HTTPException
from apikey import create_consumer, apikey

def call_create_apikey(username: str) -> apikey.Apikey:
    base_url_kong_admin = os.getenv("BASE_URL_KONG_ADMIN")
    url = f"{base_url_kong_admin}/consumers/{username}/key-auth"
    r = requests.request("POST", url)
    if r.status_code != 201:
        raise HTTPException(status_code=500, detail="Creating apikey not possible")
    res = r.text
    return apikey.Apikey.parse_raw(res)

def create_apikey(acl: acl.ACL) -> apikey.Apikey:
    result = None
    try:
        result = call_create_apikey(acl.user_id)
    except HTTPException:
        create_consumer.create_consumer(acl.user_id)
        result = call_create_apikey(acl.user_id)
    return result