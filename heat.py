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
        
    def set_category(self, cat):
        self.category = cat
        
    def info_list(self):
        info = list()
        info.append(self.category)
        info.append(str(self.heat_number) + self.extra)
        info.append(self.session + "@" + self.time)
        info.append(self.info)        
        info.append(self.shirt_number)

        dancer_info = ""
        if len(self.partner) > 0:
            dancer_info = self.dancer + " and " + self.partner
        else:
            dancer_info = self.dancer
        info.append(dancer_info)

        # placeholder for results
        info.append("---")
        return info      
    
    def level(self):
        if self.category == "Pro heat":
            if "Rising Star" in self.info:
                level = "Rising Star"
            elif "Novice" in self.info:
                level = "Novice"
            else:
                level = "Open"   
        else: # TODO: consider amateurs 
            level = "None"
        return level

    # return a blank set of heat information
    def dummy_info(self):
        result = ("-----", "-----", "-----", "-----", "-----", "-----")
        return result    
    
    # override < operator to sort heats by time
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
                return self.time < h.time
        else: # use the session numbers to determine order
            return self.session < h.session    
        
    # override == operator to compare time and number
    def __eq__(self, h):
        return (self.session == h.session) and \
               (self.time == h.time) and \
               (self.heat_number == h.heat_number)   