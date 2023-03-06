
import requests
import os
from user import db
from acl import acl
from fastapi import HTTPException
import urllib.parse

def is_allowed_to_delete_user(acl: acl.ACL, to_delete_user_id: str, user_organisation_id: str):
    if (acl.is_admin == True):
        return True
    if ("ORGANISATION_ADMIN" in acl.privileges 
        and acl.organisation_id == user_organisation_id and acl.user_id != to_delete_user_id):
        return True
    return False

def delete_user(acl: acl.ACL, user_id: str):
    user_id = user_id.lower()
    user_row = db.get_user(user_id)
    
    if not user_row:
        raise HTTPException(status_code=404, detail="user doesn't exist")
    if not is_allowed_to_delete_user(acl, to_delete_user_id=user_id, user_organisation_id=user_row["organisation_id"]):
        raise HTTPException(status_code=403, detail="user not authorized to delete user for this organisation, or tries to delete itselves which is not allowed.")
    
    delete_user_fusion_auth(user_id)
    result_db = db.delete_user(user_id=user_id)
    if not result_db:
        raise HTTPException(status_code=500, detail="deleting user from database went wrong.")
    
def delete_user_fusion_auth(email):
    base_url_fusionauth = os.getenv("BASE_URL_FUSIONAUTH")
    headers = {
        'Authorization': os.getenv("FUSIONAUTH_APIKEY")
    }
    url = "{}/api/user?email={}".format(base_url_fusionauth, urllib.parse.quote(email))
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        raise HTTPException(status_code=404, detail="user doesn't exists in fusionauth")
    
    user_id = r.json()["user"]["id"]
    url = "{}/api/user/{}?hardDelete=true".format(base_url_fusionauth, user_id)
    r = requests.delete(url, headers=headers)
    if r.status_code != 200:
        raise HTTPException(status_code=404, detail="something went wrong with deleting user from fusionauth")
        
       