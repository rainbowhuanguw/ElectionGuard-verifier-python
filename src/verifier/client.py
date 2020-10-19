from typing import Tuple

from generator import FilePathGenerator, FileReader, ParameterGetter, VoteLimitCounter
from baseline_verifier import BaselineVerifier
from encryption_verifier import BallotEncryptionVerifier
from json_parser import read_json_file
import os


def prompt_text_input(message: str, allowed_values: set, lower_case=False) -> str:
    """
    prompts text input and check if it's an allowed value
    :param message: display message
    :param allowed_values: values allowed in a set, all allowed values should be in lower case
    :param lower_case: whether to convert the processed input to all lower case
    :return: processed input
    """
    text_input = input(message).strip()
    while text_input.lower() not in allowed_values:
        print("Invalid input. Try again.", end=' ')
        text_input = input(message).strip()

    return text_input.lower() if lower_case else text_input


def prompt_path_input(message: str, exception_value=None, is_folder=False) -> str:
    """
    prompts file input and check if it's an allowed file or folder path
    :param message: display message
    :param exception_value: values suggesting the user chooses not to input a path here
    :param is_folder: True if this is a folder path
    :return: path
    """
    path_input = input(message).strip()

    if path_input.lower() == exception_value:
        return path_input.lower()

    if not path_input.startswith('/'):
        path_input = '/' + path_input

    if is_folder:
        if not path_input.endswith('/'):
            path_input += '/'
        if os.path.isdir(path_input):
            return path_input
        else:
            print("Invalid input. Try again.", end=' ')
            return prompt_path_input(message, exception_value, True)
    else:
        if path_input.endswith('/'):
            path_input = path_input[:len(path_input) - 2]
        if os.path.isfile(path_input):
            return path_input
        else:
            print("Invalid input. Try again.", end=' ')
            return prompt_path_input(message, exception_value, False)


def setup() -> Tuple:
    """
    verifier setup, prepare file reader, parameter getter, and vote limit counter
    :return: a tuple of (file reader, parameter getter, vote limit counter)
    """
    # prompt data folder path input
    print("\nTell us which election you participated in. We require three files, constants, context, "
          "and description to get the election information.")
    print("Did you store these three files in the same folder?", end=' ')
    folder_or_file = prompt_text_input("Enter Yes or No: ", {"yes", "no", "y", "n"})

    # if input is a data folder
    if folder_or_file in ("yes", "y"):
        data_folder = prompt_path_input("Enter an absolute or relative file path to a data folder: ",
                                        is_folder=True)
        # calls file path generator
        file_path_g = FilePathGenerator(data_folder)
        file_reader = FileReader(file_path_g)
        param_getter = ParameterGetter(file_reader)

    else:
        # no data folder path, prompt input of files paths separately
        # constants and context files are mandatory
        constants_path = prompt_path_input("Enter an absolute or relative file path to the constants file: ")
        context_path = prompt_path_input("Enter an absolute or relative file path to the context file: ")
        description_path = prompt_path_input("Enter an absolute or relative file path to the description file: ")

        # check if files are correct
        file_reader = FileReader(context=context_path,
                                 constants=constants_path,
                                 description=description_path)
        param_getter = ParameterGetter(file_reader)
        constants_check = param_getter.check_constants_file()
        context_check = param_getter.check_context_file()
        description_check = param_getter.check_description_file()

        while not constants_check or not context_check or not description_check:
            if not constants_check:
                print("The constants file path is invalid, try again. ")
                constants_path = prompt_path_input("Enter an absolute or relative file path "
                                                   "to the constants file: ")
            if not context_check:
                print("The context file path is invalid, try again. ")
                context_path = prompt_path_input("Enter absolute or relative file path "
                                                 "to the context file: ")

            if not description_check:
                print("The description file path is invalid, try again. ")
                context_path = prompt_path_input("Enter absolute or relative file path "
                                                 "to the description file: ")

            file_reader = FileReader(context=context_path,
                                     constants=constants_path,
                                     description=description_path)
            param_getter = ParameterGetter(file_reader)
            constants_check = param_getter.check_constants_file()
            context_check = param_getter.check_context_file()
            description_check = param_getter.check_description_file()

    vote_limit_c = VoteLimitCounter(file_reader)

    return file_reader, param_getter, vote_limit_c


def switch_role():
    pass

def switch_action():
    pass


def inspect_a_spoiled_ballot():
    pass


if __name__ == '__main__':
    print("---------- Welcome to ElectionGuard Verifier. ----------------")

    # set up, run baseline verifier and check vote limit
    file_reader, param_getter, vote_limit_c = setup()
    baseline_v = BaselineVerifier(param_getter)
    baseline_v.verify_all_params()
    print("Set up ready. \n")

    print("Please tell us more about yourself, are you a: \n"
          " (a) voter\n"
          " (b) jurisdiction officer\n"
          " (c) other \n")

    # prompt user input
    role = prompt_text_input("Please enter a, b, or c to specify your role: ", {"a", "b", "c"})

    # if voter
    if role == "a":
        print("Hello dear voter, ", end=" ")
        while True:
            print("Please select from one of the following actions you want to perform: \n"
                  " (a) verify your vote\n"
                  " (b) verify election tally\n"
                  " (c) inspect a spoiled ballot\n"
                  " (q) quit \n")

            action = prompt_text_input("Please enter a, b, c, or q to specify your activity: ", {"a", "b", "c", "q"})

            # verify the encryption of a ballot
            if action == "a":
                vote_path = prompt_path_input("Enter an absolute or relative file path to your vote file:")
                vote = read_json_file(vote_path)
                print("...verifying...")
                ballot_v = BallotEncryptionVerifier(vote, param_getter, vote_limit_c)
                encryption_res = ballot_v.verify_all_contests()
                if encryption_res:
                    print("Your votes have been encrypted correctly. ")
                else:
                    print("Seems like something is wrong. ")

            # verify tally
            elif action == "b":
                pass

            # inspect a spoiled ballot
            elif action == "c":
                pass

            # quit
            else:
                break

            continue_or_stop = prompt_text_input("Please enter continue or c to continue, or quit or q to quit. ",
                                                 {"continue", "c", "quit", "q"}, True)
            if continue_or_stop in ("quit", "q"):
                break

    # if jurisdiction officer
    elif role == "b":
        print("Hello dear jurisdiction officer, do you want to: \n"
              " (a) verify a set of encrypted ballots\n"
              " (b) verify election tally\n"
              " (c) inspect spoiled ballots\n"
              " (q) quit \n")

    else:
        pass