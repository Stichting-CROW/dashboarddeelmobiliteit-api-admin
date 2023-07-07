from fastapi import FastAPI, Request, Path
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Annotated
from acl import get_acl
from user import (
    create_user, user_account, list_users, delete_user, update_user
)
from organisation import (
    create_organisation, list_organisation_history, organisation, delete_organisation, list_organisations,
    grant_view_data_access_organisation, grant_view_data_access_user,
    list_received_data_access, list_granted_data_access, revoke_view_data_access,
    update_organisation, get_organisation
)
from apikey import (
    create_apikey, list_apikeys
)
from organisation.view_data_access import ViewDataAccessOrganisation, ViewDataAccessUser
from yearly_cost_overview import calculate_yearly_cost
from datetime import date


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
    print(request.state.acl.privileges)
    return request.state.acl

@app.get("/user/list", tags=["user"])
async def list_users_route(request: Request, organisation_id: int | None = None):
    return list_users.list_users(request.state.acl, organisation_id=organisation_id)

@app.post("/user/create", tags=["user"], status_code=201)
async def create_user_route(user_account: user_account.UserAccount, request: Request):
    return create_user.create_user(request.state.acl, user_account_object=user_account)

@app.put("/user/update", tags=["user"])
async def update_user_route(user_account: user_account.UserAccount, request: Request):
    return update_user.update_user(request.state.acl, user_account)

@app.delete("/user/delete", tags=["user"], status_code=204)
async def delete_user_route(user_id: str, request: Request):
    delete_user.delete_user(request.state.acl, user_id)

@app.get("/organisation/list", tags=["organisation"])
async def list_organisation_route():
    return list_organisations.list_organisations()

@app.get("/organisation", tags=["organisation"])
async def get_organisation_route(request: Request, organisation_id: int | None = None):
    return get_organisation.get_organisation(organisation_id, request.state.acl)

@app.post("/organisation/create", tags=["organisation"], status_code=201)
async def create_organisation_route(organisation: organisation.OrganisationWithDetails, request: Request):
    return create_organisation.create_organisation(request.state.acl, organisation)

@app.put("/organisation/update", tags=["organisation"])
async def update_organisation_route(organisation: organisation.OrganisationWithDetails, request: Request):
    return update_organisation.update_organisation(request.state.acl, organisation)

@app.delete("/organisation/delete/{organisation_id}", tags=["organisation"], status_code=204)
async def delete_organisation_route(
        organisation_id: Annotated[int, Path(title="The ID of the organisation you like to delete.")],
        request: Request
    ):
    delete_organisation.delete_organisation(request.state.acl, organisation_id)

@app.get("/organisation/details_history/{organisation_id}", tags=["organisation"])
async def list_organisation_details_history_route(
        organisation_id: Annotated[int, Path(title="The ID of the organisation you like to see more history off.")],
        request: Request
    ):
    return list_organisation_history.list_organisation_detail_history(request.state.acl, organisation_id=organisation_id)

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
async def revoke_data_access_route(
        grant_view_data_id: Annotated[int, Path(title="The ID of the granted_view you would like to remove.")],
        request: Request
    ):
    revoke_view_data_access.revoke_data_access(request.state.acl, grant_view_data_id=grant_view_data_id)

@app.get("/data_access/list_granted/{organisation_id}", tags=["data_access"], status_code=200)
async def list_granted_data_access_route(
    organisation_id: Annotated[int, Path(title="The ID of the organisation you like to receive granted data access from.")], 
    request: Request):
    return list_granted_data_access.list_granted_data_access(
        request.state.acl, organisation_id)

@app.get("/data_access/list_received", tags=["data_access"], status_code=200)
async def list_received_data_access_route(request: Request):
    return list_received_data_access.list_received_data_access(request.state.acl)

@app.get("/organisation/yearly_cost_overview", tags=["organisation"])
async def calculate_yearly_cost_overview(reference_date: date, request: Request):
    excel_sheet = calculate_yearly_cost.calculate(request.state.acl, reference_date)
    file_name = "jaarlijkse_kosten_overzicht_peil_datum_{}.xlsx".format(reference_date.isoformat())
    return StreamingResponse(
        excel_sheet, 
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={'Content-Disposition': 'attachment; filename="{}"'.format(file_name)}
    )

@app.get("/apikey/list", tags=["apikey"])
async def list_apikeys_route(request: Request):
    return list_apikeys.list_apikeys(request.state.acl)

@app.post("/apikey/create", tags=["apikey"], status_code=201)
async def create_apikey_route(request: Request):
    return create_apikey.create_apikey(request.state.acl)

# @app.delete("/apikey/delete", tags=["apikey"], status_code=204)
# async def delete_apikey(apikey_id: str, request: Request):
#     #delete_user.delete_user(request.state.acl, user_id)

@app.get("/feed/list", tags=["feed"])
async def root():
    return {"message": "Hello World"}