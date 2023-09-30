import os

import lambdawarmer
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from mangum import Mangum

from controller.auth_controller import api_controller

STAGE = os.environ.get('STAGE')
root_path = '/' if not STAGE else f'/{STAGE}'

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
            <title>Welcome to my Demo</title>
        </head>
        <body>
            <h1>Welcome to my Demo</h1>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


api_controller(app)
mangum_handler = Mangum(app, lifespan='off')


@lambdawarmer.warmer
def handler(event, context):
    return mangum_handler(event, context)
