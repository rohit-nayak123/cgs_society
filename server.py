from fastapi import FastAPI
import os
from appwrite.client import Client
from dotenv import load_dotenv
from appwrite.services.tables_db import TablesDB
from uuid import uuid4
from pydantic import BaseModel
from contextlib import asynccontextmanager
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from gmailFile import cron_jobs
from google import genai
from google.genai import types
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request
import base64
import json

# ----------------------------------------------------------------------------
load_dotenv()

database_client = Client()
database_client.set_endpoint(os.environ.get("APPWRITE_ENDPOINT"))
database_client.set_project(os.environ.get("APPWRITE_PROJECT_ID"))
database_client.set_key(os.environ.get("APPWRITE_API_KEY"))

database_id: str = os.environ.get("DATABASE_ID", "")
table_id: str = os.environ.get("TABLE_ID", "")
google_api_key: str = os.environ.get("GEMINI_API_KEY", "")

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

# # ----------------------------------------------------------------------------


def generate(prompt: str, image_base64: str) -> str:
    gemini_client = genai.Client(
        api_key=google_api_key
    )

    header, encoded = image_base64.split(",", 1)

    mime_type = (
        header
        .split(";")[0]
        .replace("data:", "")
    )

    image_bytes = base64.b64decode(encoded)

    response = gemini_client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=[
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(
                        text=prompt
                    ),
                    types.Part.from_bytes(
                        data=image_bytes,
                        mime_type=mime_type,
                    ),
                ],
            )
        ],
        config=types.GenerateContentConfig(
            thinking_config=types.ThinkingConfig(
                thinking_budget=0
            )
        ),
    )

    return response.text or ""

# ------------------------------------------------------------------------------------


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
tables_db = TablesDB(database_client)


class classTime(BaseModel):
    location: str
    email: str
    Stime: int | float
    duration: int | float
    Day: str
    subject: str


def extractTimetable():
    return 1


@app.get("/")
def home():
    return "hello world"


@app.post("/timetable")
async def add_timetable_entry(req: Request):
    prompt = """Read this image of a timetable properly and give me a list with object as its items. The structure of each object is:{"location": str,"email": str,"Stime": int,"Day": str,"subject": str,"duration": int}Example:[{"location": "NR112","email": email,"Stime": 8,"Day": "Mon","subject": "MA11003","duration": 2},{...},{...}] NOTE:1. Leave the email field exactly as "email". 2. Stime is the starting time and must be an integer only. Do not include AM, PM, minutes, or formats like 8:00. 3. duration must be an integer only. Do not include text such as "2 hours" or "55 minutes". Use only values like 1, 2, 3, etc. 4. The starting time should be converted to 12-hour format and stored as an integer. 5. Most important: return ONLY the JSON array and nothing else no explanations, no extra text before or after the markdown."""

    data = await req.json()
    email = data.get("email")

    result = generate(
        prompt=prompt,
        image_base64=data["image"]
    )

    parsed_result: list = json.loads(result)
    # print(result)
    # print(type(parsed_result))

    # return {
    #     "success": True,
    #     "result": result
    # }
# '''
    try:
        for item in parsed_result:
            tables_db.create_row(
                database_id=database_id,
                table_id=table_id,
                row_id=str(uuid4()),
                data={
                    "location": item["location"],
                    "email": email,
                    "Stime": item["Stime"],
                    "Day": str(item["Day"])[0:3],
                    "subject": item["subject"],
                    "duration": item["duration"]
                },
            )

        return {"successful": True}

    except Exception as e:
        print(e)
        return {"successful": False, "error": str(e)}
# '''
