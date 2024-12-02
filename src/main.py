from fastapi import FastAPI

app = FastAPI()


def hello():
    print("Hello world!!")


@app.get("/")
async def read_route():
    return "Hello world!!!"


@app.get("/greet/{name}")
async def greet_name(name: str) -> dict:
    return {"message": f"Helllo {name}!!!"}
