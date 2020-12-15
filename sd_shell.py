from utilities import ONLINE_CONTACTS, register_email, user_contact_exist
from utilities import contacts_dict_exist
from network import tcp_client
import utilities
from cmd import Cmd
import json


# Function to get contact info from user
def contact_details():
    name = input("Enter Full Name: ")
    email = register_email()
    return (email, name)


# function that removes old email ID and builds new email ID
# TODO: Clean up code -> need to add a boolean function that just checks if
#                        contacts exists (will move rest of code to do_add
#                        function)
def update_user_contact(email, name):
    count = 0
    fp = open("user_list.json", "r+")
    data = json.load(fp)  # load all json data into a string

    # get the user email
    user_email = list(data["Users"][0].keys())[0]
    print(user_email)
    # get all data associated with user
    u_dictionary = data["Users"][0][user_email]["contacts"]
    print("initial u_dictionary: ", u_dictionary)
    for x in u_dictionary:
        if u_dictionary[count].get("email") == email:
            u_dictionary.pop(count)
            u_dictionary.append({"email": email, "name": name})
            print("updated u_dictionary after pop/append: ", u_dictionary)
            fp.seek(0)
            json.dump(data, fp)
            fp.close()
            return True
        count += 1
    return False


def add_contact():
    fp = open("user_list.json", "r+")
    data = json.load(fp)  # load all json data into a string

    # get the user email
    user_email = list(data["Users"][0].keys())[0]

    # get all data associated with user
    u_dictionary = data["Users"][0][user_email]

    if contacts_dict_exist():  # if user has already added a contact
        email, name = contact_details()
        email_exist = user_contact_exist(
            data["Users"][0][user_email]["contacts"], email
        )  # check to see if the email the user wants to add already exists
        if email_exist:  # email already exists
            fp.close()
            update_user_contact(email, name)
        else:  # email does not exist
            data["Users"][0][user_email]["contacts"].append(
                {"email": email, "name": name}
            )
            fp.seek(0)
            json.dump(data, fp)
            fp.close()
        print("Contact Added.")
    else:  # user has never added a contact before
        # get email and name the user wants to add
        email, name = contact_details()
        u_dictionary["contacts"] = [
            {"email": email, "name": name}
        ]  # create new field name -> contacts
        # add the email and name the user wants to contact to their contacts
        data["Users"][0][
            user_email
        ] = u_dictionary  # add the email and name the user wants to contact to their contacts
        fp.seek(0)  # return file pointer to beginning of json file
        json.dump(data, fp)  # add new information to json file
        print("Contact Added.")
        fp.close()


def send_file(file, email):
    port = 0
    for p in utilities.ONLINE_CONTACTS:
        if p[1] == email:
            port = p[2]
            break
    tcp_client(port, file, True)


class MyPrompt(Cmd):
    prompt = "secure_drop> "
    intro = "Welcome! Type ? to list commands"

    def do_exit(self, inp):
        return True

    def help_exit(self):
        print("exit the application. Shorthand: x q Ctrl-d")

    def do_add(self, inp):
        add_contact()

    def help_add(self):
        print("Add a new contact.")

    def do_send(self, inp):
        email = input("Enter email address: ")
        file = input("Enter File: ")
        send_file(file, email)

    def help_send(self):
        pass

    def do_list(self, inp):
        print(utilities.ONLINE_CONTACTS)

    def help_list(self):
        print("List all online contacts.")

    def default(self, inp):
        if inp == "x" or inp == "q":
            return self.do_exit(inp)
            print("Default {}".format(inp))

    do_EOF = do_exit
    help_EOF = help_exit


def start_cmd():
    MyPrompt().cmdloop()
