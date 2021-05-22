import uuid
from hashlib import sha512
from typing import Optional
import uvicorn
import secrets
from fastapi import FastAPI, Request, Response, status, Depends, Cookie
from fastapi.exceptions import HTTPException
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from starlette.responses import  RedirectResponse
from message import Message

app = FastAPI()
app.username = "Someone"
app.password = "HisPa$$word007"
app.secret_key = "dfhbsrjke463gjgbhfr43yhygf76jkn"
app.access_token : Optional[str] = None
app.messages_list = []


def authentication_basic(credentials: HTTPBasicCredentials = Depends(HTTPBasic())):
    user_checked = secrets.compare_digest(credentials.username,app.username)
    password_checked = secrets.compare_digest(credentials.password,app.password)
    if not user_checked or not password_checked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")
    return True


def authentication_session(access_token: str = Cookie(None)):
    if app.access_token and access_token == app.access_token:
        return True
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect credentials")


@app.post("/login", status_code=201)
def create_session(request: Request, response:Response, auth: bool = Depends(authentication_basic)):
    token = sha512(bytes(f"{uuid.uuid4().hex}{app.secret_key}{request.headers['authorization']}","utf-8", )).hexdigest()
    setattr(app, "access_token", token)
    response.set_cookie(key="access_token", value=token)
    return {"message": "You are logged in"}


@app.get("/logged_out")
def logged_out():
    return {"message": "Logged out!"}


@app.delete("/logout")
def logout(auth: bool = Depends(authentication_session)):
    setattr(app, "access_token", None)
    response = RedirectResponse(url='/logged_out', status_code=status.HTTP_303_SEE_OTHER)
    return response


@app.post("/message", status_code=201)
def add_message(message: Message, auth: bool = Depends(authentication_session)):
    if len(message.message_text) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    len_list = len(app.messages_list)
    if len_list == 0:
        message.id = 0
    else:
        message.id = app.messages_list[len_list-1].id +1
    app.messages_list.append(message)
    return {"info": "message created", "id": message.id, "message text": message.message_text}


@app.get("/message/{id}")
def read_message(id: int):
    if not any(message.id == id for message in app.messages_list):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    for message in app.messages_list:
        if message.id == id:
            message.views_counter += 1
            return {"message": message.message_text, "amount of views": message.views_counter}


@app.put("/message/{id}")
def edit_message(id: int, new_message: Message,auth: bool = Depends(authentication_session)):
    if not any(message.id == id for message in app.messages_list):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    for message in app.messages_list:
        if message.id == id:
            message.views_counter = 0
            message.message_text = message.message_text + new_message.message_text
            return {"info": "message was edited","message": message.message_text, "amount of views": message.views_counter}


@app.delete("/message/{id}")
def delete_message(id: int, auth: bool = Depends(authentication_session)):
    if not any(message.id == id for message in app.messages_list):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    for message in app.messages_list:
        if message.id == id:
            app.messages_list.remove(message)
            return {"info": "message was deleted"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


