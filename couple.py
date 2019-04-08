class Couple():
    def __init__(self, dancer, partner):
        # store each individual name, and their names combined
        self.name1 = min(dancer, partner)
        self.name2 = max(dancer, partner)
        self.pair_name = self.name1 + " and " + self.name2

        # store a list of age divisions and heats that this couple is competing in.
        self.age_divisions = list()

        # stores a list of heats that this couple is participating in
        self.heats = list()

    # this method compares the names of the couple c, with the current object
    def same_names_as(self, c):
        if self.pair_name == c.pair_name:
            return True
        else:
            return False

    # this method adds the age division, d, to the list of age divisions
    # that this couple is competing in
    def add_age_division(self, d):
        if d not in self.age_divisions:
            self.age_divisions.append(d)
            self.age_divisions.sort()

    # this method adds the heat info, h, to the list of heats
    # that this couple is competing in
    def add_heat(self, h):
        if h not in self.heats:
            self.heats.append(h)  