from project.json_parser import read_json_file


class FilePathGenerator:
    """
    This class is responsible for navigating to different data files in the given dataset folder,
    the root folder path can be changed to where the whole dataset is stored and its inner structure should
    remain unchanged
    """

    def __init__(self, root_folder_path='/Users/rainbowhuang/Desktop/ElectionGuard/data_08132020/',
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
