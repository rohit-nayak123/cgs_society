from fastapi import FastAPI
import os
from appwrite.client import Client
from dotenv import load_dotenv
from appwrite.services.tables_db import TablesDB
from appwrite.models import Row
from uuid import uuid4
from pydantic import BaseModel
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from gmailFile import cron_jobs
# ----------------------------------------------------------------------------
load_dotenv()

client = Client()
client.set_endpoint(os.environ.get("APPWRITE_ENDPOINT"))
client.set_project(os.environ.get("APPWRITE_PROJECT_ID"))
client.set_key(os.environ.get("APPWRITE_API_KEY"))

database_id: str = os.environ.get("DATABASE_ID", "")
table_id: str = os.environ.get("TABLE_ID", "")

# ----------------------------------------------------------------------------

scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")


@asynccontextmanager
async def lifespan(app: FastAPI):

    cron_jobs(scheduler)

    scheduler.start()
    print("Scheduler started!")

    yield

    scheduler.shutdown()
    print("Scheduler shut down!")

# ------------------------------------------------------------------------------------

app = FastAPI(lifespan=lifespan)
tables_db = TablesDB(client)


class classTime(BaseModel):
    location: str
    email: str
    Stime: int | float
    duration: int | float
    Day: str
    subject: str


@app.get("/")
def home():
    return "hello world"


@app.post("/timetable")
def add_timetable_entry(req: list[classTime]):
    try:
        for item in req:
            tables_db.create_row(
                database_id=database_id,
                table_id=table_id,
                row_id=str(uuid4()),
                data={
                    "location": item.location,
                    "email": item.email,
                    "Stime": item.Stime,
                    "Day": item.Day,
                    "subject": item.subject,
                    "duration": item.duration,
                },
            )

        return {"successful": True}

    except Exception as e:
        print(e)
        return {"successful": False, "error": str(e)}
