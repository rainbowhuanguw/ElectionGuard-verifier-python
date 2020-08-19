from project.contest_verifier import TallyContestVerifier


class TallyDecryptionVerifier:
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
        self.__contest_names = list(self.__contests.keys())
        self.__tally_id = self.__tally_dic.get('object_id')

    def verify_all_contests(self) -> bool:
        error = False
        for contest_name in self.__contest_names:
            contest = self.__contest_names.get(contest_name)
            tcv = TallyContestVerifier(contest, self.__generator, self.__extended_hash, self.__public_keys)
            if not tcv.verify_a_contest():
                error = True

        if not error:
            print(self.__tally_id + ' tally decryption verification failure. ')

        return not error







