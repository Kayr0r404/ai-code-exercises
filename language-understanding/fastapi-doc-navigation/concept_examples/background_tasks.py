"""Background tasks — based on FastAPI docs on Background Tasks."""

from fastapi import FastAPI, BackgroundTasks

app = FastAPI()


def send_welcome_email(user_email: str):
    print(f"Sending welcome email to {user_email}...")
    with open("email_log.txt", "a") as f:
        f.write(f"Welcome email sent to {user_email}\n")


@app.post("/register/")
async def register_user(email: str, background_tasks: BackgroundTasks):
    background_tasks.add_task(send_welcome_email, email)
    return {"message": "Registered. Welcome email will be sent shortly."}


# Background task from a dependency
def log_request(path: str):
    with open("request_log.txt", "a") as f:
        f.write(f"Request to {path}\n")


async def logging_dependency(background_tasks: BackgroundTasks, path: str):
    background_tasks.add_task(log_request, path)
    return path


@app.get("/tracked/")
async def tracked_endpoint(path: str = Depends(logging_dependency)):
    return {"path": path}
