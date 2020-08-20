from project import json_parser
from .contest_verifier import BallotContestVerifier
from .generator import ParameterGenerator, VoteLimitCounter
from .interfaces import IVerifier
import glob


class AllBallotsVerifier(IVerifier):
    def __init__(self, folder_path: str, param_g: ParameterGenerator, limit_counter: VoteLimitCounter):
        super().__init__(param_g)
        self.folder_path = folder_path
        self.__limit_counter = limit_counter

    def verify_all_ballots(self) -> bool:
        error = False
        count = 0
        for ballot_file in glob.glob(self.folder_path + '*.json'):
            ballot_dic = json_parser.read_json_file(ballot_file)
            bvv = BallotEncryptionVerifier(ballot_dic, self.param_g, self.__limit_counter)
            res = bvv.verify_all_contests()
            if not res:
                error = True
                count += 1

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
        error = False

        ballot_id = self.ballot_dic.get('object_id')
        contests = self.ballot_dic.get('contests')

        for contest in contests:
            cv = BallotContestVerifier(contest, self.param_g, self.__limit_counter)
            res = cv.verify_a_contest()
            if not res:
                error = True

        if not error:
            print(ballot_id + ' ballot correctness verification success.')
        else:
            print(ballot_id + ' ballot correctness verification failure.')

        return not error

