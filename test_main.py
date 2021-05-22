from fastapi.testclient import TestClient
from requests.auth import HTTPBasicAuth

from main import app

client = TestClient(app)


def test_login():
    auth = HTTPBasicAuth(username="Someone", password="HisPa$$word007")
    response = client.post("/login", auth=auth)
    assert response.status_code == 201, response.text
    assert response.json() == {"message": "You are logged in"}


def test_login_no_credentials():
    response = client.post("/login")
    assert response.status_code == 401, response.text
    assert response.json() == {"detail": "Not authenticated"}


def test_login_invalid_credentials():
    auth = HTTPBasicAuth(username="NoUser", password="NoPassword")
    response = client.post("/login", auth=auth)
    assert response.status_code == 401, response.text
    assert response.json() == {"detail": "Incorrect credentials"}


def test_login_logout():
    auth = HTTPBasicAuth(username="Someone", password="HisPa$$word007")
    response = client.post("/login", auth=auth)
    assert response.status_code == 201, response.text
    assert response.json() == {"message": "You are logged in"}
    response1 = client.delete("/logout")
    assert response1.is_redirect is True
    assert response1.status_code == 303, response1.text


def test_logout_invalid_no_credentials():
    response1 = client.delete("/logout")
    assert response1.json() == {"detail": "Incorrect credentials"}
    assert response1.status_code == 401, response1.text


def test_add_message_with_no_auth():
    response_add = client.post("/message", json={"message_text": "Hello Ron!"})
    assert response_add.status_code == 401, response_add.text
    assert response_add.json() == {"detail": "Incorrect credentials"}


def test_add_message_with_auth():
    auth = HTTPBasicAuth(username="Someone", password="HisPa$$word007")
    client.post("/login", auth=auth)

    response_add = client.post("/message", json={"message_text": "Hello Ron!"})
    assert response_add.status_code == 201, response_add.text
    assert response_add.json() == {"info": "message created", "id": app.messages_list[-1].id,
                                   "message text": app.messages_list[-1].message_text}

    client.delete("/logout")


def test_add_empty_message_with_auth():
    auth = HTTPBasicAuth(username="Someone", password="HisPa$$word007")
    client.post("/login", auth=auth)

    response_add = client.post("/message", json={"message_text": ""})
    assert response_add.status_code == 400, response_add.text
    assert response_add.json() == {"detail": "Bad Request"}

    response1 = client.delete("/logout")


def test_add_gt160signs_message_with_auth():
    auth = HTTPBasicAuth(username="Someone", password="HisPa$$word007")
    client.post("/login", auth=auth)

    message = "Harry Potter is a series of seven fantasy novels written by British author J. K. Rowling. The novels " \
              "chronicle the lives of a young wizard, Harry Potter, and his friends Hermione Granger and Ron Weasley, " \
              "all of whom are students at Hogwarts School of Witchcraft and Wizardry. The main story arc concerns " \
              "Harry's struggle against Lord Voldemort, a dark wizard who intends to become immortal, overthrow the " \
              "wizard governing body known as the Ministry of Magic and subjugate all wizards and Muggles (" \
              "non-magical people). "
    response_add = client.post("/message", json={"message_text": message})
    assert response_add.status_code == 400, response_add.text
    assert response_add.json() == {"detail": "Bad Request"}

    response1 = client.delete("/logout")


def test_read_message_no_auth():
    auth = HTTPBasicAuth(username="Someone", password="HisPa$$word007")
    client.post("/login", auth=auth)
    client.post("/message", json={"message_text": "test_read_message_no_auth"})
    client.delete("/logout")
    response = client.get("/message/" + str(app.messages_list[-1].id))
    assert response.status_code == 200, response.text
    assert response.json() == {"message": "test_read_message_no_auth", "amount of views": 1}


def test_read_not_existing_message_no_auth():
    response = client.get("/message/666")
    assert response.status_code == 404, response.text
    assert response.json() == {"detail": "Not Found"}


def test_read_message_auth():
    auth = HTTPBasicAuth(username="Someone", password="HisPa$$word007")
    client.post("/login", auth=auth)
    client.post("/message", json={"message_text": "test_read_message_auth"})

    response = client.get("/message/" + str(app.messages_list[-1].id))
    assert response.status_code == 200, response.text
    assert response.json() == {"message": "test_read_message_auth", "amount of views": 1}

    client.delete("/logout")


def test_read_not_existing_message_auth():
    auth = HTTPBasicAuth(username="Someone", password="HisPa$$word007")
    client.post("/login", auth=auth)

    response = client.get("/message/666")
    assert response.status_code == 404, response.text
    assert response.json() == {"detail": "Not Found"}

    client.delete("/logout")


def test_read_check_views():
    auth = HTTPBasicAuth(username="Someone", password="HisPa$$word007")
    client.post("/login", auth=auth)
    client.post("/message", json={"message_text": "test_read_check_views"})
    client.delete("/logout")
    for i in range(1, 5):
        response = client.get("/message/" + str(app.messages_list[-1].id))
        assert response.status_code == 200, response.text
        assert response.json() == {"message": "test_read_check_views", "amount of views": i}


def test_edit_with_auth():
    message = "test_edit_with_auth"
    edition = "How are you?"
    auth = HTTPBasicAuth(username="Someone", password="HisPa$$word007")
    client.post("/login", auth=auth)
    client.post("/message", json={"message_text": message})

    response = client.put("/message/" + str(app.messages_list[-1].id), json={"message_text": edition})
    assert response.status_code == 200, response.text
    assert response.json() == {"info": "message was edited", "message": message + edition, "amount of views": 0}

    client.delete("/logout")


def test_edit_gt160signs_with_auth():
    message = "test_edit_with_auth"
    edition = "Harry Potter is a series of seven fantasy novels written by British author J. K. Rowling. The novels " \
              "chronicle the lives of a young wizard, Harry Potter, and his friends Hermione Granger and Ron Weasley, " \
              "all of whom are students at Hogwarts School of Witchcraft and Wizardry. The main story arc concerns " \
              "Harry's struggle against Lord Voldemort, a dark wizard who intends to become immortal, overthrow the " \
              "wizard governing body known as the Ministry of Magic and subjugate all wizards and Muggles (" \
              "non-magical people). "
    auth = HTTPBasicAuth(username="Someone", password="HisPa$$word007")
    client.post("/login", auth=auth)
    client.post("/message", json={"message_text": message})

    response = client.put("/message/" + str(app.messages_list[-1].id), json={"message_text": edition})
    assert response.status_code == 400, response.text
    assert response.json() == {"detail": "Bad Request"}

    client.delete("/logout")


def test_edit_not_existing_with_auth():
    auth = HTTPBasicAuth(username="Someone", password="HisPa$$word007")
    client.post("/login", auth=auth)

    response = client.put("/message/666", json={"message_text": "edition"})
    assert response.status_code == 404, response.text
    assert response.json() == {"detail": "Not Found"}

    client.delete("/logout")


def test_edit_no_auth():
    message = "test_edit_with_auth"
    edition = "How are you?"
    auth = HTTPBasicAuth(username="Someone", password="HisPa$$word007")
    client.post("/login", auth=auth)
    client.post("/message", json={"message_text": message})
    client.delete("/logout")

    response = client.put("/message/" + str(app.messages_list[-1].id), json={"message_text": edition})
    assert response.status_code == 401, response.text
    assert response.json() == {"detail": "Incorrect credentials"}


def test_delete_with_auth():
    message = "test_delete_with_auth"
    auth = HTTPBasicAuth(username="Someone", password="HisPa$$word007")
    client.post("/login", auth=auth)
    client.post("/message", json={"message_text": message})

    response = client.delete("/message/" + str(app.messages_list[-1].id))
    assert response.status_code == 200, response.text
    assert response.json() == {"info": "message was deleted"}

    client.delete("/logout")


def test_delete_not_existing_with_auth():
    auth = HTTPBasicAuth(username="Someone", password="HisPa$$word007")
    client.post("/login", auth=auth)

    response = client.delete("/message/666")
    assert response.status_code == 404, response.text
    assert response.json() == {"detail": "Not Found"}

    client.delete("/logout")


def test_delete_no_auth():
    message = "test_delete_no_auth"
    auth = HTTPBasicAuth(username="Someone", password="HisPa$$word007")
    client.post("/login", auth=auth)
    client.post("/message", json={"message_text": message})
    client.delete("/logout")

    response = client.delete("/message/" + str(app.messages_list[-1].id))
    assert response.status_code == 401, response.text
    assert response.json() == {"detail": "Incorrect credentials"}
