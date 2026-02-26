<h1>SPARCS Auth Service</h1>
<p>A serverless REST API implemented with Clean Architecture and Domain Driven Design</p>

## Architecture

This project follows the [clean architecture style](http://blog.thedigitalcatonline.com/blog/2016/11/14/clean-architectures-in-python-a-step-by-step-example/) and structured the codebase accordingly.

![cleanArchitecture image](https://cdn-images-1.medium.com/max/1600/1*B7LkQDyDqLN3rRSrNYkETA.jpeg)

_Image credit to [Thang Chung under MIT terms](https://github.com/thangchung/blog-core)_

## Folder Structure

This service separates concerns to keep core business logic independent of external frameworks. 

* **`aws/`**: AWS-specific configurations (e.g., Cognito settings).
* **`constants/`**: Application-wide static values and common constants.
* **`controller/`**: Manages incoming requests (API routers like `auth_router.py`) and routes them to the appropriate usecases.
* **`model/`**: Contains the core business objects, data entities, and schemas.
* **`repository/`**: Handles data access and interacts directly with the database or external APIs.
* **`resources/`**: Infrastructure and configuration assets (e.g., `api.yml`, `cognito.yml`).
* **`scripts/`**: Utility scripts for local setup.
* **`usecase/`**: Contains the core business logic and application rules.
* **`utils/`**: Reusable helper functions and generic logic.

## AWS SSO Authentication

[cite_start]This service utilizes **AWS SSO** for authentication. 

**To authenticate:**
1. [cite_start]Ensure your DevContainer is running (your host `.aws/` directory is automatically mounted)[cite: 14].
2. Open the terminal inside VS Code and run:
   ```bash
   aws sso login
   ```
3. Follow the prompt to open your browser and authorize your session. Once approved, your terminal will be authenticated and ready to interact with AWS resources.

## Commands & Scripts

Here are the standard commands for local development and deployment. [cite_start]Ensure you are running these inside the DevContainer environment[cite: 6, 7].

### Run Local Server
```bash
uvicorn main:app --reload --log-level debug --env-file .env
```
[cite_start]*When/Why:* Run this to start the FastAPI development server locally to test your endpoints[cite: 24].

### Deploy to AWS Lambda
If the Serverless framework is not yet installed in the container, install it and its plugins first:
```bash
npm install -g serverless
npm install
```
Then, deploy the service:
```bash
serverless deploy --stage 'dev' --aws-profile 'default'
```
[cite_start]*When/Why:* Run this to deploy the Serverless configuration and Lambda functions to AWS[cite: 24].

### Resources
- [https://fastapi.tiangolo.com/](https://fastapi.tiangolo.com/)
- [https://www.serverless.com/framework/docs](https://www.serverless.com/framework/docs)
- [https://react.dev/reference/react](https://react.dev/reference/react)
- [https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)