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
                user_, hashed = line.split("\t")
                if user == user_:
                    user_in_file = True

    if not user_in_file:
        hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
        hashed64 = base64.b64encode(hashed).decode("utf-8")
        with open(filepath, "a") as file_:
            file_.write("{}\t{}\n".format(user, hashed64))
        return True
    return False

if __name__ == "__main__":
    #argparser = argparse.ArgumentParser()
    #argparser.add_argument("
    user = sys.argv[1]
    password = sys.argv[2]
    filepath = sys.argv[3]

    add_user(user, password, filepath)
