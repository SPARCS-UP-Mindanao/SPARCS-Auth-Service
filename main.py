import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from mangum import Mangum
from lambda_decorators import cors_headers

from controller.auth_controller import api_controller

STAGE = os.environ.get('STAGE')
root_path = f'/{STAGE}' if STAGE else '/'

app = FastAPI(
    root_path=root_path,
    title="SPARCS Auth Service",
    contact={
        "name": "Society of Programmers and Refined Computer Scientists",
        "email": "contact@sparcsup.com",
    },
)


@app.get("/", include_in_schema=False)
def welcome():
    html_content = """
    <html>
        <head>
            <title>Welcome to the SPARCS Auth API</title>
        </head>
        <body>
            <h1>Welcome to the Auth API</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


api_controller(app)
mangum_handler = Mangum(app, lifespan='off')

@cors_headers
def handler(event, context):
    return mangum_handler(event, context)
