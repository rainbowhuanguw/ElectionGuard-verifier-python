class FilePathGenerator:

    def __init__(self, num_of_guardians=5, threshold=3, num_of_ballots=100, num_of_spoiled_ballots=8):
        """
        generate a file name generator with parameters from the json files
        :param num_of_guardians: number of guardians, set default to 5
        :param threshold: quorum, the minimum number of members that must be present, set default to 3
        :param num_of_ballots: number of ballot files, set default to 100
        :param num_of_spoiled_ballots: number of spoiled ballot files, set default to 8
        """
        #TODO: change to relative paths when push to git
        self.DATA_FOLDER_PATH = '/Users/rainbowhuang/Desktop/ElectionGuard/data_08132020'
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