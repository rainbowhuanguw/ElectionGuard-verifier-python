from project import number, hash, constants
from project.selection_verifier import BallotSelectionVerifier


class IContestVerifier:
    """
    Contest verifier as an interface
    """

    def verify_a_contest(self):
        pass


class BallotContestVerifier(IContestVerifier):
    """
    This class is responsible for checking individual ballot encryption and selection limit
    """
    def __init__(self, contest_dic: dict, generator: int, extended_hash: int, public_key: int, vote_limit_dic: dict):

        self.__generator = generator
        self.__extended_hash = extended_hash
        self.__public_key = public_key
        self.__vote_limit_dic = vote_limit_dic

        # contest info
        self.__contest_dic = contest_dic
        self.__contest_alpha = int(contest_dic.get('proof', {}).get('pad'))
        self.__contest_beta = int(contest_dic.get('proof', {}).get('data'))
        self.__contest_response = int(contest_dic.get('proof', {}).get('response'))
        self.__contest_challenge = int(contest_dic.get('proof', {}).get('challenge'))
        self.__contest_id = contest_dic.get('object_id')

    def verify_a_contest(self) -> bool:
        """
        verify a contest within a ballot, ballot correctness
        :return
        """
        # initialize errors to false
        encryption_error, limit_error = False, False
        # get variables
        selections_list = self.__contest_dic.get('ballot_selections')
        vote_limit = int(self.__vote_limit_dic.get(self.__contest_id))

        placeholder_count = 0
        selection_alpha_product = 1
        selection_beta_product = 1

        for selection in selections_list:
            # verify encryption correctness on every selection  - selection check
            # create selection verifiers
            sv = BallotSelectionVerifier(selection, self.__generator, self.__public_key, self.__extended_hash)

            # get alpha, beta products
            selection_alpha_product = selection_alpha_product * sv.get_pad() % constants.LARGE_PRIME
            selection_beta_product = selection_beta_product * sv.get_data() % constants.LARGE_PRIME

            # check validity of a selection
            is_correct = sv.verify_selection_validity()
            if not is_correct:
                encryption_error = True

            # check selection limit, whether each a and b are in zrp
            is_within_limit = sv.verify_selection_limit()
            if not is_within_limit:
                limit_error = True

            # get placeholder counts
            if sv.is_placeholder_selection():
                placeholder_count = self.__increment_count(placeholder_count)

        # verify the placeholder numbers match the maximum votes allowed - contest check
        placeholder_match = self.__match_vote_limit_by_contest(self.__contest_id, placeholder_count)
        if not placeholder_match:
            limit_error = True

        challenge_computed = hash.hash_elems(self.__extended_hash, selection_alpha_product, selection_beta_product,
                                              self.__contest_alpha, self.__contest_beta)

        # check if given contest challenge matches the computation
        challenge_match = self.__check_challenge(challenge_computed)
        if not challenge_match:
            limit_error = True

        # check equations
        equ1_check = self.__check_equation1(selection_alpha_product)
        equ2_check = self.__check_equation2(selection_beta_product, vote_limit)

        if not equ1_check or not equ2_check:
            limit_error = True

        if encryption_error or limit_error:
            output = self.__contest_id + ' verification failure:'
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
        res = number.is_within_set_zq(self.__contest_response)
        if not res:
            print("Contest response error. ")
        return res

    def __check_challenge(self, challenge_computed) -> bool:
        """

        :param alpha_product:
        :param beta_product:
        :return:
        """
        res = number.equals(challenge_computed, self.__contest_challenge)

        if not res:
            print("Contest challenge error. ")

        return res

    def __check_equation1(self, alpha_product: int) -> bool:
        """
        check g ^ v = a * A ^ c mod p
        :return:
        """
        left = pow(self.__generator, self.__contest_response, constants.LARGE_PRIME)
        right = number.mod(number.mod(self.__contest_alpha, constants.LARGE_PRIME)
                           * pow(alpha_product, self.__contest_challenge, constants.LARGE_PRIME),
                           constants.LARGE_PRIME)

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
        left = number.mod(pow(self.__generator, votes_allowed, constants.LARGE_PRIME) * \
                          pow(self.__public_key, self.__contest_response, constants.LARGE_PRIME),
                          constants.LARGE_PRIME)

        right = number.mod(self.__contest_beta * pow(beta_product, self.__contest_challenge, constants.LARGE_PRIME),
                           constants.LARGE_PRIME)

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
        vote_limit = int(self.__vote_limit_dic.get(contest_name))

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


# TODO:
class TallyContestVerifier(IContestVerifier):
    def __init__(self, contest_dic: dict, param_dic: dict):
        self.contest_dic = contest_dic
        self.selection_names = list(self.contest_dic.get('selections').keys())

    def verify_a_contest(self):
        pass
