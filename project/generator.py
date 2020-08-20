from project.json_parser import read_json_file


class FilePathGenerator:

    def __init__(self, root_folder_path='/Users/rainbowhuang/Desktop/ElectionGuard/data_08132020/',
                 num_of_guardians=5, threshold=3):
        """
        generate a file name generator with parameters from the json files
        :param num_of_guardians: number of guardians, set default to 5
        :param threshold: quorum, the minimum number of members that must be present, set default to 3
        """
        #TODO: change to relative paths when push to git
        self.DATA_FOLDER_PATH = root_folder_path
        self.FILE_TYPE_SUFFIX = '.json'
        self.FOLDER_SUFFIX = '/'

        # class variables
        self.num_of_guardians = num_of_guardians
        self.threshold = threshold

    def get_guardian_coefficient_file_path(self, index: int) -> str:
        """
        generate a coefficient file path given the guardian's index
        :param index: index of a guardian, (0 - number of guardians)
        :return: a string of the coefficient
        """
        coeff_file_path = '/coefficients/coefficient_validation_set_hamilton-county-' \
                                                       'canvass-board-member-'

        return self.DATA_FOLDER_PATH + coeff_file_path + str(index) + self.FILE_TYPE_SUFFIX

    def get_context_file_path(self) -> str:
        """

        :return:
        """
        return self.DATA_FOLDER_PATH + 'context' + self.FILE_TYPE_SUFFIX

    def get_constants_file_path(self) -> str:
        """

        :return:
        """
        return self.DATA_FOLDER_PATH + 'constants' + self.FILE_TYPE_SUFFIX

    def get_tally_file_path(self) -> str:
        """

        :return:
        """
        return self.DATA_FOLDER_PATH + 'tally' + self.FILE_TYPE_SUFFIX

    def get_description_file_path(self) -> str:
        """

        :return:
        """
        return self.DATA_FOLDER_PATH + 'description' + self.FILE_TYPE_SUFFIX

    def get_encrypted_ballot_folder_path(self) -> str:
        """

        :return:
        """

        return self.DATA_FOLDER_PATH + 'encrypted_ballots' + self.FOLDER_SUFFIX

    def get_spoiled_ballot_folder_path(self) -> str:
        """

        :return:
        """
        return self.DATA_FOLDER_PATH + '/spoiled_ballots' + self.FILE_TYPE_SUFFIX


class ParameterGenerator:
    def __init__(self, path_g: FilePathGenerator, num_of_guardians=5, quorum=3):
        """

        :type path_g: object
        """
        self.path_g = path_g
        self.num_of_guardians = num_of_guardians
        self.quorum = quorum

    def get_context(self) -> dict:
        """
        get all context as a dictionary
        :return:
        """
        context_path = self.path_g.get_context_file_path()
        return read_json_file(context_path)

    def get_constants(self) -> dict:
        """
        get all constants as a dictionary
        :return:
        """
        constants_path = self.path_g.get_constants_file_path()
        return read_json_file(constants_path)

    def get_generator(self) -> int:
        """
        get generator, set default name to be generator
        :return:
        """
        return int(self.get_constants().get('generator'))

    def get_large_prime(self) -> int:
        """
        get large prime p
        :return:
        """
        return int(self.get_constants().get('large_prime'))

    def get_small_prime(self) -> int:
        """
        get large prime p
        :return:
        """
        return int(self.get_constants().get('small_prime'))

    def get_cofactor(self) -> int:
        """

        :return:
        """
        return int(self.get_constants().get('cofactor'))

    def get_extended_hash(self) -> int:
        """

        :return:
        """
        return int(self.get_context().get('crypto_extended_base_hash'))

    def get_base_hash(self) -> int:
        """

        :return:
        """
        return int(self.get_context().get('crypto_base_hash'))

    def get_elgamal_key(self) -> int:
        """

        :return:
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
        for i in range(self.num_of_guardians):
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
        return int(self.num_of_guardians)

    def get_quorum(self) -> int:
        """

        :return:
        """
        return int(self.quorum)


class VoteLimitCounter:
    def __init__(self, param_g: ParameterGenerator):
        self.description_dic = param_g.get_description()
        self.contest_vote_limits = {}

    def get_contest_vote_limits(self) -> dict:
        """
        :return:
        """
        # fill in dictionary when it's empty
        if not bool(self.contest_vote_limits):
            self.__fill_contest_vote_limits()

        return self.contest_vote_limits

    def __fill_contest_vote_limits(self):
        """
        fill in the num_max_vote dictionary, key- contest name, value- maximum votes allowed for this contest
        source: description
        :return:
        """

        contests = self.description_dic.get('contests')
        for contest in contests:
            contest_name = contest.get('object_id')
            num_max_vote = contest.get('votes_allowed')
            self.contest_vote_limits[contest_name] = int(num_max_vote)
