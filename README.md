# Here’s how you can get all three services up and running using Docker Compose:

## 1. Prerequisites

- Make sure you have Docker and Docker Compose installed on your machine.

- Create a .env file in the same directory as the docker-compose.yml

## 2. Inspect your .env file

This is what the .env file should look like (e.g. .env.local). 
- If you are running the microservice outside Docker, make sure to set your DATABASE_HOST as localhost

```
DATABASE_USER=
DATABASE_PASSWORD=
DATABASE_NAME=
DATABASE_HOST=
DATABASE_PORT=
SCHEDULER_SECONDS_INTERVAL=
SLACK_WEBHOOK_URL=
SLA_CONFIG_PATH=
```

Docker Compose will substitute these into any ${...} entries in your compose file

## 3. Bring the services up

Before proceeding, I need to explain a few things first

- There is a script that creates the database located in app/db/create_db.py.
- This script is already being called when we execute the docker compose, but make sure you have everything running before testing the application.

```bash
$ docker compose up --build -d
```

### OPTIONAL 
- If you want to simulate a client connected to the websocket, you can execute the code in client.py with the command python client.py, after downloading the required dependencies.

You should see 3 services running:
1. postgres-service
2. mock-api
3. fastapi_app

## 4. Testing the application

Now that you have the application already setup on your computer, you can import the collection located in:

```
collection.postman_collection.json
```

There you can make requests to test all endpoints.

### OPTIONAL

There is a commented endpoint in the file app/controllers/ticket_controller.py that I used during development to test more easily the escalation_workflow, so feel free to uncomment and test it by yourself.