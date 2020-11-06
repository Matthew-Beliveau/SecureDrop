from cmd import Cmd
from getpass import getpass
import os.path
import json
import re
import crypt
import secrets


USER_LIST = "./user_list.json"


def password_check(password):
    """
    Verify the strength of 'password'
    Returns a dict indicating the wrong criteria
    A password is considered strong if:
        8 characters length or more
        1 digit or more
        1 symbol or more
        1 uppercase letter or more
        1 lowercase letter or more
    """
    # length
    length_error = len(password) < 8

    # searching for digits
    digit_error = re.search(r"\d", password) is None

    # searching for uppercase
    uppercase_error = re.search(r"[A-Z]", password) is None

    # searching for lowercase
    lowercase_error = re.search(r"[a-z]", password) is None

    # searching for symbols
    symbol_error = re.search(r"\W", password) is None

    # overall result
    password_ok = not (
        length_error
        or digit_error
        or uppercase_error
        or lowercase_error
        or symbol_error
    )

    return {
        "password_ok": password_ok,
        "length_error": length_error,
        "digit_error": digit_error,
        "uppercase_error": uppercase_error,
        "lowercase_error": lowercase_error,
        "symbol_error": symbol_error,
    }


def credentials():
    email = check_email()
    # add method to check if email is valid
    password = getpass("Enter password: ")
    return (email, password)


def check_email():
    # regular expression for validating email
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    i = 1
    
    while i == 1:
        email = input("Enter email: ")

        if(re.search(regex, email)):
            print("Valid Email")
            i = 0
        else:
            print("Invalid Email")
    
    return email
    


def hash_password(password, salt):
    return crypt.crypt(password, salt)


# User registration Function.  Checks password for complexity and for
# matching.  If it passes the checks it then hashes the password and stores
# the hash and salt for login later.
#
# TODO: Needs cleanup. The code is messy right now and has some redundancies.
#       - could create a function out of pw error section 
def user_registration(file):
    name = input("Enter Full name: ")
    creds = credentials()
    email = creds[0]
    password = creds[1]
    second_pass = getpass("Re-enter Password")
    check = password_check(password)

    # loop until password is correct.  This can be better written.
    while not check.get("password_ok") or password != second_pass:
        if password != second_pass:
            print("Passwords don't match.")
        elif not check.get("password_ok"):
            
            # print out the correct password error
            if check.get("length_error"):
                print('8 characters in length or more!')
            if check.get("digit_error"):
                print('1 digit or more')
            if check.get("symbol_error"):
                print('1 symbol or more')
            if check.get("uppercase_error"):
                print('1 uppercase letter or more')
            if check.get("lowercase_error"):
                print('lowercase letter or more.')
    
        password = getpass("Enter password:")
        second_pass = getpass("Re-enter Password")
        check = password_check(password)

    salt = secrets.token_hex(8)
    h_password = hash_password(password, salt)

    dict = {}
    dict["Users"] = []
    dict["Users"].append({email: {"name": name, "password": h_password, "salt": salt}})
    json.dump(dict, f)
    file.close()


# TODO: Implement code to check if email is registered
def login_helper():
    bool = False
    creds = credentials()
    email = creds[0]
    
    # testing how to check if email exists in JSON file
    if email in USER_LIST:
        print("Email exists!")
    if email not in USER_LIST:
        print("Email not in user list?")
    
    
    # testing how to check if email exists in JSON file

    
    password = creds[1]
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
    else:
        print("password is incorrect")
        bool = False
    return bool


# TODO: Implement session ID to keep login relevant
def user_login():
    count = 0
    while count < 3:
        if not login_helper():
            count += 1
        else:
            count = 4


class MyPrompt(Cmd):
    prompt = "secure_drop> "
    intro = "Welcome! Type ? to list commands"

    def do_exit(self, inp):
        return True

    def help_exit(self):
        print("exit the application. Shorthand: x q Ctrl-d")

    def do_add(self, inp):
        print("adding '{}'".format(inp))

    def help_add(self):
        print("Add a new contact.")

    def do_list(self, inp):
        print("list contacts")

    def help_list(self):
        print("List all online contacts.")

    def default(self, inp):
        if inp == "x" or inp == "q":
            return self.do_exit(inp)
            print("Default {}".format(inp))

    do_EOF = do_exit
    help_EOF = help_exit


if __name__ == "__main__":

    """
    The user registration is a one-time process. Once a user is registered on a
    client, the login module is activated subsequently. After a successful
    login, a "secure_drop>" shell is started.
    """
    # could potentially use open("user_list, x") in a try catch for this
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

    MyPrompt().cmdloop()
