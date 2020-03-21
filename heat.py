import copy

from calc_points import pro_heat_level, non_pro_heat_level

        
def dance_style(s):
    '''This function determines the dance style based on the heat description.'''
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


#TODO: develop this class to convert heat_info and populate
class Heat_Summary(list):
    '''This class is used for printing heat information to a file
       or displaying it in a GUI list control.'''
    
    NUM_COLUMNS = 7
    CATEGORY_COLUMN = 0
    HEAT_NUM_COLUMN = 1
    TIME_COLUMN = 2
    INFO_COLUMN = 3
    SHIRT_NUM_COLUMN = 4
    NAMES_COLUMN = 5
    RESULT_RANK_COLUMN = 6
    
    def __init__(self, *args):
        list.__init__(self, *args)
        # the default heat summary is all blanks
        for i in range(Heat_Summary.NUM_COLUMNS):
            self.append("---")
            
    def of_heat(self, h):
        '''Build a Heat_Summary list object from heat h.'''
        self[Heat_Summary.CATEGORY_COLUMN] = h.category
        self[Heat_Summary.HEAT_NUM_COLUMN] = str(h.heat_number) + h.extra
        self[Heat_Summary.TIME_COLUMN] = h.session + "@" + h.time
        self[Heat_Summary.INFO_COLUMN] = h.info        
        self[Heat_Summary.SHIRT_NUM_COLUMN] = h.shirt_number

        dancer_info = ""
        if h.partner is not None:
            dancer_info = h.dancer + " and " + h.partner
        else:
            dancer_info = h.dancer
        self[Heat_Summary.NAMES_COLUMN] = dancer_info

        # placeholder for results
        if h.result is None:
            self[Heat_Summary.RESULT_RANK_COLUMN] = "---"
        else:
            self[Heat_Summary.RESULT_RANK_COLUMN] = h.result        
            

class Heat():
    '''This class stores information about a single heat for one dancer or couple.'''
    def __init__(self):
        # the dancer and partner names are saved as strings
        # one member of the couple will have a shirt number
        self.dancer = ""
        self.partner = "" 
        self.shirt_number = "???"
        
        # the category is either "Heat" or "Pro heat". 
        # Each category has a separate sequence of heat numbers
        self.category = "Heat"        
        self.heat_number = 0
        
        # the extra field is a string with additional info about the heat number
        # this can indicate a ballroom, or simply be a letter like A
        self.extra = ""  
        
        # the info field stores the description of the heat. It is used to 
        # determine the level and dance style.
        self.info = ""

        # the code is a string associated with the dancer, which can be used to 
        # look up results from a scoresheet.
        self.code = ""
     
        # these fields indicate the when the heat is scheduled to be danced
        self.session = "1"
        self.time = ""  

        # this field indicates if the heat had prelim rounds before the Final.
        self.rounds = "F"  # default is Final only

        # the result indicates the place that this dancer finished in this heat.
        # if they made the finals, the result will be an integer. 
        # if they were eliminated in an earlier round, the result will be a string
        self.result = None
        
        # the level stores the number of points awarded to the winner of the heat
        # assuming there were no prelim rounds
        self.level = None

        # this field indicates the number of points earned by the couple in this heat
        self.points = None

        
    def set_category(self, cat):
        '''This routine assigns a category (Heat or Pro heat)'''
        self.category = cat
        
    def swap_names(self):
        ''' This routine switches the names of a couple to match the scoresheet.
            In a pro heat the male dancer is listed first. '''    
        temp = self.dancer
        self.dancer = self.partner
        self.partner = temp    
        
        
    def heat_summary(self):
        '''Create a Heat_Summary object from the current heat.'''
        summary = Heat_Summary()
        summary.of_heat(self)
        return summary
    
    
    def populate(self, summary, dancer_code=0):
        '''populate the current heat from the Heat_Summary list and optional dancer code.'''
        self.category = summary[Heat_Summary.CATEGORY_COLUMN]
        
        #extract heat number and extra info, if any
        try:
            self.heat_number = int(summary[Heat_Summary.HEAT_NUM_COLUMN])
        except:
            end_index = 0
            while summary[Heat_Summary.HEAT_NUM_COLUMN][end_index].isdigit():
                end_index += 1
            self.heat_number = int(summary[Heat_Summary.HEAT_NUM_COLUMN][:end_index])
            self.extra = summary[Heat_Summary.HEAT_NUM_COLUMN][end_index:]
        
        # extract the heat time information
        time_fields = summary[Heat_Summary.TIME_COLUMN].split("@")
        self.session = time_fields[0]
        self.time = time_fields[1]
        
        # extract the heat description
        self.info = summary[Heat_Summary.INFO_COLUMN]
        self.set_level()
        
        # extract the shirt number of the couple and the names
        self.shirt_number = summary[Heat_Summary.SHIRT_NUM_COLUMN]
        couple_fields = summary[Heat_Summary.NAMES_COLUMN].split(" and ")
        self.dancer = couple_fields[0]
        if len(couple_fields) == 2:
            self.partner = couple_fields[1]

        self.code = dancer_code
        

    def info_no_prefix(self):
        '''This function strips off the common prefixes used in heat descriptions.
           In pro-am heats, men and women students often compete against one another but
           the prefixes make it appear they are separate heats.'''
        if self.info.startswith("L-"):
            return self.info[2:]
        elif self.info.startswith("G-"):
            return self.info[2:]
        elif self.info.startswith("AP-"):
            return self.info[3:]
        elif self.info.startswith("PA-"):
            return self.info[3:]  
        else:
            return self.info

    
    def set_level(self):
        '''This routine sets the level field based on the category and heat description'''
        if self.category == "Pro heat":
            self.level = pro_heat_level(self.info)
        else: 
            self.level = non_pro_heat_level(self.info, self.multi_dance())

            
    def multi_dance(self):
        '''This function returns True if the description indicates a multi-dance heat.'''
        s = self.info
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
    

    def amateur_heat(self):
        '''This function returns True if the description indicates an amateur heat.'''
        s = self.info
        if "AC-" in s or "AA-" in s or "Amateur" in s or "YY-" in s or "AM/AM" in s or "AmAm" in s:
            return True
        else:
            return False


    def junior_heat(self):
        '''This function returns True if the description indicates a junior or youth heat.'''
        s = self.info
        if "-Y" in s or "YY" in s or "Youth" in s or "YH" in s or "-LY" in s or \
           "-J" in s or "JR" in s or "J1" in s or "J2" in s or "Junior" in s or \
           "PT" in s or "Preteen" in s or "P1" in s or "P2" in s or "Pre-Teen" in s or \
           "High School" in s or "Elementary School" in s or \
           "-TB" in s or "Teddy Bear" in s:
                  
            # Under 21 heats are sometimes listed as youth, but should not be treated as juniors
            if "U21" in s or "Under 21" in s:
                return False
            else:
                return True
        else:
            return False
    

    def __lt__(self, h):
        ''' override < operator to sort heats by various fields.'''
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
                    # if the times are the same, sort by heat number
                    if self.heat_number == h.heat_number:
                        # if the heat numbers are the same, sort by info/description
                        self_no_prefix = self.info_no_prefix()
                        h_no_prefix = h.info_no_prefix()
                        if self_no_prefix == h_no_prefix:
                            # if the descriptions are the same, sort by shirt number
                            return self.shirt_number < h.shirt_number
                        else:
                            return self_no_prefix < h_no_prefix                       
                    else:
                        return self.heat_number < h.heat_number
                else:
                    return self.time < h.time
        else: # use the session numbers to determine order
            return self.session < h.session    
        
        
    def __eq__(self, h):
        ''' override == operator to compare category and number'''
        return (self.category == h.category) and (self.heat_number == h.heat_number)  

    
class Heat_Report(list):
    '''This class is a list of Heat objects of the couples single heat'''
    def __init__(self, *args):
        list.__init__(self, *args)
        
    def add_entry(self, h, remove_duplicates=True):
        if remove_duplicates:
            for e in self:
                if e.shirt_number == h.shirt_number:
                    break
            else:
                self.append(h)
        else:
            self.append(h)
        
    def length(self):
        return len(self)
    
    def entry(self, index = 0):
        return self[index]
    
    def description(self, index = 0):
        return self[index].info
    
    def category(self):
        return self[0].category
    
    def heat_number(self):
        return self[0].heat_number
    
    def extra(self, index = 0):
        return self[index].extra
    
    def level(self):
        return self[0].level
    
    def multi_dance(self):
        return self[0].multi_dance()
        
    def rounds(self):
        return self[0].rounds
    
    def set_rounds(self, r):
        self[0].rounds = r
        
    def build_late_entry(self, entry=None):
        if entry is None:
            e = copy.deepcopy(self[-1])
        else:
            e = copy.deepcopy(entry)
        # null out certain fields 
        e.shirt_number = "???"
        e.result = None
        e.points = None        
        return e