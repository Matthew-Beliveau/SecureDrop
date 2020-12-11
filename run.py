from utilities import USER_LIST
from login import user_login
from user_registration import user_registration
from sd_shell import ScanTask, listen_for_scan, start_cmd
from threading import Thread
import os.path


# Handles the initial login. If there is not registered users, the function
# will run user_registration(file)
def start_up():
    """
    The user registration is a one-time process. Once a user is registered on a
    client, the login module is activated subsequently. After a successful
    login, a "secure_drop>" shell is started.
    """
    if os.path.isfile(USER_LIST) and os.path.getsize(USER_LIST) > 0:
        user_login()
    else:
        print(
            "No users are registered with this client."
            "\nDo you want to register a new user (y/n)?"
        )
        inp = ""
        while inp != "y" and inp != "n":
            inp = input()
        if inp == "y":
            f = open(USER_LIST, "w")
            user_registration(f)
        elif inp == "n":
            exit(1)


def run():
    start_up()

    sc = ScanTask()
    scanner = Thread(target=sc.scan_for_online_contacts)
    listener = Thread(target=listen_for_scan)
    cmd = Thread(target=start_cmd)

    scanner.start()
    listener.start()
    cmd.start()
    cmd.join()
    listener.join()

    sc.terminate()
    scanner.join()
