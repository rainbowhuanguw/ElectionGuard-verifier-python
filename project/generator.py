from project.json_parser import read_json_file


class FilePathGenerator:

    def __init__(self, root_folder_path='/Users/rainbowhuang/Desktop/ElectionGuard/data_08132020',
                 num_of_guardians=5, threshold=3, num_of_ballots=100, num_of_spoiled_ballots=8):
        """
        generate a file name generator with parameters from the json files
        :param num_of_guardians: number of guardians, set default to 5
        :param threshold: quorum, the minimum number of members that must be present, set default to 3
        :param num_of_ballots: number of ballot files, set default to 100
        :param num_of_spoiled_ballots: number of spoiled ballot files, set default to 8
        """
        #TODO: change to relative paths when push to git
        self.DATA_FOLDER_PATH = root_folder_path
        self.FILE_TYPE_SUFFIX = '.json'

        # class variables
        self.num_of_guardians = num_of_guardians
        self.threshold = threshold
        self.num_of_ballots = num_of_ballots
        self.num_of_spoiled_ballots = num_of_spoiled_ballots

    def get_guardian_coefficient_file_path(self, index: int) -> str:
        """
        generate a coefficient file path given the guardian's index
        :param index: index of a guardian, (0 - number of guardians)
        :return: a string of the coefficient
        """
        coeff_file_path = self.DATA_FOLDER_PATH + '/coefficients/coefficient_validation_set_hamilton-county-' \
                                                       'canvass-board-member-'
        if index >= self.num_of_guardians or index < 0:
            raise IndexError("index out of bound")

        return self.DATA_FOLDER_PATH + coeff_file_path + str(index) + self.FILE_TYPE_SUFFIX

    def get_context_file_path(self) -> str:
        """

        :return:
        """
        return self.DATA_FOLDER_PATH + '/context' + self.FILE_TYPE_SUFFIX

    def get_constants_file_path(self) -> str:
        """

        :return:
        """
        return self.DATA_FOLDER_PATH + '/constants' + self.FILE_TYPE_SUFFIX

    def get_tally_file_path(self) -> str:
        """

        :return:
        """
        return self.DATA_FOLDER_PATH + '/tally' + self.FILE_TYPE_SUFFIX

    def get_description_file_path(self) -> str:
        """

        :return:
        """
        return self.DATA_FOLDER_PATH + '/description' + self.FILE_TYPE_SUFFIX

    def get_encrypted_ballot_folder_path(self) -> str:
        """

        :return:
        """

        return self.DATA_FOLDER_PATH + '/encrypted_ballots'

    def get_spoiled_ballot_folder_path(self) -> str:
        """

        :return:
        """
        return self.DATA_FOLDER_PATH + '/spoiled_ballots'


class ParameterGenerator:
    def __init__(self, num_of_guardians=5, threshold=3, num_of_ballots=100, num_of_spoiled_ballots=8):
        self.__filename_generator = FilePathGenerator()
        self.num_of_guardians = num_of_guardians
        self.threshold = threshold
        self.num_of_ballots = num_of_ballots
        self.num_of_spoiled_ballots = num_of_spoiled_ballots

    def get_context(self) -> dict:
        """
        get all context as a dictionary
        :return:
        """
        context_path = self.__filename_generator.get_context_file_path()
        return read_json_file(context_path)

    def get_constants(self) -> dict:
        """
        get all constants as a dictionary
        :return:
        """
        constants_path = self.__filename_generator.get_constants_file_path()
        return read_json_file(constants_path)

    def get_generator(self, generator_name='generator') -> int:
        """
        get generator, set default name to be generator
        :param generator_name:
        :return:
        """
        return int(self.get_constants().get(generator_name))

    def get_large_prime(self, prime_name='large_prime') -> int:
        """
        get large prime p
        :param prime_name:
        :return:
        """
        return int(self.get_constants().get(prime_name))

    def get_small_prime(self, prime_name='small_prime') -> int:
        """
        get large prime p
        :param prime_name:
        :return:
        """
        return int(self.get_constants().get(prime_name))

    def get_extended_hash(self, hash_name='crypto_extended_base_hash') -> int:
        """

        :param hash_name:
        :return:
        """
        return int(self.get_context().get(hash_name))

    def get_base_hash(self, hash_name='crypto_base_hash') -> int:
        """

        :param hash_name:
        :return:
        """
        return int(self.get_context().get(hash_name))

    def get_elgamal_key(self, key_name='elgamal_public_key') -> int:
        """

        :param key_name:
        :return:
        """
        return int(self.get_context().get(key_name))

    def get_public_key_of_a_guardian(self, index: int) -> int:
        """

        :param index:
        :return:
        """
        file_path = self.__filename_generator.get_guardian_coefficient_file_path(index)
        coefficients = read_json_file(file_path)
        return coefficients.get('coefficient_commitments')[0]

    def get_public_keys_of_all_guardians(self) -> list:
        """

        :return:
        """
        for i in range(self.num_of_guardians):
            yield self.get_public_key_of_a_guardian(i)