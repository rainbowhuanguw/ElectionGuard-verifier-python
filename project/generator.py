from project.json_parser import read_json_file
import glob
from project import number
import os


class FilePathGenerator:
    """
    This class is responsible for navigating to different data files in the given dataset folder,
    the root folder path can be changed to where the whole dataset is stored and its inner structure should
    remain unchanged
    """

    def __init__(self, root_folder_path="/Users/rainbowhuang/Desktop/ElectionGuard/data_08132020/",
                 num_of_guardians=5):
        """
        generate a file name generator with parameters from the json files
        :param num_of_guardians: number of guardians, set default to 5 #TODO: how to coordinate?
        """
        # TODO: change to relative paths when push to git
        self.DATA_FOLDER_PATH = root_folder_path
        self.FILE_TYPE_SUFFIX = '.json'
        self.FOLDER_SUFFIX = '/'

        # class variables
        self.num_of_guardians = num_of_guardians

    def get_guardian_coefficient_file_path(self, index: int) -> str:
        """
        generate a coefficient file path given the guardian's index
        :param index: index of a guardian, (0 - number of guardians)
        :return: a string of the coefficient
        """
        coeff_file_path = '/coefficients/coefficient_validation_' \
                          'set_hamilton-county-canvass-board-member-'

        return self.DATA_FOLDER_PATH + coeff_file_path + str(index) + self.FILE_TYPE_SUFFIX

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

    def get_device_folder_path(self) -> str:
        """
        get a path to the devices folder
        :return:
        """
        return self.DATA_FOLDER_PATH + '/devices' + self.FILE_TYPE_SUFFIX

class ParameterGenerator:
    """
    This class should be responsible for accessing parameters stored in dataset files
    with the help of the file path file generator to locate the files. Parameters in this
    case only include those that are higher than ballot-level. Those that are directly related
    to each specific ballot, contest, or selection will be taken care of by each level of verifiers.
    """
    def __init__(self, path_g: FilePathGenerator):
        """
        initializer
        :param path_g: FilePathGenerator that helps to get the paths of files
        """
        self.path_g = path_g

    def get_context(self) -> dict:
        """
        get all context information as a dictionary
        :return: a dictionary of context info
        """
        context_path = self.path_g.get_context_file_path()
        return read_json_file(context_path)

    def get_constants(self) -> dict:
        """
        get all constants as a dictionary
        :return: a dictionary of constants info
        """
        constants_path = self.path_g.get_constants_file_path()
        return read_json_file(constants_path)

    def get_generator(self) -> int:
        """
        get generator, set default name to be generator
        :return: generator 'g' in integer
        """
        return int(self.get_constants().get('generator'))

    def get_large_prime(self) -> int:
        """
        get large prime p
        :return: large prime 'p' in integer
        """
        return int(self.get_constants().get('large_prime'))

    def get_small_prime(self) -> int:
        """
        get small prime q
        :return: small prime 'q' in integer
        """
        return int(self.get_constants().get('small_prime'))

    def get_cofactor(self) -> int:
        """
        get cofactor r
        :return: cofactor 'r' in integer
        """
        return int(self.get_constants().get('cofactor'))

    def get_extended_hash(self) -> int:
        """
        get extended base hash Q-bar
        :return: extended base hash Q-bar in integer
        """
        return int(self.get_context().get('crypto_extended_base_hash'))

    def get_base_hash(self) -> int:
        """
        get extended base hash Q
        :return: base hash Q in integer
        """
        return int(self.get_context().get('crypto_base_hash'))

    def get_elgamal_key(self) -> int:
        """
        get Elgamal key K
        :return: Elgamal key K in integer
        """
        return int(self.get_context().get('elgamal_public_key'))

    def get_public_key_of_a_guardian(self, index: int) -> int:
        """

        :param index:
        :return:
        """
        file_path = self.path_g.get_guardian_coefficient_file_path(index)
        coefficients = read_json_file(file_path)
        return int(coefficients.get('coefficient_commitments')[0])

    def get_public_keys_of_all_guardians(self) -> list:
        """

        :return:
        """
        num_of_guardians = self.get_num_of_guardians()
        for i in range(num_of_guardians):
            yield self.get_public_key_of_a_guardian(i)

    def get_description(self) -> dict:
        """

        :return:
        """
        file_path = self.path_g.get_description_file_path()
        return read_json_file(file_path)

    def get_num_of_guardians(self) -> int:
        """

        :return:
        """
        context_file_path = self.path_g.get_context_file_path()
        context = read_json_file(context_file_path)
        return int(context.get('number_of_guardians'))

    def get_quorum(self) -> int:
        """

        :return:
        """
        context_file_path = self.path_g.get_context_file_path()
        context = read_json_file(context_file_path)
        return int(context.get('quorum'))

    def get_num_of_ballots(self) -> int:
        """

        :return:
        """
        ballot_folder_path = self.path_g.get_encrypted_ballot_folder_path()
        ballot_files = next(os.walk(ballot_folder_path))[2]
        return len(ballot_files)

    def get_num_of_spoiled_ballots(self) -> int:
        """

        :return:
        """
        spoiled_ballot_folder_path = self.path_g.get_spoiled_ballot_folder_path()
        spoiled_ballot_files = next(os.walk(spoiled_ballot_folder_path))[2]
        return len(spoiled_ballot_files)

    def get_device_id(self) -> str:
        """

        :return:
        """
        device_folder_path = self.path_g.get_device_folder_path()
        for file in glob.glob(device_folder_path + '*json'):
            dic = read_json_file(file)
            return dic.get('uuid')

    def get_location(self) -> str:
        """

        :return:
        """
        device_folder_path = self.path_g.get_device_folder_path()
        for file in glob.glob(device_folder_path + '*json'):
            dic = read_json_file(file)
            return dic.get('location')


class VoteLimitCounter:
    def __init__(self, param_g: ParameterGenerator):
        self.description_dic = param_g.get_description()
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
    # TODO:
    def __init__(self, path_g: FilePathGenerator, param_g: ParameterGenerator):
        self.param_g = param_g
        self.path_g = path_g
        self.order_names_dic = {}   # a dictionary to store the contest names and its sequence
        self.names_order_dic = {}
        self.contest_selection_names = {}  # a dictionary to store the contest names and its selection names
        self.dics_by_contest = []   # a list to store all the dics, length = 2 * contest_names
        self.total_pad_dic = {}
        self.total_data_dic = {}

    def get_dics(self):
        """

        :return:
        """
        if len(self.dics_by_contest) == 0:
            self.__create_inner_dic()
            self.__fill_in_dics()
        return self.dics_by_contest

    def get_dic_id_by_contest_name(self, contest_name: str, type: str) -> int:
        """
        get the corresponding dataframe id in the dfs list by the name of contest
        :param contest_name:
        :param type:
        :return:
        """
        if type == 'a':
            return 2 * self.order_names_dic[contest_name]
        elif type == 'b':
            return 2 * self.order_names_dic[contest_name] + 1

    def __create_inner_dic(self):
        """
        create 2 * contest names number of dicts. Two for each contest, one for storing pad values,
        one for storing data values. Fill in column names with selections in that specific contest
        :return:
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
        alternative way of getting the data
        loop over the folder that stores all encrypted ballots, go through every ballot to get the selection
        pad and data
        :return:
        """
        # get to the folder
        ballot_folder_path = self.path_g.get_encrypted_ballot_folder_path()

        # loop over every ballot file
        for ballot_file in glob.glob(ballot_folder_path + '*json'):
            ballot = read_json_file(ballot_file)
            ballot_name = ballot.get('object_id')
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
        get the accumulative product of pad and data for all the selections
        :param dic:
        :param selection_name:
        :param num:
        :return:
        """
        if dic.get(selection_name) == '':
            dic[selection_name] = str(num)
        else:
            temp = int(dic[selection_name])
            product = number.mod_p(temp * num)
            dic[selection_name] = str(product)

    def __fill_total_pad_data(self):
        """
        read pad and data of each non dummy selections in all contests
        :return:
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
        description_dic = self.param_g.get_description()
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
        if len(self.total_pad_dic.keys()) == 0:
            self.__fill_total_pad_data()

        return self.total_pad_dic

    def get_total_data(self):
        if len(self.total_data_dic.keys()) == 0:
            self.__fill_total_pad_data()

        return self.total_data_dic






