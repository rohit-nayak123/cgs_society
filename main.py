import json
import requests

timetable = []
email = None

while True:
    print("\n===== Timetable Menu =====")
    print("1. Add a Class / Slot")
    print("2. Save the Timetable")
    print("3. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":

        if email is None:
            email = input("Enter Email: ")

        day = input("Enter Day (Mon, Tue, Wed, Thu, Fri): ")
        subject = input("Enter Subject Code : ")
        location = input("Enter Class Room Number : ")
        duration = int(input("Enter Duration (in hours): "))
        starting_time = int(input("Enter Starting Time : "))

        slot = {
            "location": location,
            "email": email,
            "Stime": starting_time,
            "Day": day,
            "subject": subject,
            "duration": duration
        }

        timetable.append(slot)

        print("\nClass added successfully!")

    elif choice == "2":
        if len(timetable) == 0:
            print("Enter your Class.")
        else:
            reqUrl = "https://cgs-society.onrender.com/timetable"
            headers = {
                "Accept": "*/*",
                "Content-Type": "application/json"
            }

            data = json.dumps(timetable)

            response = requests.request(
                "POST", reqUrl, data=data,  headers=headers)

            print("\nSaved in the database. ")
            timetable = []

    elif choice == "3":

        print("Exiting...")
        break

    else:
        print("Invalid choice!")
