from fastapi import FastAPI

app = FastAPI()


def hello():
    print("Hello world!!")


@app.get("/")
def main():
    return "Hello world!!!"
