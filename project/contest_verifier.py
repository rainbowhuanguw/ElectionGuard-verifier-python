from project import number, hash, constants
from project.selection_verifier import BallotSelectionVerifier

class ContestVerifier:

    def __init__(self, contest_dic: dict, param_dic: dict):
        pass

    def verify_a_contest(self):
        pass

class BallotContestVerifier:

    def __init__(self, contest_dic: dict, generator: int, public_key: int, extended_hash: int, vote_limits: dict):
        # dictionaries
        self.contest_dic = contest_dic
        self.generator = generator
        self.public_key = public_key
        self.extended_hash = extended_hash
        self.vote_limit_dic = vote_limits

        # contest info
        self.contest_alpha = int(contest_dic.get('proof', {}).get('pad'))
        self.contest_beta = int(contest_dic.get('proof', {}).get('data'))
        self.contest_response = int(self.contest_dic.get('proof', {}).get('response'))
        self.contest_challenge = int(self.contest_dic.get('proof', {}).get('challenge'))
        self.contest_id = self.contest_dic.get('object_id')

    def verify_a_contest(self) -> bool:
        """
        verify a contest within a ballot, ballot correctness
        :return
        """
        # initialize errors to false
        encryption_error, limit_error = False, False
        # get variables
        selections_list = self.contest_dic.get('ballot_selections')
        vote_limit = int(self.vote_limit_dic.get(self.contest_id))

        placeholder_count = 0
        selection_alpha_product = 1
        selection_beta_product = 1

        for selection in selections_list:
            # verify encryption correctness on every selection  - selection check
            # create selection verifiers
            sv = BallotSelectionVerifier(selection, self.generator, self.public_key, self.extended_hash)

            # check validity of a selection
            is_correct = sv.verify_selection_validity()
            if not is_correct:
                encryption_error = True

            # check selection limit, whether each a and b are in zrp
            is_within_limit = sv.verify_selection_limit()
            if not is_within_limit:
                limit_error = True

            # get alpha, beta products
            selection_alpha_product, selection_beta_product = self.__get_product(sv,
                                                                                 selection_alpha_product,
                                                                                 selection_beta_product)
            # get placeholder counts
            if sv.is_placeholder_selection():
                placeholder_count = self.__increment_count(placeholder_count)

        print(selection_alpha_product)
        print(self.contest_alpha)

        print(selection_beta_product)
        print(self.contest_beta)

        # verify the placeholder numbers match the maximum votes allowed - contest check
        placeholder_match = self.__match_vote_limit_by_contest(self.contest_id, placeholder_count)
        if not placeholder_match:
            limit_error = True

        # check whether selection alpha, beta products equal to contest alpha and beta - contest check
        product_match = self.__check_product(selection_alpha_product, selection_beta_product)
        if not product_match:
            limit_error = True

        # check if given contest challenge matches the computation
        challenge_match = self.__check_challenge(selection_beta_product, selection_beta_product)
        if not challenge_match:
            limit_error = True

        # check equations
        equ1_check = self.__check_equation1(selection_alpha_product)
        equ2_check = self.__check_equation2(selection_beta_product, vote_limit)

        if not equ1_check or not equ2_check:
            limit_error = True

        if encryption_error or limit_error:
            output = self.contest_id + ' verification failure:'
            if encryption_error:
                output += ' encryption error. '
            if limit_error:
                output += ' selection limit error. '
            print(output)

        return not encryption_error and not limit_error

    def __check_product(self, alpha_product: int, beta_product: int) -> bool:
        """
        check if the given alpha(pad) and beta(data) in each contest equal to the accumulative product of alphas
        and betas from each selection within this contest
        :param contest_dic:
        :param alpha_product:
        :param beta_product:
        :return:
        """
        a_res = number.equals(self.contest_alpha, alpha_product)
        b_res = number.equals(self.contest_beta, beta_product)

        if not a_res:
            print("Contest alpha/pad value error. ")

        if not b_res:
            print("Contest beta/data value error. ")

        return a_res and b_res

    def __check_response(self) -> bool:
        """

        :param contest_dic:
        :return:
        """
        res = number.is_within_set_zq(self.contest_response)
        if not res:
            print("Contest response error. ")
        return res

    def __check_challenge(self, alpha_product: int, beta_product: int) -> bool:
        """

        :param alpha_product:
        :param beta_product:
        :return:
        """
        challenge_computed = hash.hash_elems(self.extended_hash, self.contest_alpha, self.contest_beta,
                                             alpha_product, beta_product)

        res = number.equals(self.contest_challenge, challenge_computed)

        if not res:
            print("Contest challenge error. ")

        return res

    def __check_equation1(self, alpha_product: int) -> bool:
        """
        check g ^ v = a * A ^ c mod p
        :return:
        """
        left = pow(self.generator, self.contest_response, constants.LARGE_PRIME)
        right = number.mod(number.mod(self.contest_alpha, constants.LARGE_PRIME)
                           * pow(alpha_product, self.contest_challenge, constants.LARGE_PRIME),
                           constants.LARGE_PRIME)

        res = number.equals(left, right)
        if not res:
            print("Contest selection limit check equation 1 error. ")

        return res

    def __check_equation2(self, beta_product: int,  votes_allowed: int):
        """
        g ^ L * K ^ v = b * B ^ C mod p
        :param beta_product:
        :return:
        """
        left = number.mod(pow(self.generator, votes_allowed, constants.LARGE_PRIME) * \
               pow(self.public_key, self.contest_response, constants.LARGE_PRIME), constants.LARGE_PRIME)

        right = number.mod(self.contest_beta * pow(beta_product, self.contest_challenge, constants.LARGE_PRIME),
                           constants.LARGE_PRIME)

        res = number.equals(left, right)
        if not res:
            print("Contest selection limit check equation 2 error. ")

    def __get_product(self, sv: BallotSelectionVerifier, alpha_product: int, beta_product: int) -> tuple:
        """
        get alpha and beta from a selection and return the accumulative product
        :param selection_dic:
        :param alpha_product:
        :param beta_product:
        :return:
        """

        return (alpha_product * sv.get_pad_data()[0] % constants.LARGE_PRIME,
                beta_product * sv.get_pad_data()[1] % constants.LARGE_PRIME)

    def __match_vote_limit_by_contest(self, contest_name: str, num_of_placeholders: int) -> bool:
        """
        match the placeholder numbers in each contest with the maximum
        :param vote_limits_dic
        :param contest_name
        :param num_of_placeholders
        :return:
        """
        vote_limit = int(self.vote_limit_dic.get(contest_name))

        res = number.equals(vote_limit, num_of_placeholders)
        if not res:
            print("contest placeholder number error. ")

        return res

    def __increment_count(self, count: int) -> int:
        """
        increment the number of placeholder by 1
        :param count:
        :return:
        """
        return count + 1


# TODO:
class TallyContestVerifier:
    def __init__(self, contest_dic: dict):
        self.contest_dic = contest_dic
        self.selection_names = list(self.contest_dic.get('selections').keys())

    def verify_a_contest(self):
        pass


