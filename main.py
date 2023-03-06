from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from acl import get_acl
from user import create_user, user_account, list_users, delete_user
from organisation import (
    create_organisation, organisation, delete_organisation, list_organisations,
    grant_view_data_access_organisation, grant_view_data_access_user,
    list_received_data_access, list_granted_data_access, revoke_view_data_access
)
from organisation.view_data_access import ViewDataAccessOrganisation, ViewDataAccessUser

app = FastAPI()

@app.middleware("http")
async def authorize(request: Request, call_next):
    result = get_acl.get_access(request=request)
    if not result:
        return JSONResponse(status_code=401, content={"reason": "user is not authorized"})
    request.state.acl = result
    response = await call_next(request)
    return response

@app.get("/user/acl", tags=["user"])
async def list_users_route(request: Request):
    return request.state.acl

@app.get("/user/list", tags=["user"])
async def list_users_route(request: Request, organisation_id: int | None = None):
    return list_users.list_users(request.state.acl, organisation_id=organisation_id)

@app.post("/user/create", tags=["user"], status_code=201)
async def create_user_route(user_account: user_account.UserAccount, request: Request):
    return create_user.create_user(request.state.acl, user_account_object=user_account)

@app.put("/user/update", tags=["user"])
async def update_user():
    return {"message": "Hello World"}

@app.delete("/user/delete", tags=["user"], status_code=204)
async def delete_user_route(user_id: str, request: Request):
    delete_user.delete_user(request.state.acl, user_id)

@app.get("/organisation/list", tags=["organisation"])
async def list_organisation_route():
    return list_organisations.list_organisations()

@app.get("/organisation/{organisation_id}", tags=["organisation"])
async def get_organisation_route(organisation_id):
    return {"message": organisation_id}

@app.post("/organisation/create", tags=["organisation"], status_code=201)
async def create_organisation_route(organisation: organisation.OrganisationWithDetails, request: Request):
    return create_organisation.create_organisation(request.state.acl, organisation)

@app.put("/organisation/update", tags=["organisation"])
async def update_organisation_route():
    return {"message": "Hello World"}

@app.delete("/organisation/delete/{organisation_id}", tags=["organisation"], status_code=204)
async def delete_organisation_route(organisation_id: str, request: Request):
    delete_organisation.delete_organisation(request.state.acl, organisation_id)

@app.post("/data_access/grant_organisation", tags=["data_access"], status_code=201)
async def grant_organisation_data_access_route(
        view_data_access: ViewDataAccessOrganisation, 
        request: Request
    ):
    return grant_view_data_access_organisation.grant_data_access_organisation(
        request.state.acl, view_data_access)
    
@app.post("/data_access/grant_user", tags=["data_access"], status_code=201)
async def grant_user_data_access_route(view_data_access: ViewDataAccessUser, request: Request):
    return grant_view_data_access_user.grant_data_access_user(
        request.state.acl, view_data_access=view_data_access)

@app.delete("/data_access/revoke/{grant_view_data_id}", tags=["data_access"], status_code=204)
async def revoke_data_access_route(grant_view_data_id: str, request: Request):
    revoke_view_data_access.revoke_data_access(request.state.acl, grant_view_data_id=grant_view_data_id)

@app.get("/data_access/list_granted/{organisation_id}", tags=["data_access"], status_code=200)
async def list_granted_data_access_route(organisation_id: str, request: Request):
    return list_granted_data_access.list_granted_data_access(
        request.state.acl, organisation_id)

@app.get("/data_access/list_received", tags=["data_access"], status_code=200)
async def list_received_data_access_route(request: Request):
    return list_received_data_access.list_received_data_access(request.state.acl)

@app.get("/organisation/yearly_cost_overview", tags=["organisation"])
async def root():
    return {"message": "Hello World"}

@app.get("/feed/list", tags=["feed"])
async def root():
    return {"message": "Hello World"}