import os
from appwrite.client import Client
from dotenv import load_dotenv
from appwrite.services.tables_db import TablesDB
from appwrite.models import RowList
from appwrite.query import Query
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import smtplib
from email.message import EmailMessage
from datetime import datetime
import zoneinfo

load_dotenv()

client = Client()
client.set_endpoint(os.environ.get("APPWRITE_ENDPOINT"))
client.set_project(os.environ.get("APPWRITE_PROJECT_ID"))
client.set_key(os.environ.get("APPWRITE_API_KEY"))

database_id: str = os.environ.get("DATABASE_ID", "")
table_id: str = os.environ.get("TABLE_ID", "")
mail_id: str = os.environ.get("MAIL", "")
mail_password: str = os.environ.get("MAIL_PASSWORD", "")

tables_db = TablesDB(client)

def loadRow(day, time):
    result: RowList = tables_db.list_rows(
        database_id=database_id,
        table_id=table_id,
        queries=[
            Query.equal("Day", day),
            Query.equal("Stime", time)
        ]

    )
    return result.model_dump()

def sendMail():

    timezone = zoneinfo.ZoneInfo("Asia/Kolkata")
    present_time = datetime.now(timezone)
    day = present_time.strftime("%A")
    day = day[0:3]
    hour = int(present_time.strftime("%I"))
    am_pm = present_time.strftime("%p")

    data = loadRow(day, hour)
    # data = loadRow("Fri", 9)
    rows = data["rows"]
    # print(rows)
    # for i in rows:
    #     print(i)
    # '''
    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            for i in rows:
                email = i["data"]["email"]
                location = i["data"]["location"]
                duration = i["data"]["duration"]
                subject = "" + i["data"]["subject"]
                stime = i["data"]["Stime"]
                msg = EmailMessage()
                msg['From'] = mail_id
                msg['To'] = email
                msg['Subject'] = "Your have a class"
                msg.set_content("Hello,\n\nYou have class of " + str(subject) + " at class room " +
                                str(location) + " for " + str(duration) + " hours at " + str(stime) + " " + str(am_pm) + " O' clock")
                smtp.login(mail_id, mail_password)
                smtp.send_message(msg)
            print("Email sent successfully!")

    except Exception as e:
        print(f"Failed to send email. Error: {e}")

# '''

# sendMail()

# '''

def cron_jobs(scheduler: AsyncIOScheduler):
    """
    Runs at 45 minutes past the hour, from 07:45 to 16:45 from Mon to Fri
    """

    scheduler.add_job(
        sendMail,
        trigger='cron',
        day_of_week='mon-fri',
        hour='7-16',
        minute=43,
        misfire_grace_time=300,
        max_instances=1
    )

    print("Daytime hourly job registered successfully.")
    
# '''
