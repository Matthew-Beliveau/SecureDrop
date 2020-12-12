from utilities import register_email, get_password, password_check
from utilities import hash_password
from getpass import getpass
import json
import secrets


# User registration Function.  Checks password for complexity and for
# matching.  If it passes the checks it then hashes the password and stores
# the hash and salt for login later.
#
# TODO: Needs cleanup. The code is messy right now and has some redundancies.
def user_registration(file):
    name = input("Enter Full name: ")
    email = register_email()  # get the user's email
    password = get_password()
    second_pass = getpass("Re-enter Password: ")
    check = password_check(password)

    # loop until password is correct.  This can be better written.
    while not check.get("password_ok") or password != second_pass:
        if password != second_pass:
            print("Passwords don't match.")
        elif not check.get("password_ok"):
            print(
                "Password not strong enough. A password is considered strong if:"
                "\n8 characters length or more"
                "\n1 digit or more"
                "\n1 symbol or more"
                "\n1 uppercase letter or more"
                "\n1 lowercase letter or more."
            )
        password = getpass("Enter password:")
        second_pass = getpass("Re-enter Password")
        check = password_check(password)

    salt = secrets.token_hex(8)
    h_password = hash_password(password, salt)

    dict = {}
    dict["Users"] = []
    dict["Users"].append({email: {"name": name, "password": h_password, "salt": salt}})
    json.dump(dict, file)
    file.close()
    # require user to re-login once they have registered (for security reasons)
    print("User sucessfully registered, please login again to begin...")
    exit()
