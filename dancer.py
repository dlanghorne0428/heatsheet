class Dancer():
    '''This class stores information about a Dancer, including name,
       scoresheet code, age divisions, and Heat information.'''
    def __init__(self, name="", code=""):
        self.name = name
        self.code = code
        self.heats = list()
        self.age_divisions = list()
        
        
    def add_heat(self, h):
        '''This method adds the heat information, h, to the list of heats
           that this dancer is competing in.'''
        if h not in self.heats:
            self.heats.append(h)
            self.heats.sort()
            

    def add_age_division(self, d):
        '''This method adds the age division, d, to the list of age divisions
           that this dancer is competing in.'''
        if d not in self.age_divisions:
            self.age_divisions.append(d)
            self.age_divisions.sort() 
            

    def format_name(orig_name, split_on=1):
        '''This static function converts a name into last, first format.'''
        name = ""
        fields = orig_name.split()
        for f in range(split_on, len(fields)):
            if f > split_on:
                name += " "
            name += fields[f]
        name += ","
        for f in range(0, split_on):
            name += " " + fields[f]
        return name