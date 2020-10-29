from cmd import Cmd
from getpass import getpass
import os.path
import json
import re
import crypt
import pwd


USER_LIST = "./user_list.json"


class User:
    email = ""
    password = ""
    contacts = []


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


def hash_password(password):
    pass


def user_registration(file):
    user = User()
    user.email = input("Enter email:")
    user.password = getpass("Enter password:")
    check = password_check(user.password)
    # loop untill password is correct.  This can be better written.
    while not check.get("password_ok"):
        print(
            "Password not strong enough. A password is considered strong if:"
            "\n8 characters length or more"
            "\n1 digit or more"
            "\n1 symbol or more"
            "\n1 uppercase letter or more"
            "\n1 lowercase letter or more"
        )
        user.email = input("Enter email:")
        user.password = getpass("Enter password:")
        check = password_check(user.password)

    hash_password(user.password)
    dict = {}
    dict["emails"] = []
    dict["emails"].append({"email": user.email, "password": user.password})
    json.dump(dict, f)
    file.close()


def user_login():
    pass


class MyPrompt(Cmd):
    prompt = "secure_drop> "
    intro = "Welcome! Type ? to list commands"

    def do_exit(self, inp):
        print("bye")
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
        f = open(USER_LIST, "w")
        user_registration(f)

    MyPrompt().cmdloop()
