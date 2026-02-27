<h1>SPARCS Auth Service</h1>
<p>A serverless REST API implementing Clean Architecture and Domain-Driven Design principles</p>

## Architecture

This project follows the [clean architecture style](http://blog.thedigitalcatonline.com/blog/2016/11/14/clean-architectures-in-python-a-step-by-step-example/) and structures the codebase accordingly.

![cleanArchitecture image](https://cdn-images-1.medium.com/max/1600/1*B7LkQDyDqLN3rRSrNYkETA.jpeg)

_Image credit to [Thang Chung under MIT terms](https://github.com/thangchung/blog-core)_

## Setting Up Dev Containers

This project uses **VS Code Dev Containers** to provide a consistent environment.

---

1. First, Install Docker Desktop: [Docker Windows Install Guide](https://docs.docker.com/desktop/setup/install/windows-install/)  
2. Start Docker Desktop and wait for **“Docker Desktop is running”**  
3. Open the project in VS Code → it connects automatically  
4. Wait for a prompt to Rebuild/Start the Dev Container, else:  
5. Start/Rebuild Dev Container by doing `Ctrl + Shift + P` and press `Dev Containers: Rebuild Container` 
6. To verify, the terminal inside the Dev Container should look similar to this: `root ➜ /workspaces/TechTix (main) $`
7. Then, install dependencies and run localhost using 
```
npm run install && npm run dev
```

## Folder Structure

This service separates concerns to maintain core business logic independence from external frameworks. 

* **`aws/`**: AWS-specific configurations (e.g., Cognito settings).
* **`constants/`**: Application-wide static values and common constants.
* **`controller/`**: Manages incoming HTTP requests (API routers like `auth_router.py`) and routes them to appropriate use cases.
* **`model/`**: Contains core business objects, data entities, and schemas.
* **`repository/`**: Handles data access and interacts directly with databases or external APIs.
* **`resources/`**: Infrastructure and configuration assets (e.g., `api.yml`, `cognito.yml`).
* **`scripts/`**: Utility scripts for local setup and configuration.
* **`usecase/`**: Implements core business logic and application rules.
* **`utils/`**: Reusable helper functions and generic utilities.

## Best Practices

### Naming Conventions

Follow these naming standards to maintain consistency across the codebase:

* **Classes**: Use PascalCase for all class names
  - Models: `Admin`, `Entities`, `AdminIn` (Input models)
  - Use Cases: `AuthUsecase`, `AdminUseCase`, `EmailUsecase`
  - Repositories: `AdminsRepository`, `RepositoryUtils`
  - Routers: `auth_router`, `admin_auth_router`

* **Files**: Use snake_case for all file names
  - `auth_usecase.py`, `admin_repository.py`, `common_constants.py`

* **Variables & Functions**: Use snake_case
  - `sign_up_details`, `user_pool_id`, `store_admin()`

* **Database Attributes**: Use camelCase for PynamoDB attributes
  - `hashKey`, `rangeKey`, `latestVersion`, `entryStatus`, `firstName`, `lastName`

* **Constants**: Use UPPER_SNAKE_CASE
  - `USER_POOL_ID`, `REGION`, `STAGE`

### Clean Architecture Dependency Rules

The architecture enforces strict dependency flow to maintain separation of concerns:

1. **Dependency Direction**: Dependencies must point inward (from outer to inner layers)
   - `controller` → `usecase` → `repository` → `model`
   - Inner layers (model, usecase) should never depend on outer layers (controller, repository)

2. **Layer Independence**:
   - **Model Layer**: Contains no external dependencies—only pure business entities and schemas
   - **Use Case Layer**: Depends only on models; business logic remains framework-agnostic
   - **Repository Layer**: Implements data access; depends on models but not on use cases
   - **Controller Layer**: Depends on use cases and models; handles HTTP-specific concerns

3. **Interface Segregation**:
   - Use cases interact with repositories through well-defined interfaces
   - Controllers receive data via Pydantic models and pass them to use cases
   - Use cases return domain objects, not framework-specific responses

### Layer Responsibilities

Each layer has distinct responsibilities to maintain clean separation:

#### **Controller Layer** (`controller/`)
- Handle HTTP requests and responses
- Validate request format and route to appropriate use cases
- Transform HTTP-specific data to domain models
- Define API endpoints and their documentation
- **Must not contain business logic**

#### **Use Case Layer** (`usecase/`)
- Implement core business logic and application rules
- Orchestrate data flow between controllers and repositories
- Coordinate multiple repository operations when needed
- Handle business validations and exceptions
- Remain framework-agnostic (no FastAPI/AWS dependencies in business logic)

#### **Repository Layer** (`repository/`)
- Manage data persistence and retrieval
- Interact with databases (DynamoDB via PynamoDB)
- Translate between domain models and database schemas
- Handle database-specific error handling
- Implement data access patterns

#### **Model Layer** (`model/`)
- Define business entities and data structures
- Specify validation rules using Pydantic
- Define database models using PynamoDB
- Contain no business logic—only data definitions
- Serve as contracts between layers

## AWS SSO Authentication

This service utilizes **AWS SSO** for authentication. 

**To authenticate:**
1. Ensure your DevContainer is running (your host `.aws/` directory is automatically mounted).
2. Open the terminal inside VS Code and run:
   ```bash
   aws sso login
   ```
3. Follow the prompt to open your browser and authorize your session. Once approved, your terminal will be authenticated and ready to interact with AWS resources.

## Commands & Scripts

Standard commands for local development and deployment. Ensure you run these inside the DevContainer environment.

### Run Local Server
```bash
uvicorn main:app --reload --log-level debug --env-file .env
```
**When/Why:** Run this command to start the FastAPI development server locally for testing your endpoints.

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
**When/Why:** Run this command to deploy the Serverless configuration and Lambda functions to AWS.

## Resources
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Serverless Framework Documentation](https://www.serverless.com/framework/docs)
- [Clean Architecture by Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Clean Architectures in Python](http://blog.thedigitalcatonline.com/blog/2016/11/14/clean-architectures-in-python-a-step-by-step-example/)