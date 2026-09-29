from fastapi.testclient import TestClient
from main import app
from limiter import limiter
limiter.enabled = False

client = TestClient(app)

def test_get():
     response = client.get("/todos/46")

     assert response.status_code == 200


def test_get_not_found():
     response = client.get("/todos/999999")

     assert response.status_code == 404

def test_post():
     response = client.post("/todos", json={"title": "c"})
     print(response.json())
     assert response.status_code == 200

     body = response.json()
     assert body["Msg"] == "todo created"
     assert body["Data"]["title"] == "c"
     assert body["Data"]["completed"] is False

def test_delete():
    response = client.delete("/todos/49")
    assert response.status_code == 200

    body = response.json()
    assert body["Msg"] == "Todo deleted"
    assert body["Data"]["title"] == "c"
    assert body["Data"]["completed"] is False


def test_update():
    response = client.put("/todos/48",json={"todo_id":48,"title":"pycharm","completed":True})
    assert response.status_code == 200
    

    body = response.json()
    assert body["Msg"] == "Todo updated"
    assert body["Data"]["id"] == 48
    assert body["Data"]["title"] == "pycharm"
    assert body["Data"]["completed"] == True