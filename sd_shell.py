from cmd import Cmd
from getpass import getpass
import os.path
import json
import re
import crypt
import secrets

MAX_TIMES_ALLOWED_TO_ENTER = 3

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

def get_password():
    password = getpass("Enter password: ")
    return password

def check_email():
    #function check_email allows the user to attempt to enter their password 3 times before exiting 

    # regular expression for validating email
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'

    email_enter_attempts = 0

    while email_enter_attempts < MAX_TIMES_ALLOWED_TO_ENTER:
        email = input("Enter email: ")
        if(re.search(regex, email)):
            print("Valid Email")
            email_enter_attempts = MAX_TIMES_ALLOWED_TO_ENTER
            return email
        else:
            print("Invalid Email")
            email_enter_attempts += 1
    return None
    
def register_email():
    email = input("Enter email: ")
    return email

def hash_password(password, salt):
    return crypt.crypt(password, salt)

# User registration Function.  Checks password for complexity and for
# matching.  If it passes the checks it then hashes the password and stores
# the hash and salt for login later.
#
# TODO: Needs cleanup. The code is messy right now and has some redundancies.
def user_registration(file):
    name = input("Enter Full name: ")
    email = register_email() #get the user's email
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
    json.dump(dict, f)
    file.close()
    #require user to re-login once they have registered (for security reasons)
    print("User sucessfully registered, please login again to begin...")
    exit()

# TODO: Implement code to check if email is registered
def login_helper():
    #function login_helper allows the user to try to enter 
    #their password a maximum of three times before exiting
    number_of_password_login_attempts = 0
    bool = False
    email = check_email()
    #if email is None then the user mis-entered their email three times, so exit
    
    json_data = open(USER_LIST)
    jdata = json.load(json_data)
    user_data = jdata['Users']
    
    # case where email exists in JSON file
    if email in user_data[0]:
        print('Email exists, you may proceed!')
        while number_of_password_login_attempts < MAX_TIMES_ALLOWED_TO_ENTER:
            password = get_password() #get the user's password attempt
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
                number_of_password_login_attempts +=1
    
    elif email not in user_data[0]:
        print('\nUser with that email not registered!')
        print('Exiting\n')
        
    return bool


# TODO: Implement session ID to keep login relevant
def user_login():
    #if login_helper fails (returns False), then exit the program as 
    #the user mis-entered their email or password more than 3 times
    if not login_helper():
        exit()

#Function to see if "contacts" field exists in json file
def contacts_exist(user_dictionary):
    if 'contacts' in user_dictionary:
        return True
    return False

#Function to get contact info from user
def add_contact():
    name = input("Enter Full Name: ")
    email = input("Enter Email Address: ")
    return (email, name)

#Function to check if the email the user wants to register as a contact
#already exists 
def user_contact_exist(user_dictionary, email):
    count = 0
    for x in user_dictionary:
        if user_dictionary[count].get('email') == email:
            return True
        count += 1
    return False

#function that removes old email ID and builds new email ID
# TODO: Clean up code -> need to add a boolean function that just checks if
#                        contacts exists (will move rest of code to do_add function)
def update_user_contact(email, name):
    count = 0
    fp = open("user_list.json", "r+")
    data = json.load(fp) #load all json data into a string
        
    #get the user email
    user_email = list(data['Users'][0].keys())[0]
    print(user_email)
    #get all data associated with user
    u_dictionary = data['Users'][0][user_email]['contacts']
    print("initial u_dictionary: ", u_dictionary)
    for x in u_dictionary:
        if u_dictionary[count].get('email') == email:
            u_dictionary.pop(count)
            u_dictionary.append({'email': email, 'name': name})
            print("updated u_dictionary after pop/append: ", u_dictionary)
            #print("data before the clear: ", data)
            #data['Users'][0][user_email]['contacts'].clear()
            #print("data after the clear: ", data)
            #data['Users'][0][user_email]['contacts'].append(u_dictionary)
            #print("data after addition of u_dictionary ", data)
            fp.seek(0)
            json.dump(data, fp)
            fp.close()    
            return True
        count += 1
    return False 

class MyPrompt(Cmd):
    prompt = "secure_drop> "
    intro = "Welcome! Type ? to list commands"

    def do_exit(self, inp):
        return True

    def help_exit(self):
        print("exit the application. Shorthand: x q Ctrl-d")

    def do_add(self, inp):
        fp = open("user_list.json", "r+")
        data = json.load(fp) #load all json data into a string
    
        #get the user email
        user_email = list(data['Users'][0].keys())[0]
        
        #get all data associated with user
        u_dictionary = data['Users'][0][user_email]

        if contacts_exist(u_dictionary): #if user has already added a contact
            email, name = add_contact()
            email_exist = user_contact_exist(data['Users'][0][user_email]['contacts'], email) #check to see if the email the user wants to add already exists
            if email_exist: #email already exists
                #data['Users'][0][user_email]['contacts'].clear()
                #data['Users'][0][user_email]['contacts'] = u_d_temp
                #fp.seek(0)
                #json.dump(data, fp)
                fp.close()
                update_user_contact(email, name)
                #print("Contact Added.")
            else: #email does not exist
                data['Users'][0][user_email]['contacts'].append({'email': email, 'name': name})
                fp.seek(0)
                json.dump(data, fp)
                fp.close()
            print("Contact Added.")
        else: #user has never added a contact before
            email, name = add_contact() #get email and name the user wants to add
            u_dictionary['contacts'] = [{'email': email, 'name': name}] #create new field name -> contacts
            data['Users'][0][user_email] = u_dictionary #add the email and name the user wants to contact to their contacts 
            fp.seek(0) #return file pointer to beginning of json file 
            json.dump(data, fp) #add new information to json file
            print("Contact Added.")
            fp.close()

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
