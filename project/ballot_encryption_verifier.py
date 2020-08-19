from project import json_parser
from project.contest_verifier import BallotContestVerifier
from project.vote_limit_counter import VoteLimitCounter


class BallotEncryptionVerifier:
    """
    This class checks ballot correctness on each ballot. Ballot correctness can be represented by:
    1. correct encryption (of value 0 or 1) of each selection within each contest (box 3)
    2. selection limits are satisfied for each contest (box 4)
    """

    def __init__(self, ballot_dic: dict, generator, public_key, extended_hash, vote_limit_dic):
        #kwargs: generator, public_key, __extended_hash, vote_limit_dic
        """"""
        self.ballot_dic = ballot_dic
        self.generator = generator
        self.public_key = public_key
        self.extended_hash = extended_hash
        self.vote_limit_dic = vote_limit_dic

    def verify_all_contests(self) -> bool:
        """
        verify all the contests within a ballot
        :return: True if all contests checked out/no error, False if any error in any selection
        """
        error = False

        ballot_id = self.ballot_dic.get('object_id')
        contests = self.ballot_dic.get('contests')

        for contest in contests:
            cv = BallotContestVerifier(contest, generator=self.generator, public_key=self.public_key,
                                       extended_hash=self.extended_hash, vote_limit_dic=self.vote_limit_dic)
            res = cv.verify_a_contest()
            if not res:
                error = True

        if not error:
            print(ballot_id + ' ballot correctness verification success.')
        else:
            print(ballot_id + ' ballot correctness verification failure.')

        return not error

