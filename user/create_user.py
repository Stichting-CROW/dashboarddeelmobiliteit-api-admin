import os
import random
import string
import requests
import json
from user import user_account, db
from acl import acl
from fastapi import HTTPException

def is_allowed_to_create_user(acl: acl.ACL, user_account: user_account.UserAccount):
    if (acl.is_admin == True):
        return True
    if ("ORGANISATION_ADMIN" in acl.privileges and acl.part_of_organisation == user_account.organisation_id):
        return True
    
    return False

def create_user(acl: acl.ACL, user_account_object: user_account.UserAccount):
    user_account_object.user_id = user_account_object.user_id.lower()
    if not is_allowed_to_create_user(acl, user_account_object):
        raise HTTPException(status_code=403, detail="user not authorized to create user for this organisation")
    result_create_fusionauth = create_user_fusionauth(user_account_object.user_id)
    if not result_create_fusionauth:
        raise HTTPException(status_code=400, detail="user already exists in fusionauth")
    result_db = db.create_user(user_account=user_account_object)
    if not result_db:
        raise HTTPException(status_code=400, detail="user already exists in db")
    return user_account.UserAccountSuccesfullyCreated(
        user_account=user_account_object,
        generated_password=result_create_fusionauth
    )

def random_string_generator(size=10, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def create_user_fusionauth(email):
    base_url_fusionauth = os.getenv("BASE_URL_FUSIONAUTH")
    headers = {
        'Authorization': os.getenv("FUSIONAUTH_APIKEY"),
        'Content-Type': 'application/json'
    }

    create_user_data = {}
    create_user_data["user"] = {}
    create_user_data["user"]["username"] = email
    create_user_data["user"]["email"] = email
    create_user_data["user"]["password"] = random_string_generator(12)

    r = requests.post(
        base_url_fusionauth + "/api/user", 
        headers=headers, 
        data=json.dumps(create_user_data)
    )
    if r.status_code != 200:
        return False

    response_user = r.json()
    assign_application = {}
    assign_application["registration"] = {}
    assign_application["registration"]["applicationId"] = os.getenv("APP_ID")
    assign_application["registration"]["roles"] = ["default_user"]

    r = requests.post(base_url_fusionauth + "/api/user/registration/" + response_user["user"]["id"], headers=headers, data=json.dumps(assign_application))
    if r.status_code != 200:
        return False
    return create_user_data["user"]["password"]