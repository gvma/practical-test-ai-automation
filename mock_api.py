from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/slack/mock")
async def send_message(request: Request):
    body = await request.body()
    return {"raw_body": body.decode("utf-8")}