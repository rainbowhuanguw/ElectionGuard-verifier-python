from project import number, json_parser, constants, hash


class BaselineVerifier:
    """
    This class tests that whether the given parameters p, q, r, g equal to expected values. (box 1)
    """

    def __init__(self, constants_dic: dict):
        # raises type error if the input is not a dict
        if not isinstance(constants_dic, dict):
            raise TypeError("constants_dic should be in type dict. ")

        # constants
        self.DICT_KEYS = {'cofactor', 'generator', 'large_prime', 'small_prime'}
        self.DEFAULT_K = 50

        self.constants_dic = constants_dic
        # raises a value error if the input param doesn't include all the constant fields
        if not self.DICT_KEYS.issubset(constants_dic.keys()):
            raise ValueError("constants_dic should include all the parameters, including p, q, r, g, inverse g")

    def match_prime(self, param_name: str) -> bool:
        """
        verify if p or q matches the expected value
        :param param_name: large_prime, small_prime
        :return: True if the input parameter equals to the expected
        """
        try:
            param_actual = self.constants_dic.get(param_name)
            if param_name == 'large_prime':
                return number.equals(param_actual, constants.LARGE_PRIME)
            elif param_name == 'small_prime':
                return number.equals(param_actual, constants.SMALL_PRIME)
        except ValueError:
            print("Invalid parameter")

    def verify_all_params(self) -> bool:
        """
        verify all parameters including p, q, r, g, inverse g
        :return: True if all parameters are verified to fit in designated equations or have specific values,
                False otherwise
        """
        error = False

        # check if p and q are the expected values
        if not self.match_prime('large_prime'):
            self.__set_error(error)
            print("The actual p value doesn't equal to the expected. ")
        if not self.match_prime('small_prime'):
            self.__set_error(error)
            print("The actual q value doesn't equal to the expected. ")

        # get basic parameters
        p = self.constants_dic.get('large_prime')
        q = self.constants_dic.get('small_prime')
        r = self.constants_dic.get('cofactor')
        g = self.constants_dic.get('generator')

        # use Miller-Rabin algorithm to check the primality of p and q
        # set iteration to run 50 times by default
        if not number.is_prime(p, self.DEFAULT_K):
            self.__set_error(error)
            print("p is not a prime. ")

        if not number.is_prime(q, self.DEFAULT_K):
            self.__set_error(error)
            print("q is not a prime. ")

        # check equation p - 1 = qr
        if not number.equals(p - 1, q * r):
            self.__set_error(error)
            print("p - 1 does not equals to r * q.")

        # check q is not a divisor of r
        if number.is_divisor(q, r):
            self.__set_error(error)
            print("q is a divisor of r.")

        # check 1 < g < p
        if not number.is_within_range(g, 1, p):
            self.__set_error(error)
            print("g is not in the range of 1 to p. ")

        # check g^q mod p = 1
        if not number.equals(pow(g, q, p), 1):
            self.__set_error(error)
            print("g^q mod p does not equal to 1. ")

        return not error

    @staticmethod
    def __set_error(error):
        """
        setter method to set error to True
        :param error: the error variable being passed in
        :return: none
        """
        error = True


class SelectionVerifier:
    """
    This class is reponsible for verify one selection at a time, its main purpose is to confirm selection validity,
    will be used in ballot_validity_verifier,

    """
    def __init__(self, selection_dic: dict, context_dic: dict, constants_dic: dict):
        self.selection_dic = selection_dic
        self.public_key = context_dic.get('public_key')
        self.generator = constants_dic.get('generator')
        self.extended_hash = context_dic.get('crypto_extended_base_hash')
        self.alpha = int(self.selection_dic.get('proof', {}).get('pad'))
        self.beta = int(self.selection_dic.get('proof', {}).get('data'))

        # constants
        self.ZRP_PARAM_NAMES = {'pad', 'data'}
        self.ZQ_PARAM_NAMES = {'challenge', 'response'}

    def get_alpha_beta(self) -> tuple:
        """
        get a selection's alpha and beta
        :return:
        """
        return self.alpha, self.beta
    # --------------------------------------- validity check ----------------------------------------------------
    def verify_selection_validity(self):
        """
        verify a selection within a contest
        :param selection_dic:
        :return:
        """
        error = False

        # get dictionaries
        cipher_dic = self.selection_dic.get('ciphertext')
        proof_dic = self.selection_dic.get('proof')

        # get values
        pad = int(cipher_dic.get('pad'))  # alpha
        data = int(cipher_dic.get('data'))  # beta

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
        if not (self.__check_params_within_zrp(cipher_dic) and self.__check_params_within_zrp(proof_dic)):
            error = True

        # point 3: check if the given values, c0, c1, v0, v1 are each in the set zq
        if not self.__check_params_within_zq(proof_dic):
            error = True

        # point 2: conduct hash computation, c = H(Q-bar, (alpha, beta), (a0, b0), (a1, b1))
        challenge = hash.hash_elems(self.extended_hash, pad, data, zero_pad, zero_data, one_pad, one_data)

        # point 4:  c = c0 + c1 mod q is satisfied
        if not self.__check_hash_comp(challenge, zero_challenge, one_challenge):
            error = True

        # point 5: check equations
        if not (self.__check_equation1(pad, zero_pad, zero_challenge, zero_response) and
                self.__check_equation1(pad, one_pad, one_challenge, one_response) and
                self.__check_equation2(data, zero_data, zero_challenge, zero_response) and
                self.__check_equation3(data, one_data, one_challenge, one_response)):
            error = True

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
        error = False
        # all the relevant parameters in one loop
        for (k, v) in param_dic.items():
            # if it's a desired field, verify the number
            if any(name in k for name in self.ZRP_PARAM_NAMES):
                res = number.is_within_set_zrp(v)
                if not res:
                    error = True
                    print('parameter error, {name} is not in set Zrp. '.format(name=k))

        return not error

    def __check_params_within_zq(self, param_dic: dict) -> bool:
        """
        check if the given values, c0, c1, v0, v1 are each in the set zq
        :param param_list:
        :return:
        """
        error = False

        for (k, v) in param_dic.items():
            if any(name in k for name in self.ZQ_PARAM_NAMES):
                res = number.is_within_set_zq(v)
                if not res:
                    error = True
                    print('parameter error, {name} is not in set Zq. '.format(name=k))

        return not error

    def __check_equation1(self, pad: int, x_pad: int, x_chal: int, x_res: int) -> bool:
        """

        :param x_pad:
        :param x_chal:
        :param x_res:
        :return:
        """
        equ1_left = pow(self.generator, x_res, constants.LARGE_PRIME)
        equ1_right = number.mod(x_pad * pow(pad, x_chal, constants.LARGE_PRIME), constants.LARGE_PRIME)
        res = number.equals(equ1_left, equ1_right)
        if not res:
            print("equation 1 error. ")

        return res

    def __check_equation2(self, data: int, zero_data: int, zero_chal: int, zero_res: int) -> bool:
        """

        :param data:
        :param zero_data:
        :param zero_chal:
        :param zero_res:
        :return:
        """
        equ2_left = pow(self.public_key, zero_res, constants.LARGE_PRIME)
        equ2_right = number.mod(zero_data * pow(data, zero_chal, constants.LARGE_PRIME), constants.LARGE_PRIME)

        res = number.equals(equ2_left, equ2_right)

        if not res:
            print("equation 2 error. ")

        return res

    def __check_equation3(self, data: int, one_data: int, one_chal: int, one_res: int) -> bool:
        """

        :param data:
        :param one_data:
        :param one_chal:
        :param one_res:
        :return:
        """
        equ3_left = number.mod(pow(self.generator, one_chal, constants.LARGE_PRIME) *
                               pow(self.public_key, one_res, constants.LARGE_PRIME), constants.LARGE_PRIME)
        equ3_right = number.mod(one_data * pow(data, one_chal, constants.LARGE_PRIME), constants.LARGE_PRIME)

        res = number.equals(equ3_left, equ3_right)
        if not res:
            print("equation 3 error. ")

        return res

    def __check_hash_comp(self, chal, zero_chal, one_chal) -> bool:
        """
        check if the equation c = c0 + c1 mod q is satisfied.
        :param chal:
        :param zero_chal:
        :param one_chal:
        :return:
        """
        # calculated expected challenge value: c0 + c1 mod q
        expected = number.mod(int(zero_chal) + int(one_chal),
                              constants.SMALL_PRIME)

        res = number.equals(chal, expected)

        if not res:
            print("challenge value error.")

        return res

    # --------------------------------------- limit check ----------------------------------------------------
    def verify_selection_limit(self):
        return self.__check_a_b()


    def __check_a_b(self) -> bool:
        """
        check if a selection's a and b are in set Zrp - box 4, limit check
        :return: True if a and b both within set zrp
        """

        a_res = number.is_within_set_zrp(self.alpha)
        b_res = number.is_within_set_zrp(self.beta)

        if not a_res:
            print('selection pad/a value error. ')

        if not b_res:
            print('selection data/b value error. ')

        return a_res and b_res



