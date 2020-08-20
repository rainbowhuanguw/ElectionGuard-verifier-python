from project import number
from project.selection_verifier import BallotSelectionVerifier, TallySelectionVerifier
from project.generator import ParameterGenerator, VoteLimitCounter
from project.interfaces import IVerifier, IContestVerifier


class BallotContestVerifier(IVerifier, IContestVerifier):
    """
    This class is responsible for checking individual ballot encryption and selection limit
    """

    def __init__(self, contest_dic: dict, param_g: ParameterGenerator, limit_counter: VoteLimitCounter):
        super().__init__(param_g)
        self.limit_counter = limit_counter
        self.vote_limit_dic = limit_counter.get_contest_vote_limits()

        # contest info
        self.contest_dic = contest_dic
        self.contest_alpha = int(contest_dic.get('proof', {}).get('pad'))
        self.contest_beta = int(contest_dic.get('proof', {}).get('data'))
        self.contest_response = int(contest_dic.get('proof', {}).get('response'))
        self.contest_challenge = int(contest_dic.get('proof', {}).get('challenge'))
        self.contest_id = contest_dic.get('object_id')

    def verify_a_contest(self) -> bool:
        """
        verify a contest within a ballot, ballot correctness
        :return
        """
        # initialize errors to false
        encryption_error, limit_error = self.initiate_error(), self.initiate_error()
        # get variables
        selections_list = self.contest_dic.get('ballot_selections')
        vote_limit = int(self.vote_limit_dic.get(self.contest_id))

        placeholder_count = 0
        selection_alpha_product = 1
        selection_beta_product = 1

        for selection in selections_list:
            # verify encryption correctness on every selection  - selection check
            # create selection verifiers
            sv = BallotSelectionVerifier(selection, self.param_g)

            # get alpha, beta products
            selection_alpha_product = selection_alpha_product * sv.get_pad() % self.param_g.get_large_prime()
            selection_beta_product = selection_beta_product * sv.get_data() % self.param_g.get_large_prime()

            # check validity of a selection
            is_correct = sv.verify_selection_validity()
            if not is_correct:
                encryption_error = self.set_error()

            # check selection limit, whether each a and b are in zrp
            is_within_limit = sv.verify_selection_limit()
            if not is_within_limit:
                limit_error = self.set_error()

            # get placeholder counts
            if sv.is_placeholder_selection():
                placeholder_count = self.__increment_count(placeholder_count)

        # verify the placeholder numbers match the maximum votes allowed - contest check
        placeholder_match = self.__match_vote_limit_by_contest(self.contest_id, placeholder_count)
        if not placeholder_match:
            limit_error = self.set_error()

        challenge_computed = number.hash_elems(self.extended_hash, selection_alpha_product, selection_beta_product,
                                               self.contest_alpha, self.contest_beta)

        # check if given contest challenge matches the computation
        challenge_match = self.__check_challenge(challenge_computed)
        if not challenge_match:
            limit_error = self.set_error()

        # check equations
        # TODO: error in equation 2
        equ1_check = self.__check_equation1(selection_alpha_product)
        equ2_check = self.__check_equation2(selection_beta_product, vote_limit)

        if not equ1_check or not equ2_check:
            limit_error = self.set_error()

        if encryption_error or limit_error:
            output = self.contest_id + ' verification failure:'
            if encryption_error:
                output += ' encryption error. '
            if limit_error:
                output += ' selection limit error. '
            print(output)

        return not encryption_error and not limit_error

    def __check_response(self) -> bool:
        """
        :return:
        """
        res = number.is_within_set_zq(self.contest_response)
        if not res:
            print("Contest response error. ")
        return res

    def __check_challenge(self, challenge_computed) -> bool:
        """
        :param challenge_computed
        :return:
        """
        res = number.equals(challenge_computed, self.contest_challenge)

        if not res:
            print("Contest challenge error. ")

        return res

    def __check_equation1(self, alpha_product: int) -> bool:
        """
        check g ^ v = a * A ^ c mod p
        :return:
        """
        left = pow(self.generator, self.contest_response, self.large_prime)
        right = number.mod(number.mod(self.contest_alpha, self.large_prime)
                           * pow(alpha_product, self.contest_challenge, self.large_prime),
                           self.large_prime)

        res = number.equals(left, right)
        if not res:
            print("Contest selection limit check equation 1 error. ")

        return res

    def __check_equation2(self, beta_product: int, votes_allowed: int) -> bool:
        """
        g ^ L * K ^ v = b * B ^ C mod p
        :param beta_product:
        :return:
        """
        # TODO: confirm what L is, use contest constant * challenge or vote limit
        contest_constant = self.contest_dic.get('proof', {}).get('constant')
        left = number.mod(pow(self.generator, contest_constant * self.contest_challenge, self.large_prime) *
                          pow(self.public_key, self.contest_response, self.large_prime),
                          self.large_prime)
        #left = number.mod(pow(self.generator, votes_allowed, self.large_prime) *
        #                  pow(self.public_key, self.contest_response, self.large_prime),
        #                  self.large_prime)

        right = number.mod(self.contest_beta * pow(beta_product, self.contest_challenge, self.large_prime),
                           self.large_prime)

        res = number.equals(left, right)
        if not res:
            print("Contest selection limit check equation 2 error. ")

        return res

    def __match_vote_limit_by_contest(self, contest_name: str, num_of_placeholders: int) -> bool:
        """
        match the placeholder numbers in each contest with the maximum
        :param contest_name
        :param num_of_placeholders
        :return:
        """
        vote_limit = int(self.vote_limit_dic.get(contest_name))

        res = number.equals(vote_limit, num_of_placeholders)
        if not res:
            print("contest placeholder number error. ")

        return res

    @staticmethod
    def __increment_count(count: int) -> int:
        """
        increment the number of placeholder by 1
        :param count:
        :return:
        """
        return count + 1


class TallyContestVerifier(IVerifier, IContestVerifier):

    def __init__(self, contest_dic: dict, param_g: ParameterGenerator):
        super().__init__(param_g)
        self.contest_dic = contest_dic
        self.public_keys = param_g.get_public_keys_of_all_guardians()
        self.selections = self.contest_dic.get('selections')
        self.selection_names = list(self.selections.keys())
        self.contest_id = self.contest_dic.get('object_id')

    def verify_a_contest(self) -> bool:
        """

        :return:
        """
        error = self.initiate_error()
        for selection_name in self.selection_names:
            selection = self.selections.get(selection_name)
            tsv = TallySelectionVerifier(selection, self.param_g)
            if not tsv.verify_a_selection():
                error = self.set_error()

        if error:
            print(self.contest_id + ' tally decryption failure. ')

        return not error
