# Here’s how you can get all three services up and running using Docker Compose:

## 1. Prerequisites

- Make sure you have Docker and Docker Compose installed on your machine.

- Create a .env file in the same directory as the docker-compose.yml

- Make sure you have Postman installed on your machine

## 2. Inspect your .env file

- If you are running the microservice outside Docker, make sure to set your DATABASE_HOST as localhost

### IMPORTANT!

- For test purposes I will post the .env in this README file
- Create the .env file in the root of your cloned project with this content:

```
DATABASE_USER=postgres
DATABASE_PASSWORD=postgres
DATABASE_NAME=practical_test
DATABASE_HOST=localhost
DATABASE_PORT=5432
SCHEDULER_SECONDS_INTERVAL=60
SLACK_WEBHOOK_URL=http://localhost:8001
SLA_CONFIG_PATH=sla_config.yaml
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