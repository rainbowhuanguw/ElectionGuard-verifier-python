from project import number, hash, constants


class ShareVerifier:
    def __init__(self, shares: list, selection_pad: int, selection_data: int, generator: int,
                 extended_hash: int, public_keys: list):
        self.__shares = shares
        self.__selection_pad = selection_pad
        self.__selection_data = selection_data
        self.__generator = generator
        self.__extended_hash = extended_hash
        self.__public_keys = public_keys

    def verify_all_shares(self) -> bool:
        """
        verify all shares of a tally decryption
        :return:
        """
        error = False
        for index, share in enumerate(self.__shares):
            if not self.__verify_a_share(share):
                error = True
                print("Guardian {} decryption error. ".format(index))

        return not error

    def __verify_a_share(self, share_dic: dict) -> bool:
        """
        verify one share at a time
        :param share_dic:
        :return:
        """
        error = False
        pad, data = self.get_pad_data(share_dic)
        response = share_dic.get('proof', {}).get('response')
        # check if the response vi is in the set Zq
        response_correctness = self.__check_response(response)

        # check if the given ai, bi are both in set Zrp
        pad_data_correctness = self.__check_pad_data(pad, data)

        if not response_correctness or not pad_data_correctness:
            error = True
            print("partial decryption failure. ")

        return not error

    @staticmethod
    def get_pad_data(share_dic: dict) -> tuple:
        """
        return the pad and data of a share within a selection
        :return:
        """
        return share_dic.get('proof', {}).get('pad'), share_dic.get('proof', {}).get('data')

    @staticmethod
    def __check_response(response: int) -> bool:
        """
        check if the response vi is in the set Zq
        :param response:
        :return:
        """
        res = number.is_within_set_zq(response)
        if not res:
            print("response error. ")

        return res

    @staticmethod
    def __check_pad_data(pad: int, data: int) -> bool:
        """
        check if the given ai, bi are both in set Zrp
        :param pad:
        :param data:
        :return:
        """
        a_res = number.is_within_set_zrp(pad)
        b_res = number.is_within_set_zrp(data)

        if not a_res:
            print("a/pad value error. ")

        if not b_res:
            print("b/data value error. ")

        return a_res and b_res

    def __check_challenge(self, challenge: int, pad: int, data: int, partial_decrypt: int) -> bool:
        """
        check if the challenge values ci satisfies ci = H(Q-bar, (A,b), (ai, bi), Mi)
        :return:
        """
        challenge_computed = hash.hash_elems(self.__extended_hash, self.__selection_pad, self.__selection_data,
                                             pad, data, partial_decrypt)

        res = number.equals(challenge, challenge_computed)

        if not res:
            print("challenge value error. ")

        return res

    def __check_equation1(self, response: int, pad: int, challenge: int, public_key: int) -> bool:
        """
        check g ^ vi = ai * (Ki ^ ci) mod p
        :param response:
        :param pad:
        :param public_key:
        :param challenge:
        :return:
        """
        left = pow(self.__generator, response, constants.LARGE_PRIME)
        right = number.mod(pad * pow(public_key, challenge, constants.LARGE_PRIME), constants.LARGE_PRIME)

        res = number.equals(left, right)

        if not res:
            print("equation 1 error. ")

        return res

    def __check_equation2(self, response: int, data: int, challenge: int, partial_decrypt: int) -> bool:
        """
        check A^vi = bi * (Mi^ci) mod p
        :param response:
        :param data:
        :param challenge:
        :param partial_decrypt:
        :return:
        """
        left = pow(self.__selection_pad, response, constants.LARGE_PRIME)
        right = number.mod(data * pow(partial_decrypt, challenge, constants.LARGE_PRIME), constants.LARGE_PRIME)

        res = number.equals(left, right)
        if not res:
            print("equation 2 error. ")

        return res
