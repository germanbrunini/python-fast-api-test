from fastapi import FastAPI, Response, HTTPException, status
from random import randrange
from typing import List, Optional
import psycopg
from psycopg.rows import dict_row  # Import the row factory for dictionaries
from psycopg.pool import AsyncConnectionPool
from pydantic import BaseModel, field_validator
import time
import asyncio


# Detailed description of the API using Markdown
description = """
**MyFastAPIProj** API allows you to manage posts efficiently. 🚀

## Posts

- **Read posts**: Retrieve a list of all posts.
- **Create posts**: Add a new post.

## Users

- **Create users** (_not implemented_).
- **Read users** (_not implemented_).
"""

# Initialize the FastAPI application with metadata
app = FastAPI(
    title='MyFastAPIProj',
    description=description,
    summary='playing around with an API to manage posts and users.',
    version='0.1.0',
    terms_of_service='http://example.com/terms/',
    contact={
        'name': 'German Brunini',
        'url': 'http://example.com/contact/',
        'email': 'bruninigerman@gmail.com',
    },
    license_info={
        'name': 'MIT License',
        'url': 'https://opensource.org/licenses/MIT',
    },
)

# --------- Configuration ---------
HOST = 'localhost'
PT = '5433'
DBN = 'postgres'
USER = 'postgres'
PASS = 'germanpostgres1'


# Define your connection parameters
DB_CONFIG = f'host={HOST} port={PT} dbname={DBN} user={USER} password={PASS}'

# Retry connection until successful
while True:
    try:
        with psycopg.connect(
            DB_CONFIG, row_factory=dict_row
        ) as conn:  # Use dict_row factory
            print('Connection successful')

            with conn.cursor() as cursor:
                cursor.execute(
                    'SELECT id, title, content, published FROM public.posts ORDER BY id ASC;'
                )
                rows = cursor.fetchall()

                # Each row is now a dictionary
                for row in rows:
                    print(
                        f"ID: {row['id']}, Title: {row['title']}, Published: {row['published']}"
                    )
                    print(f"Content: {row['content']}\n")

            break  # Exit the loop if connection and query are successful

    except psycopg.OperationalError as e:
        print(f'Operational error occurred: {e}')
        time.sleep(5)  # Wait for 5 seconds before retrying

    except Exception as e:
        print(f'An unexpected error occurred: {e}')
        break  # If it's a critical error, you may want to stop retrying


# --------- Pydantic Models ---------
class Post(BaseModel):
    # id: int
    title: str
    content: str
    published: bool = True

    # rating: Optional[int] = None
    # @field_validator('rating')
    # def validate_rating(cls, value):
    #    """
    #    Ensure that the rating is between 1 and 5 if provided.
    #
    #    Args:
    #        value (Optional[int]): The rating value to validate.
    #
    #    Returns:
    #        Optional[int]: The validated rating.
    #
    #    Raises:
    #        ValueError: If the rating is not between 1 and 5.
    #    """
    #    if value is not None:
    #        if not (1 <= value <= 5):
    #            raise ValueError('Rating must be between 1 and 5.')
    #    return value


class PostCreate(BaseModel):
    title: str
    content: str
    publish: bool = True


# Response model for /posts endpoint
class PostsResponse(BaseModel):
    data: List[Post]


my_post = [
    {'title': 'this title 1', 'content': 'this content 1', 'id': 1},
    {'title': 'this title 2', 'content': 'this content 2', 'id': 2},
]


def hello():
    """
    Print a greeting message to the console.

    This function outputs a simple "Hello world!!" message.
    """
    print('Hello world!!')


def find_post(id: int):
    """
    Retrieve a post by its ID.

    Iterates through the `my_post` list to find a post matching the provided ID.

    Args:
        id (int): The unique identifier of the post to retrieve.

    Returns:
        dict or None: The post dictionary if found; otherwise, `None`.
    """
    for p in my_post:
        if p['id'] == id:
            return p


def find_post_index(id: int) -> int | None:
    """
    Find the index of a post by its ID.

    Args:
        id (int): The unique identifier of the post.

    Returns:
        int | None: The index of the post in `my_post` if found; otherwise, `None`.
    """
    for index, post in enumerate(my_post):
        if post['id'] == id:
            return index
    return None


@app.get('/')
async def root():
    """
    Root endpoint returning a welcome message.

    Returns:
        str: A simple "Hello world!!!" greeting.
    """
    return 'Hello world!!!'


@app.get('/greet/{name}')
async def greet_name(name: str, age: int) -> dict:
    """
    Greet a user by name and acknowledge their age.
    Constructs a personalized greeting message including the user's name and age.

    Args:
        name (str): The name of the user to greet.
        age (int): The age of the user.

    Returns:
        dict: A dictionary containing the greeting message and age.
            Example:
                {
                    "message": "Hello John!!!",
                    "age": 30
                }
    """
    return {'message': f'Hello {name}!!!', 'age': age}


@app.get('/posts')
async def get_post():
    """
    Retrieve all posts.
    Fetches and returns the list of all posts stored in `my_post`.

    Returns:
        dict: A dictionary containing the list of posts.
            Example:
                {
                    "data": [
                        {"id": 1, "title": "First Post", "content": "This is the first post."},
                        ...
                    ]
                }
    """
    return {'data': my_post}


@app.get('/posts/latest')
async def get_latest_post():
    """
    Retrieve the latest post.

    Fetches the most recent post from `my_post` and returns it.

    Returns:
        dict: A dictionary containing the latest post.
            Example:
                {
                    "latest_post": "here is your latest {'id': 2, 'title': 'Second Post', ...}"
                }
    """
    post = my_post[-1]  # Simplified index access
    return {'latest_post': f'here is your latest {post}'}


@app.get('/posts/{id}')
async def get_post_by_id(id: int) -> dict[str, str]:
    """
    Retrieve a specific post by its ID.

    Searches for a post with the given ID. If found, returns the post details.
    If not found, raises a 404 HTTP exception.

    Args:
        id (int): The unique identifier of the post to retrieve.

    Returns:
        dict[str, str]: A dictionary containing the post details.
            Example:
                {
                    "post_detail": "here is your post {'id': 1, 'title': 'First Post', ...}"
                }

    Raises:
        HTTPException: If no post with the specified ID is found.
            - status_code: 404 NOT FOUND
            - detail: Error message indicating the missing post.
    """
    post = find_post(id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Item with id: {id} not found',
        )
    return {'post_detail': f'here is your post {post}'}


@app.post('/posts', status_code=status.HTTP_201_CREATED)
async def create_post(post: Post):
    """
    Create a new post.

    Accepts a post payload, assigns a random ID, appends it to the `my_post` list,
    and returns the created post data.

    Args:
        post (Post): A Pydantic model instance containing the post details.

    Returns:
        dict: A dictionary containing the newly created post data.
            Example:
                {
                    "data": {
                        "id": 123456,
                        "title": "New Post",
                        "content": "This is a new post."
                    }
                }
    """
    post_dict = post.model_dump()
    post_dict['id'] = randrange(0, 10000000)
    my_post.append(post_dict)
    return {'data': post_dict}


@app.delete('/posts/{id}')
async def delete_post(id: int):
    """
    Delete a specific post by its ID.

    Searches for a post with the given ID. If found, deletes it from the `my_post` list.
    If not found, raises a 404 HTTP exception.

    Args:
        id (int): The unique identifier of the post to delete.

    Returns:
        dict: A confirmation message indicating successful deletion.
            Example:
                {
                    "message": "Post with id 1 has been deleted successfully.",
                    "deleted_post": {
                        "id": 1,
                        "title": "First Post",
                        "content": "Content of the first post."
                    }
                }

    Raises:
        HTTPException: If no post with the specified ID is found.
            - status_code: 404 NOT FOUND
            - detail: Error message indicating the missing post.
    """
    index = find_post_index(id)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post with id {id} not found.',
        )
    deleted_post = my_post.pop(index)
    return {
        'message': f'Post with id {id} has been deleted successfully.',
        'deleted_post': deleted_post,
    }


@app.put('/posts/{id}')
async def update_post(id: int, updated_post: Post):
    """
    Update an existing post by its ID.

    Searches for a post with the given ID. If found, updates its details with the provided data.
    If not found, raises a 404 HTTP exception.

    Args:
        id (int): The unique identifier of the post to update.
        updated_post (Post): A Pydantic model instance containing the updated post details.

    Returns:
        dict: A confirmation message along with the updated post data.
            Example:
                {
                    "message": "Post with id 1 has been updated successfully.",
                    "updated_post": {
                        "id": 1,
                        "title": "Updated First Post",
                        "content": "Updated content of the first post.",
                        "publish": True,
                        "rating": 4
                    }
                }

    Raises:
        HTTPException: If no post with the specified ID is found.
            - status_code: 404 NOT FOUND
            - detail: Error message indicating the missing post.
    """
    index = find_post_index(id)
    if index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'Post with id {id} not found.',
        )
    # Update the post details
    updated_post_dict = updated_post.model_dump()
    updated_post_dict['id'] = id  # Ensure the ID remains unchanged
    my_post[index].update(updated_post_dict)
    return {
        'message': f'Post with id {id} has been updated successfully.',
        'updated_post': my_post[index],
    }
