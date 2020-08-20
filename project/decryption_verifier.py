from project.contest_verifier import TallyContestVerifier
from project.interfaces import IVerifier
from project.generator import ParameterGenerator


class TallyDecryptionVerifier(IVerifier):
    """
    This class is responsible for box 6, tally decryption, where the verifier will check the total
    tally of ballot selections matches the actual selections
    """
    def __init__(self, tally_dic: dict, param_g: ParameterGenerator):
        super().__init__(param_g)
        self.tally_dic = tally_dic
        self.contests = self.tally_dic.get('contests')
        self.spoiled_ballots = self.tally_dic.get('spoiled_ballots')

    def verify_cast_ballot_tallies(self) -> bool:
        """

        :return:
        """
        tally_name = self.tally_dic.get('object_id')
        contest_names = list(self.contests.keys())
        return self.__make_all_contest_verification(self.contests, contest_names, tally_name)

    def verify_a_spoiled_ballot(self, ballot_name: str) -> bool:
        """

        :param ballot_name:
        :return:
        """
        spoiled_ballot = self.spoiled_ballots.get(ballot_name)
        contest_names = list(spoiled_ballot.keys())
        return self.__make_all_contest_verification(spoiled_ballot, contest_names, ballot_name)

    def verify_all_spoiled_ballots(self) -> bool:
        """

        :return:
        """
        error = self.initiate_error()

        spoiled_ballot_names = list(self.spoiled_ballots.keys())
        for spoiled_ballot_name in spoiled_ballot_names:
            if not self.verify_a_spoiled_ballot(spoiled_ballot_name):
                error = self.set_error()

        output = "Spoiled ballot decryption"
        if error:
            output += " failure. "
        else:
            output += " success"

        return not error

    def __make_all_contest_verification(self, contest_dic: dict, contest_names: list, tally_name: str) -> bool:
        """
        helper function
        :param contest_dic:
        :param contest_names:
        :param tally_name:
        :return:
        """
        error = self.initiate_error()
        for contest_name in contest_names:
            contest = contest_dic.get(contest_name)
            tcv = TallyContestVerifier(contest, self.param_g)
            if not tcv.verify_a_contest():
                error = self.set_error()

        output = tally_name + ' decryption verification '
        if error:
            output += 'failure. '
        else:
            output += 'success. '
        print(output)

        return not error
