import string
from operator import itemgetter

from couple import Couple
from dancer import Dancer
from heat import Heat, Heat_Report
from heatlist import Heatlist

# this module processes a ballroom competition heatlist file in HTML format generated by the CompMngr program.

# this class stores heat information for a particular couple or dancer
class CompMngrHeat(Heat):
    def __init__(self, category, line="", dancer="", scoresheet_code=0, partner="", number=0):
        super().__init__()
        self.category = category    # heat, solo, pro heat, formation
        self.dancer = dancer
        self.code = scoresheet_code
        self.partner = partner      # partner may be none for a member of a formation
        self.heat_number = number
        if len(line) > 0:           # if line is not empty, parse it to obtain other properites
            fields = line.split("<td>")
            # get the session number, heat number, and multi-round info
            heat_time = fields[1].split("</td>")[0]
            heat_time_fields = heat_time.split("@")
            self.session = heat_time_fields[0]
            heat_time = heat_time_fields[1]
            if "<br>" in heat_time:
                time_fields = heat_time.split("<br>")
                if len(time_fields) == 4:
                    self.rounds = "Q"  # start with quarter-final
                else:
                    self.rounds = "S"  # start with semi-final
                self.time = time_fields[0] + "-" + self.rounds  # truncate "Later rounds" from time string
            else:
                self.time = heat_time
                self.rounds = "F"      # final only
            
            # get the shirt number
            self.shirt_number = fields[2].split("</td>")[0]
            
            # get the heat info
            self.info = fields[4].split("</td>")[0]
            self.set_level()
            
            # pull any non-digit characters from the heat number into extra
            start_pos = fields[3].find(category) + len(category) + 1
            i = start_pos
            # stop at the first non-digit
            while fields[3][i] in string.digits:
                i = i + 1
            if i > start_pos:
                self.heat_number = int(fields[3][start_pos:i])
            # anything non-digit is extra information, like ballroom assignment
            num_chars = len("</td>")
            self.extra = fields[3][i:-num_chars]
            self.extra = self.extra.replace("Ballroom ", "")


# this class stores information about a dancer that is in the competition
class CompMngrDancer(Dancer):
    def __init__(self, line):
        super().__init__()
        # find the dancer's name
        start_pos = 8
        end_pos = line.find("</td>")
        self.name = line[start_pos:end_pos]
        # find the code number that can be used to grab their results from a scoresheet
        start_pos = line.find("TABLE_CODE_") + len("TABLE_CODE_")
        end_pos = line.find("'", start_pos)
        self.code = line[start_pos:end_pos]


# This class parses the heatlist and stores information about the competition
class CompMngrHeatlist(Heatlist):

    def __init__(self):
        super().__init__()
        self.fhand = None
        
    ############### EXTRACTION ROUTINES  #################################################
    # the following methods extract specific data items from lines in the CompMngr file
    ######################################################################################
    # look for an age division on the given line. Return it or None if no age division found
    def get_age_division(self, line):
        prefixes = ("L-", "G-", "AC-", "Pro ")  # valid prefixes for division
        return super().get_age_division(line, prefixes)

    # the comp name is found on the given line after a <strong> tag until the next HTML tag
    def get_comp_name(self,line):
        start_pos = line.find("<strong>") + len("<strong>")
        end_pos = line.find("<", start_pos)
        name = line[start_pos:end_pos]
        return name

    # this method returns the dancer name from a line, starting at a given column.
    # In the HTML file produced by CompMngr, the dancer names are inside a <strong> tag.
    def get_dancer_name(self, line, start_pos=20):
        end_pos = line.find("</strong>")
        name = line[start_pos:end_pos]
        # TODO: Handle single name people
        return name


    ################# READING THE HEATLIST HTML FILE ################################
    # this routine processes the HTML data file in CompMngr heatlist format
    # and populates the data structures
    ##################################################################################
    # open the heatlist filename and process all the lines
    def open(self, filename):
        dancer = None       # variables for the current dancer
        found_last_dancer = False

        # open the file and loop through all the lines
        self.fhand = open(filename,encoding="utf-8")
        for line in self.fhand:
            # look for TABLE_CODE to find the name of each dancer entered in the competition
            if "Show entries" in line:
                dancer = CompMngrDancer(line.strip())
                self.dancers.append(dancer)
            # if we see the line that says "size="", extract the name of the competition
            if 'size=' in line:
                self.comp_name = self.get_comp_name(line.strip())
            if "/table" in line:
                print("Found", len(self.dancers), "dancers")
                found_last_dancer = True
            if "/div" in line:
                if found_last_dancer:
                    break; 
            
            
    def get_next_dancer(self, dancer_index):
        dancer = None       # variables for the current dancer
        couple = None       # and the current couple
        
        while True:
            line = self.fhand.readline()
            # A line with "Entries For" indicates the start of a new dancer's heat information
            if "Entries for" in line:
                dancer_name = self.get_dancer_name(line.strip())
                if dancer_name == self.dancers[dancer_index].name:
                    dancer = self.dancers[dancer_index]
                    dancer_index += 1
                else:  # search for dancer name
                    print("Searching for dancer")
                    for d in self.dancers:
                        if d.name == dancer_name:
                            dancer = d
                            break
            # A line with "With " indicates the start of a new partner for the current dancer
            if "With " in line:
                partner = self.get_dancer_name(line.strip(), line.find("With ") + 5)
                if "/" in partner:
                    couple = None
                elif len(partner) == 0:
                    couple = None
                else:
                    couple = Couple(dancer.name, partner)
                    new_couple = True  # assume this is a new couple
                    for c in self.couples:
                        if couple.same_names_as(c):
                            new_couple = False
                            couple = c   # set the couple variable to the existing couple object
                            break
                    # if this actually is a new couple, add them to the couples list
                    if new_couple:
                        self.couples.append(couple)

            # Look for age divisions
            if couple is not None:
                age_div = self.get_age_division(line.strip())
                if age_div is not None:
                    self.add_age_division(age_div)
                    couple.add_age_division(age_div)
                    dancer.add_age_division(age_div)

            # look for lines with heat number information
            if "Heat " in line:
                if couple is not None:
                    # turn this line into a heat object and add it to the couple and dancer
                    heat_obj = CompMngrHeat("Heat", line, dancer.name, dancer.code, partner)
                    if heat_obj.heat_number > self.max_heat_num:
                        self.max_heat_num = heat_obj.heat_number
                    if heat_obj.multi_dance():
                        self.add_multi_dance_heat(heat_obj.heat_number)
                        self.add_event(heat_obj.info)
                    couple.add_heat(heat_obj)
                    dancer.add_heat(heat_obj)

            # look for lines with solo number information
            if "Solo " in line:
                if couple is not None:
                    # turn this line into a heat object and add it to the couple and dancer
                    solo_obj = CompMngrHeat("Solo", line, dancer.name, dancer.code, partner)
                    if solo_obj.heat_number > self.max_solo_num:
                        self.max_solo_num = solo_obj.heat_number                    
                    couple.add_heat(solo_obj)
                    dancer.add_heat(solo_obj)
                    # add this solo to the list of solos for the comp
                    if solo_obj not in self.solos:
                        self.solos.append(solo_obj)

            # look for lines with pro heat number information
            if "Pro heat " in line:
                if couple is not None:
                    # turn that heat info into an object and add it to the couple
                    pro_heat = CompMngrHeat("Pro heat", line, dancer.name, dancer.code, partner)
                    if pro_heat.heat_number > self.max_pro_heat_num:
                        self.max_pro_heat_num = pro_heat.heat_number
                    couple.add_heat(pro_heat)
                    dancer.add_heat(pro_heat)

            if "Formation" in line:
                if dancer is not None:
                    # turn that heat info into an object and add it to the couple
                    form_heat = CompMngrHeat("Formation", line, dancer.name, dancer.code, "")
                    if form_heat.heat_number > self.max_formation_num:
                        self.max_formation_num = form_heat.heat_number                    
                    dancer.add_heat(form_heat)
                    self.formations.append(form_heat)
                    
            if "/div" in line:
                break;
            
        return dancer_name
                    

    def complete_processing(self): 
        # close the file and sort the lists
        self.fhand.close()
        self.formations.sort()
        self.solos.sort()
        self.age_divisions.sort()
        self.multi_dance_heat_numbers.sort()
        self.event_titles.sort()

