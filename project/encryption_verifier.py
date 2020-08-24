from typing import Tuple

from project import json_parser, number
from .generator import ParameterGenerator, FilePathGenerator, VoteLimitCounter
from .interfaces import IBallotVerifier, IContestVerifier, ISelectionVerifier
import glob


class AllBallotsVerifier(IBallotVerifier):
    """
    This class checks ballot correctness on all the ballots, both spoiled and cast.
    """

    def __init__(self, param_g: ParameterGenerator, path_g: FilePathGenerator, limit_counter: VoteLimitCounter):
        super().__init__(param_g, limit_counter)
        self.path_g = path_g
        self.folder_path = path_g.get_encrypted_ballot_folder_path()

    def verify_all_ballots(self) -> bool:
        """
        runs through the folder that contains ballot files once, runs encryption verification on every ballot
        :return: True there is no error, False otherwise
        """
        error = self.initialize_error()
        count = 0
        for ballot_file in glob.glob(self.folder_path + '*.json'):
            ballot_dic = json_parser.read_json_file(ballot_file)
            bvv = BallotEncryptionVerifier(ballot_dic, self.param_g, self.limit_counter)
            res = bvv.verify_all_contests()
            if not res:
                error = self.set_error()
                count += 1

        if error:
            print("Ballot verification failure, {num} ballots didn't pass check. ".format(num=count))
        else:
            print("All {i} ballot verification success. ".format(i=count))

        return not error


class BallotEncryptionVerifier(IBallotVerifier):
    """
    This class checks ballot correctness on a ballot. Ballot correctness can be represented by:
    1. correct encryption (of value 0 or 1) of each selection within each contest (box 3)
    2. selection limits are satisfied for each contest (box 4)
    """

    def __init__(self, ballot_dic: dict, param_g: ParameterGenerator, limit_counter: VoteLimitCounter):
        """"""
        super().__init__(param_g, limit_counter)
        self.ballot_dic = ballot_dic

    def verify_all_contests(self) -> bool:
        """
        verify all the contests within a ballot and check if there are any encryption or limit error
        :return: True if all contests checked out/no error, False if any error in any selection
        """
        encrypt_error, limit_error = self.initialize_error(), self.initialize_error()

        ballot_id = self.ballot_dic.get('object_id')
        contests = self.ballot_dic.get('contests')

        for contest in contests:
            cv = BallotContestVerifier(contest, self.param_g, self.limit_counter)
            encrypt_res, limit_res = cv.verify_a_contest()
            if not encrypt_res:
                encrypt_error = self.set_error()
            if not limit_res:
                limit_error = self.set_error()

        if not encrypt_error and not limit_error:
            print(ballot_id + ' [box 3 & 4] ballot correctness verification success.')
        else:
            if encrypt_error:
                print(ballot_id + ' [box 3] ballot encryption correctness verification failure.')
            if limit_error:
                print(ballot_id + ' [box 4] ballot limit check failure. ')

        return not (encrypt_error and limit_error)


class BallotContestVerifier(IContestVerifier):
    """
    This class is used for checking encryption and selection limit of
    an individual contest within a ballot
    """

    def __init__(self, contest_dic: dict, param_g: ParameterGenerator, limit_counter: VoteLimitCounter):
        super().__init__(param_g)  # calls IVerifier init
        self.limit_counter = limit_counter
        self.vote_limit_dic = limit_counter.get_contest_vote_limits()

        # contest info
        self.contest_dic = contest_dic
        self.contest_alpha = int(contest_dic.get('proof', {}).get('pad'))
        self.contest_beta = int(contest_dic.get('proof', {}).get('data'))
        self.contest_response = int(contest_dic.get('proof', {}).get('response'))
        self.contest_challenge = int(contest_dic.get('proof', {}).get('challenge'))
        self.contest_id = contest_dic.get('object_id')

    def verify_a_contest(self) -> Tuple[bool, bool]:
        """
        verify a contest within a ballot, ballot correctness
        :return True if no error, False otherwise
        """
        # initialize errors to false
        encryption_error, limit_error = self.initialize_error(), self.initialize_error()
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
                placeholder_count = self.__increment_num(placeholder_count)

        # verify the placeholder numbers match the maximum votes allowed - contest check
        placeholder_match = self.__match_vote_limit_by_contest(self.contest_id, placeholder_count)
        if not placeholder_match:
            limit_error = self.set_error()

        # calculate c = H(Q-bar, (A,B), (a,b))
        challenge_computed = number.hash_elems(self.extended_hash, selection_alpha_product, selection_beta_product,
                                               self.contest_alpha, self.contest_beta)

        # check if given contest challenge matches the computation
        challenge_match = self.__check_challenge(challenge_computed)
        if not challenge_match:
            limit_error = self.set_error()

        # check equations
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

        return not encryption_error, not limit_error

    def __check_response(self) -> bool:
        """
        check if the contest response value is within set zq
        :return: True if it's within set zq, False otherwise
        """
        res = number.is_within_set_zq(self.contest_response)
        if not res:
            print("Contest response error. ")
        return res

    def __check_challenge(self, challenge_computed) -> bool:
        """
        check if the given contest response equals to the one computed as c = H(Q-bar, (A,B), (a,b))
        :param challenge_computed: the computed challenge using hash
        :return: True if the given and computed values are the same, False if not
        """
        res = number.equals(challenge_computed, self.contest_challenge)

        if not res:
            print("Contest challenge error. ")

        return res

    # TODO: semantic meaning
    def __check_equation1(self, alpha_product: int) -> bool:
        """
        check if equation g ^ v = a * A ^ c mod p is satisfied
        :return: True if the equation is satisfied, False if not
        """
        left = pow(self.generator, self.contest_response, self.large_prime)
        right = number.mod_p(number.mod_p(self.contest_alpha) *
                             pow(alpha_product, self.contest_challenge, self.large_prime))

        res = number.equals(left, right)
        if not res:
            print("Contest selection limit check equation 1 error. ")

        return res

    # TODO: semantic meaning
    def __check_equation2(self, beta_product: int, votes_allowed: int) -> bool:
        """
        check if equation g ^ (L * c) * K ^ v = b * B ^ C mod p is satisfied
        :param beta_product: the product of beta values of all the selections within this contest
        :param votes_allowed: the maximum votes allowed for this contest
        :return: True if the equation is satisfied, False if not
        """
        left = number.mod_p(pow(self.generator, number.mod_q(votes_allowed * self.contest_challenge), self.large_prime)
                            * pow(self.public_key, self.contest_response, self.large_prime))

        right = number.mod_p(self.contest_beta * pow(beta_product, self.contest_challenge, self.large_prime))

        res = number.equals(left, right)
        if not res:
            print("contest selection limit check equation 2 error. ")

        return res

    def __match_vote_limit_by_contest(self, contest_name: str, num_of_placeholders: int) -> bool:
        """
        match the placeholder numbers in each contest with the maximum
        :param contest_name: name/id of the contest
        :param num_of_placeholders: number of placeholders appear in this contest
        :return:
        """
        vote_limit = int(self.vote_limit_dic.get(contest_name))

        res = number.equals(vote_limit, num_of_placeholders)
        if not res:
            print("contest placeholder number error. ")

        return res

    @staticmethod
    def __increment_num(num: int) -> int:
        """
        increment the input number by 1
        :param num: the number that needs to be incremented
        :return: num + 1
        """
        return num + 1


class BallotSelectionVerifier(ISelectionVerifier):
    """
    This class is responsible for verify one selection at a time,
    its main purpose is to confirm selection validity,
    will be used in ballot_validity_verifier
    """

    def __init__(self, selection_dic: dict, param_g: ParameterGenerator):
        super().__init__(param_g)
        # constants
        self.ZRP_PARAM_NAMES = {'pad', 'data'}
        self.ZQ_PARAM_NAMES = {'challenge', 'response'}

        self.selection_dic = selection_dic
        self.pad = self.selection_dic.get('ciphertext', {}).get('pad')
        self.data = self.selection_dic.get('ciphertext', {}).get('data')

    def get_pad(self) -> int:
        """
        get a selection's alpha
        :return:
        """
        return self.pad

    def get_data(self) -> int:
        """

        :return:
        """
        return self.data

    def is_placeholder_selection(self) -> bool:
        """

        :return:
        """
        return bool(self.selection_dic.get('is_placeholder_selection'))

    # --------------------------------------- validity check ----------------------------------------------------
    def verify_selection_validity(self) -> bool:
        """
        verify a selection within a contest
        :return:
        """
        error = self.initialize_error()

        # get dictionaries
        proof_dic = self.selection_dic.get('proof')
        cipher_dic = self.selection_dic.get('ciphertext')

        # get values
        selection_id = self.selection_dic.get('object_id')
        zero_pad = int(proof_dic.get('proof_zero_pad'))  # a0
        one_pad = int(proof_dic.get('proof_one_pad'))  # a1
        zero_data = int(proof_dic.get('proof_zero_data'))  # b0
        one_data = int(proof_dic.get('proof_one_data'))  # b1
        zero_challenge = int(proof_dic.get('proof_zero_challenge'))  # c0
        one_challenge = int(proof_dic.get('proof_one_challenge'))  # c1
        zero_response = int(proof_dic.get('proof_zero_response'))  # v0
        one_response = int(proof_dic.get('proof_one_response'))  # v1

        # point 1: check alpha, beta, a0, b0, a1, b1 are all in set Zrp
        if not (self.__check_params_within_zrp(cipher_dic) and
                self.__check_params_within_zrp(proof_dic)):
            error = self.set_error()

        # point 3: check if the given values, c0, c1, v0, v1 are each in the set zq
        if not self.__check_params_within_zq(proof_dic):
            error = self.set_error()

        # point 2: conduct hash computation, c = H(Q-bar, (alpha, beta), (a0, b0), (a1, b1))
        challenge = number.hash_elems(self.extended_hash, self.pad, self.data,
                                      zero_pad, zero_data, one_pad, one_data)

        # point 4:  c = c0 + c1 mod q is satisfied
        if not self.__check_hash_comp(challenge, zero_challenge, one_challenge):
            error = self.set_error()

        # point 5: check chaum-pedersen proofs
        if not (self.__check_cp_proof_zero_proof(self.pad, self.data, zero_pad, zero_data,
                                                 zero_challenge, zero_response)
                and self.__check_cp_proof_one_proof(self.pad, self.data, one_pad, one_data,
                                                    one_challenge, one_response)):
            error = self.set_error()

        if error:
            print(selection_id + ' validity verification failure.')

        return not error

    def __check_params_within_zrp(self, param_dic: dict) -> bool:
        """
        check if the given values, alpha, beta, a0, b0, a1, b1 are all in set Zrp
        alpha, beta are from cipher dic and the others are from proof_dic
        :param param_dic: either ciphertext_dic or proof_dic generated in __verify_a_selection
        :return: True if all parameters in this given dict are within set zrp
        """
        error = self.initialize_error()
        # all the relevant parameters in one loop
        for (k, v) in param_dic.items():
            # if it's a desired field, verify the number
            if any(name in k for name in self.ZRP_PARAM_NAMES):
                res = number.is_within_set_zrp(v)
                if not res:
                    error = self.set_error()
                    print('parameter error, {name} is not in set Zrp. '.format(name=k))

        return not error

    def __check_params_within_zq(self, param_dic: dict) -> bool:
        """
        check if the given values, c0, c1, v0, v1 are each in the set zq
        :param param_dic:
        :return:
        """
        error = self.initialize_error()

        for (k, v) in param_dic.items():
            if any(name in k for name in self.ZQ_PARAM_NAMES):
                res = number.is_within_set_zq(v)
                if not res:
                    error = self.set_error()
                    print('parameter error, {name} is not in set Zq. '.format(name=k))

        return not error

    def __check_cp_proof_zero_proof(self, pad, data, zero_pad, zero_data, zero_chal, zero_res) -> bool:
        """

        :param pad:
        :param data:
        :param zero_pad:
        :param zero_data:
        :param zero_chal:
        :param zero_res:
        :return:
        """
        equ1_left = pow(self.generator, zero_res, self.large_prime)
        equ1_right = number.mod_p(zero_pad * pow(pad, zero_chal, self.large_prime))

        equ2_left = pow(self.public_key, zero_res, self.large_prime)
        equ2_right = number.mod_p(zero_data * pow(data, zero_chal, self.large_prime))

        res = number.equals(equ1_left, equ1_right) and number.equals(equ2_left, equ2_right)

        if not res:
            print("Chaum-pedersen proof zero proof failure. ")

        return res

    def __check_cp_proof_one_proof(self, pad, data, one_pad, one_data, one_chal, one_res) -> bool:
        """

        :param pad:
        :param data:
        :param one_pad:
        :param one_data:
        :param one_chal:
        :param one_res:
        :return:
        """
        equ1_left = pow(self.generator, one_res, self.large_prime)
        equ1_right = number.mod_p(one_pad * pow(pad, one_chal, self.large_prime))

        equ2_left = number.mod_p(pow(self.generator, one_chal, self.large_prime) *
                                 pow(self.public_key, one_res, self.large_prime))
        equ2_right = number.mod_p(one_data * pow(data, one_chal, self.large_prime))

        res = number.equals(equ1_left, equ1_right) and number.equals(equ2_left, equ2_right)

        if not res:
            print("Chaum-pedersen proof one proof failure. ")

        return res

    @staticmethod
    def __check_hash_comp(chal, zero_chal, one_chal) -> bool:
        """
        check if the equation c = c0 + c1 mod q is satisfied.
        :param chal:
        :param zero_chal:
        :param one_chal:
        :return:
        """
        # calculated expected challenge value: c0 + c1 mod q
        expected = number.mod_q(int(zero_chal) + int(one_chal))

        res = number.equals(number.mod_q(chal), expected)

        if not res:
            print("challenge value error.")

        return res

    # --------------------------------------- limit check ----------------------------------------------------
    def verify_selection_limit(self) -> bool:
        """

        :return:
        """
        return self.__check_a_b()

    def __check_a_b(self) -> bool:
        """
        check if a selection's a and b are in set Zrp - box 4, limit check
        :return: True if a and b both within set zrp
        """

        a_res = number.is_within_set_zrp(self.pad)
        b_res = number.is_within_set_zrp(self.data)

        if not a_res:
            print('selection pad/a value error. ')

        if not b_res:
            print('selection data/b value error. ')

        return a_res and b_res
