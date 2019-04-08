class Dancer():
    def __init__(self):
        self.name = ""
        self.code = ""
        self.heats = list()
        self.age_divisions = list()
        
    def add_heat(self, h):
        if h not in self.heats:
            self.heats.append(h)
            self.heats.sort()
            
    # this method adds the age division, d, to the list of age divisions
    # that this dancer is competing in
    def add_age_division(self, d):
        if d not in self.age_divisions:
            self.age_divisions.append(d)
            self.age_divisions.sort() 