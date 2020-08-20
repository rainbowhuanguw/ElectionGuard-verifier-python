from project.contest_verifier import TallyContestVerifier


class IDecryptionVerifier:
    def verify_all_contests(self) -> bool:
        pass


class TallyDecryptionVerifier(IDecryptionVerifier):
    """
    This class is responsible for box 6, tally decryption, where the verifier will check the total
    tally of ballot selections matches the actual selections
    """
    def __init__(self, tally_dic: dict, generator: int, extended_hash: int, public_keys: list):
        self.__tally_dic = tally_dic
        self.__generator = generator
        self.__extended_hash = extended_hash
        self.__public_keys = public_keys
        self.__contests = self.__tally_dic.get('contests')
        self.__spoiled_ballots = self.__tally_dic.get('spoiled_ballots')

    def verify_cast_ballot_tallies(self) -> bool:
        """

        :return:
        """
        tally_name = self.__tally_dic.get('object_id')
        contest_names = list(self.__contests.keys())
        return self.__make_all_contest_verification(self.__contests, contest_names, tally_name)


    def verify_a_spoiled_ballot(self, ballot_name: str) -> bool:
        """

        :param ballot_name:
        :return:
        """
        spoiled_ballot = self.__spoiled_ballots.get(ballot_name)
        contest_names = list(spoiled_ballot.keys())
        return self.__make_all_contest_verification(spoiled_ballot, contest_names, ballot_name)

    def verify_all_spoiled_ballots(self) -> bool:
        """

        :return:
        """
        error = False

        spoiled_ballot_names = list(self.__spoiled_ballots.keys())
        for spoiled_ballot_name in spoiled_ballot_names:
            if not self.verify_a_spoiled_ballot(spoiled_ballot_name):
                error = True

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
        error = False
        for contest_name in contest_names:
            contest = contest_dic.get(contest_name)
            tcv = TallyContestVerifier(contest, self.__generator, self.__extended_hash, self.__public_keys)
            if not tcv.verify_a_contest():
                error = True

        output = tally_name + ' decryption verification '
        if error:
            output += 'failure. '
        else:
            output += 'success. '
        print(output)

        return not error









