from fastapi import FastAPI
from .models import Item

app = FastAPI()


@app.get("/health")
def healthcheck():
    return {"status": "ok"}


@app.post("/items")
def create_item(item: Item):
    return {"message": "Item created", "item": item}
