from fastapi import APIRouter, status

router = APIRouter(
    prefix="/v1/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def get_users():
    return {"users": []}


@router.post("/")
def create_user(user):
    return {user}


@router.get("/{id}")
def get_user(id):
    return {id}


@router.put("/{id}")
def update_user(id):
    return {id}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user(id):
    return {"Message": "Removed user {id}"}


# More info https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/#oauth2passwordrequestform
@router.post("/login")
def login(form_data):
    return {"access_token": "omg, it's so secret!", "token_type": "bearer"}


@router.get("/me")
def get_me(current_user):
    return {current_user}


@router.put("/me")
def update_me(current_user):
    return {"Message": "Updated your account"}


@router.delete("/me")
def delete_me(current_user):
    # Logout as well
    return {"Message": "Deleted your account"}


@router.post("/logout")
def logout():
    return {"Message": "Logged out."}
