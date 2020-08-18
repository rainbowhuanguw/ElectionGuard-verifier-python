from project import number, json_parser, constants


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


#TODO: test in main function, create unit test and move it to test file
if __name__ == "__main__":
    constants_dic = json_parser.read_json_file('/Users/rainbowhuang/Desktop/ElectionGuard/data_08132020/constants.json')
    #print(constants_dic)
    bv = BaselineVerifier(constants_dic)
    res = bv.verify_all_params()
    if not res:
        print("Baseline parameter check failure. ")
    else:
        print("Baseline parameter check success. ")
