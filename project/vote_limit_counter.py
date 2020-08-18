
class VoteLimitCounter:
    def __init__(self, description_dic: dict):
        self.description_dic = description_dic
        self.contest_vote_limits = {}

    def get_contest_vote_limits(self):
        """
        :return:
        """
        # fill in dictionary when it's empty
        if not bool(self.contest_vote_limits):
            self.__fill_contest_vote_limits()

        return self.contest_vote_limits

    def __fill_contest_vote_limits(self):
        """
        fill in the num_max_vote dictionary, key- contest name, value- maximum votes allowed for this contest
        source: description
        :return:
        """

        contests = self.description_dic.get('contests')
        for contest in contests:
            contest_name = contest.get('object_id')
            num_max_vote = contest.get('votes_allowed')
            self.contest_vote_limits[contest_name] = int(num_max_vote)
