from project import json_parser
from .contest_verifier import BallotContestVerifier
from .generator import ParameterGenerator, FilePathGenerator, VoteLimitCounter
from .interfaces import IVerifier
import glob


class AllBallotsVerifier(IVerifier):
    def __init__(self, param_g: ParameterGenerator, path_g: FilePathGenerator, limit_counter: VoteLimitCounter):
        super().__init__(param_g)
        self.path_g = path_g
        self.folder_path = path_g.get_encrypted_ballot_folder_path()
        self.limit_counter = limit_counter

    def verify_all_ballots(self) -> bool:
        error = self.initiate_error()
        count = 0
        for ballot_file in glob.glob(self.folder_path + '*.json'):
            ballot_dic = json_parser.read_json_file(ballot_file)
            bvv = BallotEncryptionVerifier(ballot_dic, self.param_g, self.limit_counter)
            res = bvv.verify_all_contests()
            if not res:
                error = self.set_error()
                count += 1

        if error:
            print("failure. ")
        else:
            print("All {i} ballot verification success. ".format(i=count))

        return not error


class BallotEncryptionVerifier(IVerifier):
    """
    This class checks ballot correctness on each ballot. Ballot correctness can be represented by:
    1. correct encryption (of value 0 or 1) of each selection within each contest (box 3)
    2. selection limits are satisfied for each contest (box 4)
    """

    def __init__(self, ballot_dic: dict, param_g: ParameterGenerator, limit_counter: VoteLimitCounter):
        """"""
        super().__init__(param_g)
        self.ballot_dic = ballot_dic
        self.__limit_counter = limit_counter

    def verify_all_contests(self) -> bool:
        """
        verify all the contests within a ballot
        :return: True if all contests checked out/no error, False if any error in any selection
        """
        error = self.initiate_error()

        ballot_id = self.ballot_dic.get('object_id')
        contests = self.ballot_dic.get('contests')

        for contest in contests:
            cv = BallotContestVerifier(contest, self.param_g, self.__limit_counter)
            res = cv.verify_a_contest()
            if not res:
                error = self.set_error()

        if not error:
            print(ballot_id + ' ballot correctness verification success.')
        else:
            print(ballot_id + ' ballot correctness verification failure.')

        return not error
