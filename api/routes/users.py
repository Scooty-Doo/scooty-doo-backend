"""Module for the /users routes"""

from fastapi import APIRouter, status

router = APIRouter(
    prefix="/v1/users",
    tags=["users"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def get_users():
    """Gets all users in admin format."""
    return {"users": []}


@router.post("/")
def create_user(user):
    """Creates a user."""
    return {user}


@router.get("/{user_id}")
def get_user(user_id):
    """Gets a specific user from the database."""
    return {user_id}


# Used to get a users trips
@router.get("/trips/{user_id}")
def get_users_trips(user_id):
    """Gets all of a users trips."""
    return {user_id}


@router.put("/{user_id}")
def update_user(user_id):
    """Updates a user."""
    return {user_id}


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_user(user_id):
    """Removes a user."""
    return {"Message": "Removed user {user_id}"}


# More info https://fastapi.tiangolo.com/tutorial/security/simple-oauth2/#oauth2passwordrequestform
@router.post("/login")
def login(form_data):
    """Logs in a user with oauth2 and returns a token on success."""
    return {"access_token": "omg, it's so secret!", "token_type": "bearer"}


@router.get("/me")
def get_me(current_user):
    """Gets the current users details."""
    return {current_user}


@router.put("/me")
def update_me(current_user):
    """Updates the current users account."""
    return {"Message": "Updated your account"}


@router.delete("/me")
def delete_me(current_user):
    """Deletes a user account and logs them out."""
    # Logout as well
    return {"Message": "Deleted your account"}


@router.post("/logout")
def logout():
    """Logs a user out."""
    return {"Message": "Logged out."}
