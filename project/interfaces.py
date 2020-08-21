from .generator import ParameterGenerator, VoteLimitCounter


class IVerifier:
    def __init__(self, param_g: ParameterGenerator):
        self.param_g = param_g
        self.generator = self.param_g.get_generator()
        self.extended_hash = self.param_g.get_extended_hash()
        self.public_key = self.param_g.get_elgamal_key()
        self.large_prime = self.param_g.get_large_prime()
        self.small_prime = self.param_g.get_small_prime()

    @staticmethod
    def set_error() -> bool:
        return True

    @staticmethod
    def initiate_error() -> bool:
        return False


class IBallotVerifier(IVerifier):
    def __init__(self, param_g: ParameterGenerator, limit_counter: VoteLimitCounter ):
        super().__init__(param_g)
        self.limit_counter = limit_counter


class IContestVerifier(IVerifier):
    """
    Contest verifier as an interface
    """

    def verify_a_contest(self) -> bool:
        pass


class ISelectionVerifier(IVerifier):
    def get_pad(self) -> int:
        pass

    def get_data(self) -> int:
        pass
