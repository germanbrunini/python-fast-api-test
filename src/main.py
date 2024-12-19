from fastapi import FastAPI, Response, HTTPException, status, Depends, Request
from random import randrange
from typing import Annotated, List, Optional, Dict, Any, AsyncGenerator
import psycopg
from psycopg.rows import dict_row  # Import the row factory for dictionaries
from psycopg_pool import AsyncConnectionPool
from pydantic import BaseModel, ValidationError, field_validator
import time
import asyncio
import logging
from contextlib import asynccontextmanager

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

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# --------- Configuration ---------
HOST = 'localhost'
PT = '5433'
DBN = 'postgres'
USER = 'postgres'
PASS = 'germanpostgres1'
# Define your connection parameters
DB_DSN = f'host={HOST} port={PT} dbname={DBN} user={USER} password={PASS}'


# --------- Pydantic Models ---------
class Post(BaseModel):
    id: int
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
    published: bool = True


# Response model for /posts endpoint
class PostsResponse(BaseModel):
    data: List[Post]


class PostUpdate(BaseModel):
    title: str
    content: str
    published: bool = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.

    This function runs before the application starts serving requests
    and after it shuts down. It:
    - Initializes an asynchronous database connection pool.
    - Tests the database connection.
    - Yields control to the application so it can serve requests.
    - Closes the database connection pool when the application shuts down.

    If any error occurs during pool creation or the test query, it will
    raise a RuntimeError, preventing the app from starting in an
    inconsistent state.
    """
    try:
        # Create the async connection pool as a context manager.
        # Using `async with` ensures that the pool is properly opened
        # before the app starts and closed after it shuts down.
        async with AsyncConnectionPool(
            conninfo=DB_DSN, min_size=1, max_size=5, kwargs={'row_factory': dict_row}
        ) as pool:
            # Attach the pool to the app's state so it can be accessed
            # by your endpoints via dependencies.
            app.state.pool = pool

            # Test the connection at startup to ensure the DB is reachable.
            try:
                async with pool.connection() as conn:
                    async with conn.cursor() as cur:
                        await cur.execute('SELECT 1;')
                        result = await cur.fetchone()
                        if result is None:
                            # If no result returned, something is off.
                            raise RuntimeError('Test query did not return a result.')
            except psycopg.OperationalError as op_err:
                # Handle typical database connection issues
                logger.error(
                    'Database operational error occurred during startup: %s', op_err
                )
                raise RuntimeError(
                    'Failed to connect to the database at startup.'
                ) from op_err
            except Exception as e:
                # Catch-all for unexpected exceptions
                logger.exception(
                    'Unexpected error during database initialization: %s', e
                )
                raise RuntimeError(
                    'Unexpected error during database initialization.'
                ) from e

            # Yield control back to FastAPI's event loop. The application
            # will start serving requests after this point.
            yield

        # When the application is shutting down, exiting this block
        # will automatically close the pool due to `async with`.
        # No explicit return statement is needed because `yield`
        # handles the control flow for an async context manager.
    except Exception as e:
        # If we get here, it means we couldn't even enter the context.
        logger.exception('Critical error during app startup: %s', e)
        raise RuntimeError('Critical error during startup. Cannot proceed.') from e


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
    lifespan=lifespan,
)


async def get_db_connection(
    request: Request,
) -> AsyncGenerator[psycopg.AsyncConnection[Any], None]:
    # Ensure the `pool` attribute exists on `app.state`
    if not hasattr(request.app.state, 'pool'):
        raise RuntimeError('Database pool not initialized.')

    async with request.app.state.pool.connection() as conn:
        yield conn


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


def find_post(id: int) -> Optional[Dict[str, Any]]:
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


@app.get('/posts', response_model=List[Post])
async def get_posts(conn: psycopg.AsyncConnection = Depends(get_db_connection)):  # noqa: B008
    """
    Retrieve all posts from the database.

    This endpoint queries the `public.posts` table and returns a list
    of posts sorted in ascending order by their ID. Each returned post
    includes the following fields:
    - id (int): The unique identifier of the post.
    - title (str): The title of the post.
    - content (str): The full content/body of the post.
    - published (bool): A flag indicating whether the post is published or not.

    Returns:
        List[Post]: A list of post objects representing the posts retrieved
                    from the database.

    Raises:
        HTTPException (503): If the database operation fails due to
                             operational errors (e.g. connection issues).
        HTTPException (500): For any unexpected errors occurring during
                             the query execution or data processing.
    """
    try:
        async with conn.cursor() as cur:
            await cur.execute(
                'SELECT id, title, content, published FROM public.posts ORDER BY id ASC;'
            )
            rows = await cur.fetchall()

            # Convert dictionary rows into Pydantic Post models
            posts = [Post(**row) for row in rows]
            return posts

    except psycopg.OperationalError as oe:
        # Handle common database operational issues (e.g., connectivity issues)
        logger.error(f'Database operational error occurred while fetching posts: {oe}')
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Database is temporarily unavailable. Please try again later.',
        ) from oe

    except Exception as e:
        # Catch-all for any other unexpected errors
        logger.exception(f'Unexpected error occurred while fetching posts: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error occurred. Please contact support if the issue persists.',
        ) from e


@app.get('/posts/latest', response_model=Post)
async def get_latest_post(conn: psycopg.AsyncConnection = Depends(get_db_connection)):  # noqa: B008
    """
    Retrieve the latest post from the database.

    This endpoint queries the database to find the most recently added post (by ID)
    and returns it as a structured `Post` object.

    Returns:
        Post: A Pydantic model representing the latest post.

    Raises:
        HTTPException(404): If no posts are found in the database.
        HTTPException(503): If there's a database operation issue (e.g., connectivity).
        HTTPException(500): If an unexpected error occurs.
    """
    try:
        async with conn.cursor() as cur:
            # Query the database for the latest post by ordering desc and limiting to 1
            await cur.execute(
                'SELECT id, title, content, published FROM public.posts ORDER BY id DESC LIMIT 1;'
            )
            row = await cur.fetchone()

            # If no posts are found, return a 404 error.
            if row is None:
                logger.info('No posts found when retrieving the latest post.')
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail='No posts found in the database.',
                )

            # Convert the dictionary row into a Post model
            latest_post = Post(**row)
            return latest_post

    except psycopg.OperationalError as oe:
        # Operational errors often indicate connection issues or transient DB problems.
        logger.error(
            'Database operational error occurred while fetching the latest post: %s', oe
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Database is temporarily unavailable. Please try again later.',
        ) from oe

    except Exception as e:
        # Catch-all for unexpected exceptions.
        logger.exception(
            'Unexpected error occurred while fetching the latest post: %s', e
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error occurred. Please contact support if the issue persists.',
        ) from e


@app.get('/posts/{id}', response_model=Post)
async def get_post_by_id(
    id: int, conn: Annotated[psycopg.AsyncConnection, Depends(get_db_connection)]
):
    """
    Retrieve a specific post by its ID from the database.

    This endpoint queries the `public.posts` table for a post matching the given ID.
    If found, it returns the post as a `Post` model. If no post is found, a 404 error
    is raised.

    Args:
        id (int): The unique identifier of the post to retrieve.
        conn (psycopg.AsyncConnection): A database connection provided via dependency injection.

    Returns:
        Post: A Pydantic model representing the requested post.

    Raises:
        HTTPException(404): If no post with the specified ID is found.
        HTTPException(503): If there's a database operation issue (e.g., connectivity problems).
        HTTPException(500): If an unexpected error occurs during processing.
    """
    try:
        async with conn.cursor() as cur:
            # Execute query to find the post by ID
            await cur.execute(
                'SELECT id, title, content, published FROM public.posts WHERE id = %s;',
                (id,),
            )
            row = await cur.fetchone()

            # If no post found, return 404
            if not row:
                logger.info('Post with id %d not found.', id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Post with id {id} not found.',
                )

            # Convert the retrieved row (dict) into a Post model
            try:
                post = Post(**row)
            except ValidationError as ve:
                logger.error('Data validation error: %s', ve)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail='Data validation failed for the retrieved post.',
                ) from ve
            return post

    except HTTPException as he:
        # If it's an HTTPException, just re-raise it. FastAPI will handle it.
        raise he

    except psycopg.OperationalError as oe:
        # Handle issues like lost connections or transient DB errors
        logger.error(
            'Database operational error while fetching post with id %d: %s', id, oe
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Database is temporarily unavailable. Please try again later.',
        ) from oe

    except Exception as e:
        # Catch-all for any unexpected errors
        logger.exception(
            'Unexpected error occurred while fetching post with id %d: %s', id, e
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error occurred. Please contact support if the issue persists.',
        ) from e


@app.post('/posts', status_code=status.HTTP_201_CREATED, response_model=Post)
async def create_post(
    post_data: PostCreate,
    conn: Annotated[psycopg.AsyncConnection, Depends(get_db_connection)],
):
    """
    Create a new post in the database.

    Inserts a new post record into the `public.posts` table using the data
    provided by the client. Upon successful insertion, the endpoint returns
    the newly created post with a `201 Created` status code.

    Args:
        post_data (PostCreate): A Pydantic model instance containing the
            following fields:
            - title (str): The title of the post.
            - content (str): The body/content of the post.
            - published (bool): Indicates whether the post is published or not.
        conn (psycopg.AsyncConnection): An asynchronous database connection
            provided by the application's connection pool.

    Returns:
        Post: The newly created post, including its `id`, `title`, `content`,
        and `published` status.

    Raises:
        HTTPException(503): If the database is temporarily unavailable.
        HTTPException(500): If an unexpected error occurs during insertion.

    Example (Testing with Postman):
        1. Launch Postman.
        2. Set the request method to POST.
        3. Enter the endpoint URL: http://127.0.0.1:8000/posts/
        4. Go to the "Body" tab and select "raw" and "JSON".
        5. In the request body, provide valid JSON data. For example:
           {
               "title": "My Awesome Post",
               "content": "This is the content of my awesome post.",
               "published": true
           }
        6. Click "Send".
        7. If successful, you will receive a `201 Created` response and a JSON
           object representing the newly created post. For example:
           {
               "id": 42,
               "title": "My Awesome Post",
               "content": "This is the content of my awesome post.",
               "published": true
           }
    """
    try:
        async with conn.cursor() as cur:
            # Insert the new post into the database and return its full data.
            # Using RETURNING clause to get the newly created post's columns.
            await cur.execute(
                """
                INSERT INTO public.posts (title, content, published)
                VALUES (%s, %s, %s)
                RETURNING id, title, content, published;
                """,
                (post_data.title, post_data.content, post_data.published),
            )
            new_post_row = await cur.fetchone()

            # If for some reason no row is returned (highly unlikely), raise an error.
            if not new_post_row:
                logger.error('No data returned after inserting a new post.')
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail='Failed to retrieve newly created post.',
                )
            # Commit the transaction so that the insertion is persisted
            await conn.commit()
            # Convert the returned dictionary row into a Post model.
            new_post = Post(**new_post_row)
            return new_post

    except psycopg.OperationalError as oe:
        # Handle common database operational issues, like connection interruptions.
        logger.error(
            'Database operational error occurred while creating a post: %s', oe
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Database is temporarily unavailable. Please try again later.',
        ) from oe

    except Exception as e:
        # Catch-all for unexpected exceptions.
        logger.exception('Unexpected error occurred while creating a post: %s', e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error occurred. Please contact support if the issue persists.',
        ) from e


@app.delete('/posts/{id}', status_code=status.HTTP_200_OK)
async def delete_post(
    id: int, conn: Annotated[psycopg.AsyncConnection, Depends(get_db_connection)]
):
    """
    Delete a specific post by its ID from the database.

    This endpoint removes a post from the `public.posts` table if it exists.
    If the specified post is not found, it returns a `404 Not Found` error.

    Args:
        id (int): The unique identifier of the post to delete.
        conn (psycopg.AsyncConnection): A database connection obtained from the connection pool.

    Returns:
        dict: A dictionary containing a confirmation message and details of the deleted post.
        Example:
            {
                "message": "Post with id 1 has been deleted successfully.",
                "deleted_post": {
                    "id": 1,
                    "title": "First Post",
                    "content": "Content of the first post.",
                    "published": true
                }
            }

    Raises:
        HTTPException(404): If no post with the specified ID is found.
        HTTPException(503): If the database is temporarily unavailable.
        HTTPException(500): If an unexpected error occurs during deletion.

    Example (Testing with Postman):
        1. Launch Postman.
        2. Set the request method to DELETE.
        3. Enter the endpoint URL: http://localhost:8000/posts/1
        4. Click "Send".
        5. If successful, you will receive a `200 OK` response and a JSON object confirming deletion.
           If the post doesn't exist, you'll get a `404 Not Found` response.
    """
    try:
        async with conn.cursor() as cur:
            # Attempt to delete the post and return its data
            # Using the RETURNING clause to retrieve the deleted post
            await cur.execute(
                """
                DELETE FROM public.posts
                WHERE id = %s
                RETURNING id, title, content, published;
                """,
                (id,),
            )
            deleted_post_row = await cur.fetchone()

            # If no row returned, the post doesn't exist
            if not deleted_post_row:
                logger.info('No post found with id %d. Cannot delete.', id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Post with id {id} not found.',
                )

        # Commit the transaction to finalize the deletion
        await conn.commit()

        return {
            'message': f'Post with id {id} has been deleted successfully.',
            'deleted_post': deleted_post_row,
        }

    except psycopg.OperationalError as oe:
        logger.error(
            'Database operational error occurred while deleting post %d: %s', id, oe
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Database is temporarily unavailable. Please try again later.',
        ) from oe

    except Exception as e:
        logger.exception('Unexpected error occurred while deleting post %d: %s', id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error occurred. Please contact support if the issue persists.',
        ) from e


@app.put('/posts/{id}', response_model=Post)
async def update_post(
    id: int,
    updated_post: PostUpdate,
    conn: Annotated[psycopg.AsyncConnection, Depends(get_db_connection)],
):
    """
    Update an existing post by its ID in the database.

    This endpoint attempts to update the post matching the given `id` with the data
    provided in `updated_post`. If no post is found, it returns a 404 error.

    Args:
        id (int): The unique identifier of the post to update.
        updated_post (PostUpdate): A Pydantic model instance containing the updated
                                   post details (title, content, published).
        conn (psycopg.AsyncConnection): A database connection obtained from the connection pool.

    Returns:
        Post: The updated post, now reflecting the provided changes.

    Raises:
        HTTPException(404): If no post with the specified ID is found.
        HTTPException(503): If the database is temporarily unavailable.
        HTTPException(500): If an unexpected error occurs during the update.

    Example (Testing with Postman):
        1. Launch Postman.
        2. Set the request method to PUT.
        3. Enter the endpoint URL: http://localhost:8000/posts/1
        4. Go to the "Body" tab, select "raw" and "JSON".
        5. Provide a valid JSON body, for example:
           {
               "title": "Updated Title",
               "content": "Updated content of the post.",
               "published": true
           }
        6. Click "Send".
        7. If successful, you will receive a `200 OK` response and a JSON
           object representing the updated post.
    """
    try:
        async with conn.cursor() as cur:
            # Update the post and return the updated fields
            await cur.execute(
                """
                UPDATE public.posts
                SET title = %s, content = %s, published = %s
                WHERE id = %s
                RETURNING id, title, content, published;
                """,
                (updated_post.title, updated_post.content, updated_post.published, id),
            )
            updated_row = await cur.fetchone()

            # If no row returned, the post doesn't exist
            if not updated_row:
                logger.info('No post found with id %d for update.', id)
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f'Post with id {id} not found.',
                )

        # Commit the transaction to persist changes
        await conn.commit()

        return Post(**updated_row)

    except psycopg.OperationalError as oe:
        logger.error(
            'Database operational error occurred while updating post %d: %s', id, oe
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail='Database is temporarily unavailable. Please try again later.',
        ) from oe

    except Exception as e:
        logger.exception('Unexpected error occurred while updating post %d: %s', id, e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail='An unexpected error occurred. Please contact support if the issue persists.',
        ) from e
