import os
import requests
import json
from user import user_account, db
from acl import acl
from fastapi import HTTPException


def is_allowed_to_create_user(acl: acl.ACL, user_account: user_account.UserAccount):
    if (acl.is_admin == True):
        return True
    if ("ORGANISATION_ADMIN" in acl.privileges and (acl.part_of_organisation == user_account.organisation_id or user_account.organisation_id == 2)):
        return True
    
    return False


def create_user(acl: acl.ACL, user_account_object: user_account.UserAccount):
    user_account_object.user_id = user_account_object.user_id.lower()
    if not is_allowed_to_create_user(acl, user_account_object):
        raise HTTPException(status_code=403, detail="user not authorized to create user for this organisation")

    # Creates the FusionAuth user + app registration and sends FusionAuth's
    # Setup Password email (separate from the Forgot Password template used
    # by "Wachtwoord vergeten?").
    fusionauth_user_id = create_user_fusionauth(user_account_object.user_id)
    if not fusionauth_user_id:
        raise HTTPException(status_code=400, detail="user already exists in fusionauth")

    result_db = db.create_user(user_account=user_account_object)
    if not result_db:
        raise HTTPException(status_code=400, detail="user already exists in db")

    return user_account.UserAccountSuccesfullyCreated(
        user_account=user_account_object,
        # FusionAuth owns the Setup Password email body; the frontend only
        # needs to know that sending was requested successfully.
        email_text="",
        email_sent=True
    )


def create_user_fusionauth(email):
    """Create the user and application registration in one request so the
    Application-level Setup Password template is used when configured.

    Requires Tenants/Applications -> Email -> Setup password to have a
    template selected (not "Feature disabled").
    """
    base_url_fusionauth = os.getenv("BASE_URL_FUSIONAUTH")
    headers = {
        'Authorization': os.getenv("FUSIONAUTH_APIKEY"),
        'Content-Type': 'application/json'
    }

    # Combined User + Registration create. sendSetPasswordEmail causes
    # FusionAuth to ignore any password and email the Setup Password
    # template with a changePasswordId link.
    create_data = {
        "sendSetPasswordEmail": True,
        "user": {
            "username": email,
            "email": email
        },
        "registration": {
            "applicationId": os.getenv("APP_ID"),
            "roles": ["default_user"]
        }
    }

    r = requests.post(
        base_url_fusionauth + "/api/user/registration",
        headers=headers,
        data=json.dumps(create_data)
    )
    if r.status_code != 200:
        return False

    response = r.json()
    return response.get("user", {}).get("id")
