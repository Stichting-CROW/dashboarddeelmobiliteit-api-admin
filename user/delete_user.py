
import requests
import os

def delete_user_fusion_auth(email):
    base_url_fusionauth = os.getenv("BASE_URL_FUSIONAUTH")
    headers = {
        'Authorization': os.getenv("FUSIONAUTH_APIKEY")
    }
    url = base_url_fusionauth + "/api/user?email=%s" % email
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return "Something went wrong, user possibly doesn't exists."
    
    user_id = r.json()["user"]["id"]
    url = base_url_fusionauth + "/api/user/%s?hardDelete=true" % user_id
    r = requests.delete(url, headers=headers)
    if r.status_code != 200:
        return "Something went wrong with deleting user."
        
       