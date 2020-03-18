class Couple():
    '''This class stores information about a Couple, including names,
       age divisions, and Heat information.'''
    def __init__(self, dancer, partner):
        '''Declare a couple object, with the names of the dancers.'''
        # store each individual name, and their names combined
        self.name1 = min(dancer, partner)
        self.name2 = max(dancer, partner)
        self.pair_name = self.name1 + " and " + self.name2

        # store a list of age divisions and heats that this couple is competing in.
        self.age_divisions = list()

        # stores a list of heats that this couple is participating in
        self.heats = list()


    def same_names_as(self, c):
        '''This method compares the names of the couple c, with the current object.'''   
        if self.pair_name == c.pair_name:
            return True
        elif self.name1 == c.name2 and self.name2 == c.name1:
            return True
        else:
            return False
        
        
    def swap_names(self):
        '''This method swaps the names of the couple'''  
        temp = self.name1
        self.name1 = self.name2
        self.name2 = temp
        self.pair_name = self.name1 + " and " + self.name2
    
        
    def update_names(self, names):
        '''This method updates the names of the couple.'''  
        self.pair_name = names
        l = names.split(" and ")
        self.name1 = l[0]
        self.name2 = l[1]
        for h in self.heats:
            h.dancer = self.name1
            h.partner = self.name2


    def add_age_division(self, d):
        '''This method adds the age division, d, to the list of age divisions
           that this couple is competing in.'''   
        if d not in self.age_divisions:
            self.age_divisions.append(d)
            self.age_divisions.sort()


    def add_heat(self, h):
        '''This method adds the heat info, h, to the list of heats
           that this couple is competing in.'''   
        if h not in self.heats:
            self.heats.append(h)  