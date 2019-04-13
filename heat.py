import copy

class Heat():
    def __init__(self):
        self.category = "Heat"
        self.dancer = ""
        self.code = ""
        self.partner = ""        
        self.session = "1"
        self.time = ""
        self.extra = ""        
        self.heat_number = 0
        self.info = ""
        # can't tell if a heat has prelim rounds 
        self.rounds = "F"
        self.shirt_number = "???"
        self.result = None
        self.points = None
        self.level = None
        
    def set_category(self, cat):
        self.category = cat
        
    def info_list(self):
        summary = list()
        summary.append(self.category)
        summary.append(str(self.heat_number) + self.extra)
        summary.append(self.session + "@" + self.time)
        summary.append(self.info)        
        summary.append(self.shirt_number)

        dancer_info = ""
        if len(self.partner) > 0:
            dancer_info = self.dancer + " and " + self.partner
        else:
            dancer_info = self.dancer
        summary.append(dancer_info)

        # placeholder for results
        if self.result is None:
            summary.append("---")
        else:
            summary.append(self.result)
        return summary      
    
    
    def set_level(self):
        if self.category == "Pro heat":
            if "Rising Star" in self.info:
                self.level = "Rising Star"
            elif "Novice" in self.info:
                self.level = "Novice"
            else:
                self.level = "Open"   
        else: # TODO: consider amateurs 
            self.level = "None"
#        return level

    # return a blank set of heat information
    def dummy_info(self):
        result = ("-----", "-----", "-----", "-----", "-----", "-----")
        return result    
    
    # override < operator to sort heats by time. 
    # If times are the same, sort by shirt number
    def __lt__(self, h):
        # if session numbers are the same, consider AM vs. PM
        if self.session == h.session:
            if "AM" in self.time and "PM" in h.time:
                return True
            elif "PM" in self.time and "AM" in h.time:
                return False
            # if both AM or both PM, consider 12:xx times less than times of any other hour
            elif "12:" in self.time and "12:" not in h.time:
                return True
            elif "12:" in h.time and "12:" not in self.time:
                return False;
            else:  # if we get to here, either both times are in the 12:xx hour or both are in
                   # some other hour, just sort the times.
                if self.time == h.time:
                    return self.shirt_number < h.shirt_number
                else:
                    return self.time < h.time
        else: # use the session numbers to determine order
            return self.session < h.session    
        
    # override == operator to compare category and number
    def __eq__(self, h):
        return (self.category == h.category) and (self.heat_number == h.heat_number)  

    
class Heat_Report():
    def __init__(self):
        self.entries = list()
        
    def append(self, h):
        self.entries.append(h)
        
    def sort(self):
        self.entries.sort()
        
    def length(self):
        return len(self.entries)
    
    def entry(self, index):
        return self.entries[index]
    
    def description(self):
        return self.entries[0].info
    
    def category(self):
        return self.entries[0].category
    
    def heat_number(self):
        return self.entries[0].heat_number
    
    def level(self):
        return self.entries[0].level
    
    def multi_dance(self):
        d = self.description()
        if "(" in d and ")" in d:
            return True
        else:
            return False
        
    def rounds(self):
        return self.entries[0].rounds
    
    def set_rounds(self, r):
        self.entries[0].rounds = r
        
    def build_late_entry(self):
        e = copy.deepcopy(self.entries[-1])
        # null out certain fields 
        e.shirt_number = "???"
        e.result = None
        e.points = None        
        return e