import os
import glob
from number import mod_p
from json_parser import read_json_file


class FilePathGenerator:
    """
    This class is responsible for navigating to different data files in the given dataset folder,
    the root folder path can be changed to where the whole dataset is stored and its inner structure should
    remain unchanged.
    """

    def __init__(self, root_folder_path=''):
        """
        generate a file name generator with parameters from the json files
        """
        self.DATA_FOLDER_PATH = root_folder_path
        self.FILE_TYPE_SUFFIX = '.json'
        self.FOLDER_SUFFIX = '/'

    def get_coefficients_folder_path(self) -> str:
        """
        get the folder path to the coefficients
        :return:
        """
        coeff_folder_path = '/coefficients'
        return self.DATA_FOLDER_PATH + coeff_folder_path + self.FOLDER_SUFFIX

    def get_guardian_coefficient_file_path(self, index: int) -> str:
        """
        generate a coefficient file path given the guardian's index
        :param index: index of a guardian, (0 - number of guardians)
        :return: a string of the coefficient
        """
        coeff_file_path = 'coefficient_validation_' \
                          'set_hamilton-county-canvass-board-member-'

        return self.get_coefficients_folder_path() + coeff_file_path + str(index) + self.FILE_TYPE_SUFFIX

    def get_context_file_path(self) -> str:
        """
        gets the file path to the context.json file
        :return: a string representation of file path to the context.json file
        """
        return self.DATA_FOLDER_PATH + 'context' + self.FILE_TYPE_SUFFIX

    def get_constants_file_path(self) -> str:
        """
        gets the file path to the constants.json file
        :return: a string representation of file path to the constants.json file
        """
        return self.DATA_FOLDER_PATH + 'constants' + self.FILE_TYPE_SUFFIX

    def get_tally_file_path(self) -> str:
        """
        gets the file path to the tally.json file
        :return: a string representation of file path to the tally.json file
        """
        return self.DATA_FOLDER_PATH + 'tally' + self.FILE_TYPE_SUFFIX

    def get_description_file_path(self) -> str:
        """
        gets the file path to the description.json file
        :return: a string representation of file path to the description.json file
        """
        return self.DATA_FOLDER_PATH + 'description' + self.FILE_TYPE_SUFFIX

    def get_encrypted_ballot_folder_path(self) -> str:
        """
        get a path to the encrypted_ballots folder
        :return: a string representation of path to the encrypted_ballots folder
        """

        return self.DATA_FOLDER_PATH + 'encrypted_ballots' + self.FOLDER_SUFFIX

    def get_spoiled_ballot_folder_path(self) -> str:
        """
        get a path to the spoiled_ballots folder
        :return: a string representation of path to the spoiled_ballots folder
        """
        return self.DATA_FOLDER_PATH + '/spoiled_ballots' + self.FILE_TYPE_SUFFIX

    def get_spoiled_ballot_file_paths(self) -> list:
        """
        get paths of all spoiled ballot files in the folder
        :return: a list of string representation of paths to the spoiled_ballots folder
        """
        spoiled_ballot_folder_path = self.get_spoiled_ballot_folder_path()
        return next(os.walk(spoiled_ballot_folder_path))[2]

    def get_device_folder_path(self) -> str:
        """
        get a path to the devices folder
        :return: a string representation of path to the devices.json file
        """
        return self.DATA_FOLDER_PATH + '/devices' + self.FILE_TYPE_SUFFIX


def get_field_as_int(dic: dict, field: str) -> int:
    """
    get a field in the dictionary given key
    :param dic: data stored in dictionary
    :param field: key
    :return: integer representation of the target field if found, if not, return -1
    """
    return int(dic.get(field)) if field in dic.keys() else -1


class FileReader:
    def __init__(self, path_g=None, **kwargs):
        """
        initializer
        :param path_g: FilePathGenerator that helps to get the paths of files
        """
        self.path_g = path_g
        self.data = kwargs

    def get_context(self) -> dict:
        """
        get all context information as a dictionary
        :return: a dictionary of context info
        """
        if self.__path_g_exists():
            context_path = self.path_g.get_context_file_path()
            return read_json_file(context_path)
        if "context" in self.data.keys():
            context_path = self.data.get("context")
            return read_json_file(context_path)
        return {}

    def get_constants(self) -> dict:
        """
        get all constants as a dictionary
        :return: a dictionary of constants info
        """
        if self.__path_g_exists():
            constants_path = self.path_g.get_constants_file_path()
            return read_json_file(constants_path)
        if "constants" in self.data.keys():
            constants_path = self.data.get("constants")
            return read_json_file(constants_path)
        return {}

    def get_description(self) -> dict:
        """
        get the election description information as dictionary
        :return: a dictionary representation of the description.json
        """
        if self.__path_g_exists():
            description_path = self.path_g.get_description_file_path()
            return read_json_file(description_path)
        if "description" in self.data.keys():
            description_path = self.data.get("description")
            return read_json_file(description_path)
        return {}

    def set_coefficients(self, coefficient_paths: list):
        """
        set a list of coefficients path to file reader
        if coefficients exists as a key, append; if the key doesn't exist, then add
        """
        self.data["coefficients"] = coefficient_paths

    def get_coefficients_by_index(self, indx: int) -> dict:
        """
        get coefficient file path by index in the list
        :param indx: guardian index
        :return: a dictionary representation of the coefficients file of a particular guardian of index i
        """
        if self.__path_g_exists():
            coefficients_path = self.path_g.get_guardian_coefficient_file_path(indx)
            return read_json_file(coefficients_path)
        if "coefficients" in self.data.keys():
            # rearrange by name, in-place sort
            self.data["coefficients"].sort()
            return read_json_file(self.data["coefficients"][indx])
        return {}

    def set_spoiled_ballot(self, spoiled_ballot_path: str):
        """
        set spoiled ballot file path with input
        :param spoiled_ballot_path: a String representation of the spoiled ballot path
        """
        if not self.__path_g_exists():
            self.data["spoiled"] = spoiled_ballot_path

    def get_spoiled_ballot_files(self) -> list:
        """
        get a list of dictionaries of spoiled ballot information
        :return: a list of dictionary of spoiled ballot
        """
        if self.__path_g_exists():
            spoiled_paths = self.path_g.get_spoiled_ballot_file_paths()
            if len(spoiled_paths):
                return []
            for path in spoiled_paths:
                yield read_json_file(path)
        else:
            if "spoiled" not in self.data.keys() or len(self.data["spoiled"]) == 0:
                return []
            for path in self.data["spoiled"]:
                yield read_json_file(path)

    def set_device_file(self, device_file_path: str):
        """
        set the device file path with input
        """
        if not self.__path_g_exists():
            self.data["device"] = device_file_path

    def get_device_file(self) -> dict:
        """
        return the device information as a dictionary
        :return:
        """
        if self.__path_g_exists():
            device_folder_path = self.path_g.get_device_folder_path()
            for file in glob.glob(device_folder_path + '*json'):
                return read_json_file(file)
        if "device" in self.data.keys():
            return read_json_file(self.data["device"])

        return {}

    def __path_g_exists(self) -> bool:
        """
        check if the FilePathGenerator is used in this class
        :return: True if the FilePathGenerator is passed in to construct a FileReader
        """
        return self.path_g is not None and isinstance(self.path_g, FilePathGenerator)


class ParameterGetter:
    """
    This class should be responsible for accessing parameters stored in dataset files
    with the help of the file path file generator to locate the files. Parameters in this
    case only include those that are higher than ballot-level. Those that are directly related
    to each specific ballot, contest, or selection will be taken care of by each level of verifiers.
    """

    def __init__(self, file_reader: FileReader):
        self.reader = file_reader

    def check_constants_file(self) -> bool:
        """
        check if the given constants.json has all the desired fields, including large prime, small prime, generator,
        cofactor
        :return: True if the file has all these fields
        """
        if not bool(self.reader.get_constants()):
            return False
        return (self.get_large_prime() != -1 and self.get_small_prime() != -1
                and self.get_generator() != -1 and self.get_cofactor() != -1)

    def check_context_file(self) -> bool:
        """
        check if the given context.json has all the desired fields, including extended hash, base hash,
        elgamal public key, quorum, number of guardians
        :return: True if the file has all these fields
        """
        if not bool(self.reader.get_context()):
            return False
        return (self.get_base_hash() != -1 and self.get_extended_hash() != -1
                and self.get_elgamal_key() != -1 and self.get_quorum() != -1 and self.get_num_of_guardians() != -1)

    def check_description_file(self) -> bool:
        """
        check if the given description.json file has all the desired fields, including: ballot styles, candidates,
        contact_information, contests, election_scope_id, start_date, end_date, geopolitical_units, name, parties, typ.
        hardcoded here
        :return:
        """
        # TODO: how to avoid hardcode
        if not bool(self.reader.get_description()):
            return False
        return {'ballot_styles', 'candidates', 'contact_information', 'contests', 'election_scope_id', 'start_date',
                'end_date', 'geopolitical_units', 'name', 'typ'}.issubset(self.reader.get_description().keys())

    def get_generator(self) -> int:
        """
        get generator, set default name to be generator
        :return: generator 'g' in integer
        """
        return get_field_as_int(self.reader.get_constants(), 'generator')

    def get_large_prime(self) -> int:
        """
        get large prime p
        :return: large prime 'p' in integer
        """
        return get_field_as_int(self.reader.get_constants(), 'large_prime')

    def get_small_prime(self) -> int:
        """
        get small prime q
        :return: small prime 'q' in integer
        """
        return get_field_as_int(self.reader.get_constants(), 'small_prime')

    def get_cofactor(self) -> int:
        """
        get cofactor r
        :return: cofactor 'r' in integer
        """
        return get_field_as_int(self.reader.get_constants(), 'cofactor')

    def get_extended_hash(self) -> int:
        """
        get extended base hash Q-bar
        :return: extended base hash Q-bar in integer
        """
        return get_field_as_int(self.reader.get_context(), 'crypto_extended_base_hash')

    def get_base_hash(self) -> int:
        """
        get extended base hash Q
        :return: base hash Q in integer
        """
        return get_field_as_int(self.reader.get_context(), 'crypto_base_hash')

    def get_elgamal_key(self) -> int:
        """
        get Elgamal key K
        :return: Elgamal key K in integer
        """
        return get_field_as_int(self.reader.get_context(), 'elgamal_public_key')

    def get_quorum(self) -> int:
        """
        get the minimum number of presenting guardians in this election
        :return: the minimum number of presenting guardians in integer
        """
        return get_field_as_int(self.reader.get_context(), 'quorum')

    def get_public_key_of_a_guardian(self, index: int) -> int:
        """
        get the public key Ki of a guardian
        :param index: guardian index
        :return: public key Ki of guardian i in integer
        """
        coefficient = self.reader.get_coefficients_by_index(index)
        return int(coefficient.get('coefficient_commitments')[0])

    def get_public_keys_of_all_guardians(self) -> list:
        """
        get all the public keys of all guardians as a list
        :return: a list of guardians' public keys
        """
        num_of_guardians = self.get_num_of_guardians()
        return [self.get_public_key_of_a_guardian(i) for i in range(num_of_guardians)]

    def get_num_of_guardians(self) -> int:
        """
        check consistency and return the number of guardians of this election
        :return: number of guardians in integer if the number is the same from context file and coefficient folder
                if the number is inconsistent, returns -1
        """
        return get_field_as_int(self.reader.get_context(), 'number_of_guardians')

    def get_device_id(self) -> str:
        """
        get the id of recording device
        :return: the device id as string
        """
        dic = self.reader.get_device_file()
        if len(dic) > 0 and "uuid" in dic.keys():
            return dic.get("uuid")

        return ""

    def get_location(self) -> str:
        """
        get the location information of the election
        :return: location information as a string
        """
        dic = self.reader.get_device_file()
        if len(dic) > 0 and "location" in dic.keys():
            return dic.get('location')

        return ""


class VoteLimitCounter:
    """
    This VoteLimitCounter class keeps track of the vote limits of all the contests in an election, generates a
    dictionary of "contest name - maximum votes allowed" pairs. Used in the encryption verifier.
    """

    def __init__(self, file_reader: FileReader):
        self.description_dic = file_reader.get_description()
        self.contest_vote_limits = {}

    def get_contest_vote_limits(self) -> dict:
        """
        get the vote limits of a specific contest, used to confirm a ballot's correctness,
        whether the vote exceeds the vote limits of any contests in this ballots
        :return: a dictionary of contest vote limits of all the contests in this election
        """
        # fill in dictionary when it's empty
        if not bool(self.contest_vote_limits):
            self.__fill_contest_vote_limits()

        return self.contest_vote_limits

    def __fill_contest_vote_limits(self):
        """
        fill in the num_max_vote dictionary, key- contest name, value- maximum votes allowed for this contest
        source: description
        """
        contests = self.description_dic.get('contests')
        for contest in contests:
            contest_name = contest.get('object_id')
            num_max_vote = contest.get('votes_allowed')
            self.contest_vote_limits[contest_name] = int(num_max_vote)


class SelectionInfoAggregator:
    """
    This SelectionInfoAggregator class aims at collecting and storing all the selection information across contest
     in one place. Its final purpose is to create a list of dictionaries, each dictionary stands for a contest, inside a
     dictionary are corresponding selection name and its alpha or beta values. Used in decryption verifier.
    """

    def __init__(self, path_g: FilePathGenerator, file_reader: FileReader):
        self.file_reader = file_reader
        self.path_g = path_g
        self.order_names_dic = {}  # a dictionary to store the contest names and its sequence
        self.names_order_dic = {}
        self.contest_selection_names = {}  # a dictionary to store the contest names and its selection names
        self.dics_by_contest = []  # a list to store all the dics, length = 2 * contest_names
        self.total_pad_dic = {}
        self.total_data_dic = {}

    def get_dics(self):
        """
        get the whole list of dictionaries of contest selection information
        :return:a list of dictionaries of contest selection information
        """
        if len(self.dics_by_contest) == 0:
            self.__create_inner_dic()
            self.__fill_in_dics()
        return self.dics_by_contest

    def get_dic_id_by_contest_name(self, contest_name: str, typ: str) -> int:
        """
        get the corresponding dictionary id in the dictionary list by the name of contest
        :param contest_name: name of a contest, noted as "object id" under contest
        :param typ: a or b, a stands for alpha, b stands for beta, to denote what values the target dictionary contains
        :return: a dictionary of alpha or beta values of all the selections of a specific contest
        """
        if typ == 'a':
            return 2 * self.order_names_dic[contest_name]
        elif typ == 'b':
            return 2 * self.order_names_dic[contest_name] + 1

    def __create_inner_dic(self):
        """
        create 2 * contest names number of dicts. Two for each contest, one for storing pad values,
        one for storing data values. Fill in column names with selections in that specific contest
        :return: none
        """
        # get number of contest names
        if len(self.order_names_dic.keys()) == 0:
            self.__fill_in_contest_dicts()

        num = len(self.order_names_dic.keys())

        # create 2 * contest name number of lists
        for i in range(num * 2):

            # get the corresponding contest and selections of this list
            contest_idx = int(i / 2)
            contest_name = self.names_order_dic.get(contest_idx)
            selection_names = self.contest_selection_names.get(contest_name)

            # create new dict
            curr_dic = {}
            for selection_name in selection_names:
                curr_dic[selection_name] = ''  # store strings not integers in dic

            # append to dic list
            self.dics_by_contest.append(curr_dic)

    def __fill_in_dics(self):
        """
        loop over the folder that stores all encrypted ballots once, go through every ballot to get the selection
        alpha/pad and beta/data
        :return: none
        """
        # get to the folder
        ballot_folder_path = self.path_g.get_encrypted_ballot_folder_path()

        # loop over every ballot file
        for ballot_file in glob.glob(ballot_folder_path + '*json'):
            ballot = read_json_file(ballot_file)
            ballot_state = ballot.get('state')

            # ignore spoiled ballots
            if ballot_state == 'CAST':

                # loop over every contest
                contests = ballot.get('contests')
                for contest in contests:
                    contest_name = contest.get('object_id')
                    selections = contest.get('ballot_selections')
                    contest_idx = self.order_names_dic.get(contest_name)
                    curr_pad_dic = self.dics_by_contest[contest_idx * 2]
                    curr_data_dic = self.dics_by_contest[contest_idx * 2 + 1]

                    # loop over every selection
                    for selection in selections:
                        selection_name = selection.get('object_id')
                        is_placeholder_selection = selection.get('is_placeholder_selection')

                        # ignore placeholders
                        if not is_placeholder_selection:
                            pad = selection.get('ciphertext', {}).get('pad')
                            data = selection.get('ciphertext', {}).get('data')
                            self.__get_accum_product(curr_pad_dic, selection_name, int(pad))
                            self.__get_accum_product(curr_data_dic, selection_name, int(data))

    @staticmethod
    def __get_accum_product(dic: dict, selection_name: str, num: int):
        """
        get the accumulative product of alpha/pad and beta/data for all the selections
        :param dic: the dictionary alpha or beta values are being added into
        :param selection_name: name of a selection, noted as "object id" under a selection
        :param num: a number being multiplied to get the final product
        :return: none
        """
        if dic.get(selection_name) == '':
            dic[selection_name] = str(num)
        else:
            temp = int(dic[selection_name])
            product = mod_p(temp * num)
            dic[selection_name] = str(product)

    def __fill_total_pad_data(self):
        """
        loop over the tally.json file and read alpha/pad and beta/data of each non dummy selections in all contests,
        store these alphas and betas in the corresponding contest dictionary
        :return: none
        """
        tally_path = self.path_g.get_tally_file_path()
        tally = read_json_file(tally_path)
        contests = tally.get('contests')
        contest_names = list(contests.keys())
        for contest_name in contest_names:
            curr_dic_pad = {}
            curr_dic_data = {}
            contest = contests.get(contest_name)
            selections = contest.get('selections')
            selection_names = list(selections.keys())
            for selection_name in selection_names:
                selection = selections.get(selection_name)
                total_pad = selection.get('message', {}).get('pad')
                total_data = selection.get('message', {}).get('data')
                curr_dic_pad[selection_name] = total_pad
                curr_dic_data[selection_name] = total_data
            self.total_pad_dic[contest_name] = curr_dic_pad
            self.total_data_dic[contest_name] = curr_dic_data

    def __fill_in_contest_dicts(self):
        """
        get contest names, its corresponding sequence, and its corresponding selection names from description,
        (1) order_names_dic : key - sequence order, value - contest name
        (2) contest_selection_names: key - contest name, value - a list of selection names
        :return: None
        """
        description_dic = self.file_reader.get_description()
        contests = description_dic.get('contests')

        for contest in contests:
            # fill in order_names_dic dict
            # get contest names
            contest_name = contest.get('object_id')
            # get contest sequence
            contest_sequence = contest.get('sequence_order')
            self.order_names_dic[contest_name] = contest_sequence
            self.names_order_dic[contest_sequence] = contest_name

            # fill in contest_selection_names dict
            curr_list = []
            self.contest_selection_names[contest_name] = curr_list
            selections = contest.get('ballot_selections')
            for selection in selections:
                # get selection names
                selection_name = selection.get('object_id')
                curr_list.append(selection_name)

    def get_total_pad(self):
        """
        get the total alpha/pad of tallies of all contests
        :return: a dictionary of alpha/pad of tallies of all contests
        """
        if len(self.total_pad_dic.keys()) == 0:
            self.__fill_total_pad_data()

        return self.total_pad_dic

    def get_total_data(self):
        """
        get the total beta/data of tallies of all contests
        :return: a dictionary of beta/data of tallies of all contests
        """
        if len(self.total_data_dic.keys()) == 0:
            self.__fill_total_pad_data()

        return self.total_data_dic
