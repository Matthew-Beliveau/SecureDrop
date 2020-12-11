import re
from getpass import getpass
import crypt

MAX_TIMES_ALLOWED_TO_ENTER = 3

USER_LIST = "./user_list.json"

ONLINE_CONTACTS = []


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


def get_password():
    password = getpass("Enter password: ")
    return password


def register_email():
    email = input("Enter email: ")
    return email


def get_email_and_password():
    password = get_password()
    email = register_email()
    return (email, password)


def check_email():
    # function check_email allows the user to attempt to enter their password
    # 3 times before exiting

    # regular expression for validating email
    regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"

    email_enter_attempts = 0

    while email_enter_attempts < MAX_TIMES_ALLOWED_TO_ENTER:
        email = input("Enter email: ")
        if re.search(regex, email):
            print("Valid Email")
            email_enter_attempts = MAX_TIMES_ALLOWED_TO_ENTER
            return email
        else:
            print("Invalid Email")
            email_enter_attempts += 1
    return None


def hash_password(password, salt):
    return crypt.crypt(password, salt)
