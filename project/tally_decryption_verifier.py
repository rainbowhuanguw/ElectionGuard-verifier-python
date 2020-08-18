from project import number, hash, constants


class TallyDecryptionVerifier:
    """
    This class is responsible for box 6, tally decryption, where the verifier will check the total
    tally of ballot selections matches the actual selections
    """
    def __init__(self, tally_dic: dict):
        self.tally_dic = tally_dic
        self.contest_names = list(self.tally_dic.get('contests', {}).keys())


    def verify_all_tallies(self):
        pass

    def verify_one_tally(self):
        """

        :return:
        """
        pass






