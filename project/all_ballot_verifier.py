import glob
from project import json_parser
from project.ballot_encryption_verifier import BallotEncryptionVerifier


class AllBallotsVerifier:

    def __init__(self, folder_path: str, generator: int, extended_hash: int, public_key: int, vote_limit_dic: dict):
        self.folder_path = folder_path
        self.generator = generator
        self.extended_hash = extended_hash
        self.public_key = public_key
        self.vote_limit_dic = vote_limit_dic

    def verify_all_ballots(self):
        error = False
        count = 0
        for ballot_file in glob.glob(self.folder_path + '*.json'):
            ballot_dic = json_parser.read_json_file(ballot_file)
            bvv = BallotEncryptionVerifier(ballot_dic, self.generator, self.public_key,
                                           self.extended_hash, self.vote_limit_dic)
            res = bvv.verify_all_contests()
            if not res:
                error = True
                count += 1
