from acl import acl
import os
import requests
from fastapi import HTTPException
from apikey import create_consumer, apikey
from typing import List

from pydantic import BaseModel

class ApikeyListing(BaseModel):
    data: List[apikey.Apikey]

def call_list_apikeys(username: str) -> List[apikey.Apikey]:
    base_url_kong_admin = os.getenv("BASE_URL_KONG_ADMIN")
    url = base_url_kong_admin + f"/consumers/{username}/key-auth"
    r = requests.request("GET", url)
    if r.status_code != 200:
        print(r.text)
        raise HTTPException(status_code=500, detail="Listing apikeys not possible")
    res = r.text
    return ApikeyListing.parse_raw(res).data

def list_apikeys(acl: acl.ACL) -> List[apikey.Apikey]:
    result = None
    try:
        result = call_list_apikeys(acl.user_id)
    except HTTPException:
        create_consumer.create_consumer(acl.user_id)
        result = call_list_apikeys(acl.user_id)
    return result