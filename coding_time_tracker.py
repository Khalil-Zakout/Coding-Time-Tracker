import psutil
from win10toast import ToastNotifier
import datetime as dt
import time
import sqlite3


def is_program_running():
    process_map = {
        "pycharm":"PyCharm",
        "code":"VS Code",
        "vstudio":"Valentina Studio",
        "excel":"Excel",
        "pbidesktop":"PowerBI",
    }
    
    try:    # Check If a Program Is Running
        for process in psutil.process_iter():
            process_name = process.name().lower()

            for keyword, program_name in process_map.items():
                if keyword in process_name:
                    return program_name

    except(psutil.NoSuchProcess,psutil.ZombieProcess,psutil.AccessDenied):
        pass  # Skip the process if we can't access it

    return False



def storing_in_database(start_time, finish_time, duration, program):
    try:
        with sqlite3.connect("Program Usage.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""INSERT INTO sessions (start_time, finish_time, duration, program) VALUES (?,?,?,?)"""
                         ,(start_time.strftime("%Y-%m-%d %H:%M:%S"),finish_time.strftime("%Y-%m-%d %H:%M:%S"),duration, program))

            conn.commit()
    except(Exception) as e:
        print(f"Error: {e}")



def show_notification(program,duration):
    toaster = ToastNotifier()
    toaster.show_toast(
        "Time Alert",
            f"You Have Been Using {program} For {duration} Minutes 🕐\nTake a Break 🤍",
        icon_path= r"./icon.ico",
        duration=10)



def track_program_usage():
    try:
        while True:    # Ensures The Program Is Always Running In The Background
            program_name = is_program_running()
            if program_name:

                start_time = dt.datetime.now()
                first_notification_sent = False    # 45-Minute Flag Reminder
                second_notification_sent = False   # 1-Hour Flag Reminder

                print("Starting Time Now")

                while is_program_running() == program_name:    # While Same program is still running
                    time.sleep(30) # Wait for 30 seconds before checking again if it is still running

                    current_duration = (dt.datetime.now()-start_time).total_seconds()
                    if current_duration > 2700 and first_notification_sent is False:    # If The Session Exceeds 45 Minutes
                        show_notification(program_name,45)
                        first_notification_sent = True

                    elif current_duration > 3600 and second_notification_sent is False:
                        show_notification(program_name,60)
                        second_notification_sent = True



                finish_time = dt.datetime.now()
                print("Finishing Time Now")

                duration_seconds = (finish_time-start_time).total_seconds()
                duration_minutes = round(duration_seconds / 60 ,2)

                storing_in_database( start_time, finish_time, duration_minutes, program_name)
                print("Inserting To Database Success !!")

            time.sleep(10)    # Wait 10 seconds before checking again if program is running (reduce CPU usage)

    except(Exception) as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    track_program_usage()