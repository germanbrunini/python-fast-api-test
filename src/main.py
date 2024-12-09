from random import randrange
from typing import Optional

from fastapi import FastAPI, Response, HTTPException, status
from pydantic import BaseModel

app = FastAPI()


class Post(BaseModel):
    title: str
    content: str
    publish: bool = True
    rating: Optional[int] = None


my_post = [
    {'title': 'this title 1', 'content': 'this content 1', 'id': 1},
    {'title': 'this title 2', 'content': 'this content 2', 'id': 2},
]


def hello():
    print('Hello world!!')


def find_post(id: int):
    for p in my_post:
        if p['id'] == id:
            return p


@app.get('/')
async def root():
    return 'Hello world!!!'


@app.get('/greet/{name}')
async def greet_name(name: str, age: int) -> dict:
    return {'message': f'Hello {name}!!!', 'age': age}


@app.get('/posts')
async def get_post():
    return {'data': my_post}


@app.get('/posts/latest')
async def get_latest_post():
    post = my_post[len(my_post) - 1]
    return {'latest_post': f'here is your latest {post}'}


@app.get('/posts/{id}')
async def get_post(id: int, response: Response):
    post = find_post(id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Item with id: {id} not found',
        )
    return {'post_detail': f'here is your post {post}'}


@app.post('/posts')
async def create_post(post: Post):
    post_dict = post.model_dump()
    post_dict['id'] = randrange(0, 10000000)
    my_post.append(post_dict)
    return {'data': post_dict}
