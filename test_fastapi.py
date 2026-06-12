from fastapi.testclient import TestClient
from app.routes.app import app

client = TestClient(app)
response = client.get("/api/v1/products/?page=1")
print(response.status_code)
print(response.text)
