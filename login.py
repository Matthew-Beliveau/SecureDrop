from utilities import USER_LIST, MAX_TIMES_ALLOWED_TO_ENTER
from utilities import check_email, get_password, hash_password
import json


def login_helper():
    # function login_helper allows the user to try to enter
    # their password a maximum of three times before exiting
    number_of_password_login_attempts = 0
    bool = False
    email = check_email()
    # if email is None then the user mis-entered their email three times,
    # so exit

    json_data = open(USER_LIST)
    jdata = json.load(json_data)
    user_data = jdata["Users"]

    # case where email exists in JSON file
    if email in user_data[0]:
        print("Email exists, you may proceed!")
        while number_of_password_login_attempts < MAX_TIMES_ALLOWED_TO_ENTER:
            password = get_password()  # get the user's password attempt
            old_pass = ""
            salt = ""
            with open(USER_LIST) as f:
                data = json.load(f)
                for p in data["Users"]:
                    salt = p[email]["salt"]
                    old_pass = p[email]["password"]
            new_pass = hash_password(password, salt)
            if old_pass == new_pass:
                print("password is correct")
                bool = True
                number_of_password_login_attempts = 4
            else:
                print("password is incorrect")
                bool = False
                number_of_password_login_attempts += 1

    elif email not in user_data[0]:
        print("\nUser with that email not registered!")
        print("Exiting\n")

    return bool


# TODO: Implement session ID to keep login relevant
def user_login():
    # if login_helper fails (returns False), then exit the program as
    # the user mis-entered their email or password more than 3 times
    if not login_helper():
        exit()
