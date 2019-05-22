import argparse
import base64
import os
import sys

import bcrypt

def add_user(user, password, filepath):
    user_in_file = False
    if os.path.isfile(filepath):
        with open(filepath, "r") as file_:
            for line in file_:
                user_, hash_ = line.split("\t")
                if user == user_:
                    user_in_file = True

    if not user_in_file:
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        hashed64 = base64.b64encode(hashed).decode("utf-8")
        with open(filepath, "a") as file_:
            file_.write("{}\t{}\n".format(user, hashed64))
        return True
    return False

def authenticate_password(password, hash_):
    return bcrypt.hashpw(password, hash_)

def authenticate_user(user, password, filepath):
    if os.path.isfile(filepath):
        with open(filepath, "r") as file_:
            for line in file_:
                user_, hash_ = line.split("\t")
                if user == user_ and authenticate_password(password, hash_):
                    return True
    return False

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()

    action_group = argparser.add_mutually_exclusive_group()
    action_group.add_argument("-a", "--add-user", action="store_true")
    action_group.add_argument("-d", "--delete-user", action="store_true")
    action_group.add_argument("-m", "--modify-user", action="store_true")

    argparser.add_argument("-f", "--filepath", type=str, default="users")
    argparser.add_argument("-u", "--user", required=True, type=str)
    argparser.add_argument("-p", "--password", type=str)

    args = vars(argparser.parse_args())

    if args["add_user"]:
        add_user(args["user"], args["password"], args["filepath"])
    #elif args["delete_user"]:
    #    delete_user(args["user"], args["filepath"])
    #elif args["modify_user"]:
    #    modify_user(args["user"], args["password"], args["filepath"])
