import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class UserRequest(BaseModel):
    name: str


@app.get("/")
def hello():
    return {"message": "Hello World"}


@app.post("/greet")
def greet(request: UserRequest):
    return {
        "message": f"Thank you {request.name}"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)