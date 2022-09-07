from os import path
from typing import AnyStr

from argparse import ArgumentParser
from base64 import b64encode, b64decode
from bcrypt import hashpw, gensalt


def get_base64_hash(password: AnyStr) -> AnyStr:
    """
    Return a string corresponding to a salted, bcrypt-hashed base-64
    representation of a password.

    :param password: The password to be salted and hashed.
    :type password: str
    :return: The base-64 representation of the hashed password.
    :rtype: str
    """

    hashed = hashpw(password.encode("utf-8"), gensalt())
    hashed64 = b64encode(hashed).decode("utf-8")
    return hashed64


def add_user(user: AnyStr, password: AnyStr, filepath: AnyStr) -> bool:
    """
    Add an authenticated user.

    NOTE: if a user is already in the list of authenticated users, this
    function will do nothing. Use :func:`.modify_user` to change the password
    for an existing user.

    :param user: The new user's name.
    :type user: str
    :param password: The new user's password.
    :type password: str
    :param filepath: Path to the authenticated users text file.
    :type filepath: str
    :return: Boolean indicating whether the user was added.
    :rtype: bool
    """

    user_in_file = False
    if path.isfile(filepath):
        with open(filepath, "r") as file_:
            for line in file_:
                user_, hash_ = line.split("\t")
                if user == user_:
                    user_in_file = True

    if not user_in_file:
        hashed64 = get_base64_hash(password)
        with open(filepath, "a") as file_:
            file_.write("{}\t{}\n".format(user, hashed64))
        return True
    return False


def authenticate_password(password: AnyStr, hashed: bytes):
    """
    Determine whether a password corresponds to a hashed password.

    :param password: Password to check.
    :type password: str
    :param hashed: (Base-64) hashed representation of a password.
    :type hashed: str
    :return: Whether the given password matches the hashed password.
    :rtype: bool
    """
    return hashpw(password.encode("utf-8"), hashed) == hashed


def authenticate_user(user: AnyStr, password: AnyStr, filepath: AnyStr) -> bool:
    """
    Authenticate a user and password.

    :param user: User name.
    :type user: str
    :param password: User password.
    :type password: str
    :param filepath: Path to authenticated users text file.
    :type filepath: str
    :return: Whether or not the user and password match an entry in the list
        of authenticated users.
    :rtype: bool
    """

    if path.isfile(filepath):
        with open(filepath, "r") as file_:
            for line in file_:
                user_, hashed64 = line.strip().split("\t")
                hashed = b64decode(hashed64.encode("utf-8"))
                if user == user_ and authenticate_password(password, hashed):
                    return True
    return False


def delete_user(user: AnyStr, filepath: AnyStr) -> bool:
    """
    Remove a user from the list of authenticated users.

    :param user: User name.
    :type user: str
    :param filepath: Path to authenticated users text file.
    :type filepath: str
    :return: Whether the entry for the user was successfully deleted.
    :rtype: bool
    """

    user_removed = False
    if path.isfile(filepath):
        with open(filepath, "r") as file_:
            lines = file_.readlines()

        with open(filepath, "w") as file_:
            for line in lines:
                user_, hashed64 = line.strip().split("\t")
                if user_ != user:
                    file_.write("{}\t{}\n".format(user_, hashed64))
                else:
                    user_removed = True
            file_.truncate()
    return user_removed


def modify_user(user: AnyStr, password: AnyStr, filepath: AnyStr) -> bool:
    """
    Update the password for an existing user.

    :param user: User name.
    :type user: str
    :param password: New password for the user.
    :type password: str
    :param filepath: Path to authenticated users text file.
    :type filepath: str
    :return: Whether the password for the user was successfully updated.
    :rtype: bool
    """

    user_modified = False
    if path.isfile(filepath):
        with open(filepath, "r") as file_:
            lines = file_.readlines()

        with open(filepath, "w") as file_:
            for line in lines:
                user_, hashed64 = line.strip().split("\t")
                if user_ == user:
                    new_hashed64 = get_base64_hash(password)
                    file_.write("{}\t{}\n".format(user, new_hashed64))
                    user_modified = True
                else:
                    file_.write(line)
    return user_modified


if __name__ == "__main__":
    argument_parser = ArgumentParser()

    action_group = argument_parser.add_mutually_exclusive_group()
    action_group.add_argument("-a", "--add-user", action="store_true")
    action_group.add_argument("-d", "--delete-user", action="store_true")
    action_group.add_argument("-m", "--modify-user", action="store_true")
    action_group.add_argument("-c", "--check-password", action="store_true")

    argument_parser.add_argument("-f", "--filepath", type=str, default="users")
    argument_parser.add_argument("-u", "--user", required=True, type=str)
    argument_parser.add_argument("-p", "--password", type=str)

    args = vars(argument_parser.parse_args())

    if args["add_user"]:
        add_user(args["user"], args["password"], args["filepath"])
    elif args["delete_user"]:
        delete_user(args["user"], args["filepath"])
    elif args["modify_user"]:
        modify_user(args["user"], args["password"], args["filepath"])
    elif args["check_password"]:
        print(authenticate_user(args["user"], args["password"], args["filepath"]))
