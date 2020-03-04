import copy

def is_multi_dance(s):
    left_pos = s.find('(')
    right_pos = s.find(')')
    if left_pos == -1 or right_pos == -1:
        return False
    elif "Mixed" in s or "Solo Star" in s or "NP" in s:
        return False
    elif "/" in s[left_pos:right_pos] or "," in s[left_pos:right_pos]:
        return True
    else:
        return False
    
    
def is_amateur_heat(s):
    if "AC-" in s or "AA-" in s or "Amateur" in s or "YY-" in s or "AM/AM" in s or "AmAm" in s:
        return True
    else:
        return False

 
def is_junior_heat(s):
    if "-Y" in s or "-J" in s or "PT" in s or "-TB" in s or "JR" in s:
        return True
    else:
        return False
    
    
def dance_style(s):
    if "Smooth" in s:
        return "Smooth"
    elif "Rhythm" in s:
        return "Rhythm"
    elif "Latin" in s:
        return "Latin"
    elif "Standard" in s or "Ballroom" in s or "Balroom" in s or "Ballrom" in s:
        return "Standard"  
    elif "Nightclub" in s or "Night Club" in s or "NightClub" in s or "Niteclub" in s or "Nite Club" in s or "Caribbean" in s:
        return "Nightclub"
    elif "Country" in s:
        return "Country"
    elif "Cabaret" in s or "Theatre" in s or "Theater" in s or "Exhibition" in s:
        return "Cabaret"
    else:
        print("Unknown style for heat", s)
        return "Unknown"
    
def pro_heat_level(info):
    #TODO: for 2020, fix pro heat results to save the event title. 
    if type(info) == int:
        return info
    if "Rising Star" in info or "RS" in info:
        return 10  #"Rising Star"
    elif "Novice" in info or "Basics" in info or "Pre-Champ" in info:
        return 5   #"Novice"
    else:
        return 20  #"Open"  
    
    
def extra_points(info, check_for_open=True):
    value = 0
    if check_for_open and "Open" in info:
        value += 5
    if "Scholarship" in info or "Scolarship" in info:
        value += 5
    return value    

    
def non_pro_heat_level(info):
    if "Newcomer" in info or "Novice" in info:
        return 5 + extra_points(info)
    elif "Bronze" in info:
        return 10 + extra_points(info)
    elif "Silver" in info:
        return 15 + extra_points(info)
    elif "Gold" in info:
        return 20 + extra_points(info)
    elif "Closed" in info or "Challenge" in info:
        return 15 + extra_points(info)
    elif "Open" in info or "World" in info:
        return 20 + extra_points(info, False)
    elif "Pre-Champ" in info or "PreChamp" in info or "Pre Champ" in info:
        return 15 
    elif "Champ" in info or "Grand Slam" in info:
        return 20  
    elif "Scholar" in info:
        return 25
    else:
        if is_multi_dance(info):
            print("Unknown level for heat", info)
        return 15    
    
    
# return a blank set of heat information
def dummy_heat_info():
    result = ("-----", "-----", "-----", "-----", "-----", "-----")
    return result 


def prefix_removed(info):
    if info.startswith("L-"):
        return info[2:]
    elif info.startswith("G-"):
        return info[2:]
    elif info.startswith("AP-"):
        return info[3:]
    elif info.startswith("PA-"):
        return info[3:]  
    else:
        return info


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
        
    def swap_names(self):
        ''' This routine switches the names of a couple to match the scoresheet.
            In a pro heat the male dancer is listed first. 
        '''    
        temp = self.dancer
        self.dancer = self.partner
        self.partner = temp    
        
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
    
    
    def populate(self, info_list, dancer_code=0):
        self.category = info_list[0]
        
        #extract heat number and extra info, if any
        try:
            self.heat_number = int(info_list[1])
        except:
            end_index = 0
            while info_list[1][end_index].isdigit():
                end_index += 1
            self.heat_number = int(info_list[1][:end_index])
            self.extra = info_list[1][end_index:]
        
        time_fields = info_list[2].split("@")
        self.session = time_fields[0]
        self.time = time_fields[1]
        
        self.info = info_list[3]
        self.set_level()
        self.shirt_number = info_list[4]
        
        couple_fields = info_list[5].split(" and ")
        self.dancer = couple_fields[0]
        self.code = dancer_code
        if len(couple_fields) == 2:
            self.partner = couple_fields[1]

    
    
    def set_level(self):
        if self.category == "Pro heat":
            self.level = pro_heat_level(self.info)  
        else:  
            self.level = non_pro_heat_level(self.info)

            
    def multi_dance(self):
        return is_multi_dance(self.info)
    

    def amateur_heat(self):
        return is_amateur_heat(self.info)


    def junior_heat(self):
        return is_junior_heat(self.info)   
    
    
    # override < operator to sort heats by time. 
    # If times are the same, sort by info. 
    # If info is the same, sort by shirt number
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
                    if self.heat_number == h.heat_number:
                        self_no_prefix = prefix_removed(self.info)
                        h_no_prefix = prefix_removed(h.info)
                        if self_no_prefix == h_no_prefix:
                            return self.shirt_number < h.shirt_number
                        else:
                            return self_no_prefix < h_no_prefix                       
                    else:
                        return self.heat_number < h.heat_number

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
    
    def entry(self, index = 0):
        return self.entries[index]
    
    def description(self, index = 0):
        return self.entries[index].info
    
    def category(self):
        return self.entries[0].category
    
    def heat_number(self):
        return self.entries[0].heat_number
    
    def extra(self, index = 0):
        return self.entries[index].extra
    
    def level(self):
        return self.entries[0].level
    
    def multi_dance(self):
        return is_multi_dance(self.description())
        
    def rounds(self):
        return self.entries[0].rounds
    
    def set_rounds(self, r):
        self.entries[0].rounds = r
        
    def build_late_entry(self, entry=None):
        if entry is None:
            e = copy.deepcopy(self.entries[-1])
        else:
            e = copy.deepcopy(entry)
        # null out certain fields 
        e.shirt_number = "???"
        e.result = None
        e.points = None        
        return e