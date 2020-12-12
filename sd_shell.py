from utilities import ONLINE_CONTACTS, register_email
from cmd import Cmd
import time
import json
import sched


class ScanTask:
    def __init__(self):
        self._running = True

    def terminate(self):
        self._running = False

    def run(self):
        self.scan_for_online_contacts()

    s = sched.scheduler(time.time, time.sleep)

    # Scheduled function to scan network on a certain socket to determine
    # online contacts.
    # TODO: add implementation in form of separate file.
    def scan(self, sc):
        """
        This function is currently a placeholder for a real scanning
        function/file. Real scan is to be added later. The plan is to have the
        scan return a dictionary and store it in the variable ONLINE_CONTACTS.

        Example code for how this function could interact with ONLINE_CONTACTS
        is as follows:
        global ONLINE_CONTACTS
        ONLINE_CONTACTS = random.randint(100, size=(3))
        """
        if not self._running:
            return None
        self.s.enter(5, 1, self.scan, (sc,))

    # Helper function to run scan on a certain interval. This function is ran
    # on a separate thread.
    def scan_for_online_contacts(self):
        self.s.enter(5, 1, self.scan, (self.s,))
        self.s.run()


# Function to listen on a certain socket for other applications scanning,
# to potentially communicate about online contacts and file transfer. This
# function is ran on a separate thread.
def listen_for_scan():
    pass


# Function to see if "contacts" field exists in json file
def contacts_exist(user_dictionary):
    if "contacts" in user_dictionary:
        return True
    return False


# Function to get contact info from user
def contact_details():
    name = input("Enter Full Name: ")
    email = register_email()
    return (email, name)


# Function to check if the email the user wants to register as a contact
# already exists
def user_contact_exist(user_dictionary, email):
    count = 0
    for x in user_dictionary:
        if user_dictionary[count].get("email") == email:
            return True
        count += 1
    return False


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

    if contacts_exist(u_dictionary):  # if user has already added a contact
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


def list_all_user_contacts():
    user_contact_email_addresses = []
    count = 0

    fp = open("user_list.json", "r+")
    data = json.load(fp)
    fp.close()

    user_email = list(data['Users'][0].keys())[0]
    u_dictionary = data['Users'][0][user_email]['contacts']
    
    for x in u_dictionary:
        user_contact_email_addresses.append(u_dictionary[count].get('email'))
        count += 1
    return user_contact_email_addresses

def add_contact():
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
            #print(list_all_user_contacts())
        else: #user has never added a contact before
            email, name = add_contact() #get email and name the user wants to add
            u_dictionary['contacts'] = [{'email': email, 'name': name}] #create new field name -> contacts
            data['Users'][0][user_email] = u_dictionary #add the email and name the user wants to contact to their contacts
            fp.seek(0) #return file pointer to beginning of json file
            json.dump(data, fp) #add new information to json file
            print("Contact Added.")
            fp.close()
            #print(list_all_user_contacts())


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

    def do_list(self, inp):
        print(ONLINE_CONTACTS)

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
