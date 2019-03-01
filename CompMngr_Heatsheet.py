import string

# this module processes a ballroom competition heatsheet file in HTML format generated by the CompMngr program.

# this class stores heat information for a particular couple or dancer
class Heat():
    def __init__(self, category, line="", dancer="", scoresheet_code = 0, partner="", number=0):
        self.category = category    # heat, solo, pro heat, formation
        self.dancer = dancer
        self.scoresheet_code = scoresheet_code
        self.partner = partner      # partner may be none for a member of a formation
        self.heat_number = number
        if len(line) > 0:           # if line is not empty, parse it to obtain other properites
            fields = line.split("<td>")
            heat_time = fields[1].split("</td>")[0]
            if "<br>" in heat_time:
                # TO DO: maybe store later rounds as separate heats?
                self.time = heat_time.split("<br>")[0]  # truncate "Later rounds"
            else:
                self.time = heat_time
            self.shirt_number = fields[2].split("</td>")[0]
            self.info = fields[4].split("</td>")[0]
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

    # return the heat information as a list of strings
    def info_list(self, dancer=None):
        results = list()
        results.append(self.category)
        results.append(str(self.heat_number) + " " + self.extra)
        results.append(self.time)

        # make this logic better
        dancer_info = ""
        if len(self.partner) > 0:
            dancer_info = self.dancer + " and " + self.partner
        else:
            dancer_info = self.dancer

        results.append(dancer_info)
        results.append(self.shirt_number)
        results.append(self.info)
        return results

    # return a blank set of heat information
    def dummy_info(self):
        result = ("-----", "-----", "-----", "-----", "-----", "-----")
        return result

    # override < operator to sort heats by time
    def __lt__(self, h):
        # get the session numbers out of the time string
        my_session = self.time.split("@")[0]
        h_session = h.time.split("@")[0]
        # if session numbers are the same, consider AM vs. PM
        if my_session == h_session:
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
            return my_session < h_session


    # override == operator to compare category and number
    def __eq__(self, h):
        return (self.category == h.category) and (self.heat_number == h.heat_number)


# this class stores information about a dancer that is in the competition
class Dancer():
    def __init__(self, line):
        # find the dancer's name
        start_pos = 8
        end_pos = line.find("</td>")
        self.name = line[start_pos:end_pos]
        # find the code number that can be used to grab their results from a scoresheet
        start_pos = line.find("TABLE_CODE_") + len("TABLE_CODE_")
        end_pos = line.find("'", start_pos)
        self.scoresheet_code = line[start_pos:end_pos]
        self.heats = list()
        self.age_divisions = list()

    # this method adds the age division, d, to the list of age divisions
    # that this dancer is competing in
    def add_age_division(self, d):
        if d not in self.age_divisions:
            self.age_divisions.append(d)
            self.age_divisions.sort()

    # this method adds the heat info, h, to the list of heats
    # that this dancer is competing in
    def add_heat(self, h):
        if h not in self.heats:
            self.heats.append(h)
            self.heats.sort()


# this class stores information about a couple that is dancing in the competition
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
            self.heats.sort()



# This class parses the heatsheet and stores information about the competition

class CompMngrHeatsheet():

    def __init__(self):
        # store the name of the comp,
        self.comp_name = "--Click Open to load a Heat Sheet File--"
        self.dancers = list()   # store a list of the individual dancers competing
        self.couples = list()   # store a list of the couples competing
        self.solos = list()     # store a list of the solo performances (as heat objects)
        self.formations = list()    # store a list of the formation performances (as heat objects)
        self.age_divisions = ["* ALL *"]   # store a list of the age divisions
        self.max_heat_num = 0;     # store the largest heat number in the comp
        self.max_pro_heat_num = 0; # store the largest pro heat number in the comp

    ############### EXTRACTION ROUTINES  #################################################
    # the following methods extract specific data items from lines in the CompMngr file
    ######################################################################################
    # look for an age division on the given line. Return it or None if no age division found
    def get_age_division(self, line):
        prefixes = ("L-", "G-", "AC-", "Pro ")  # valid prefixes for division
        return_val = None
        for p in prefixes:
            start_pos = line.find(p)
            if start_pos == -1:                 # if prefix not found, try another one
                continue
            else:
                end_pos = line.find(" ",start_pos)  # if prefix found, look for blank that follows division
                return_val = line[start_pos:end_pos]  # return the division string
                break
        return return_val

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
        return name

    ############### DANCER / COUPLE ROUTINES  ###########################################
    # the following methods deal with dancers and couples in the competition
    #####################################################################################

    # this method returns a list of dancer names in this competition
    def dancer_name_list(self):
        l = list()
        for d in self.dancers:
            l.append(d.name)
        return l


    # this method returns a list of couple names in this competition
    def couple_name_list(self):
        l = list()
        for c in self.couples:
            l.append(c.pair_name)
        return l

    # given a pair of names, find out if this couple has already been found
    # return that couple object, or None if this is a new couple.
    def find_couple(self, couple_names):
        for c in self.couples:
            if c.pair_name == couple_names:
                return c
        return None

    # a dancer may be part of multiple couples.
    # given a dancer's name, find the couples they are a part of.
    def find_all_couples_for_dancer(self, dancer_name):
        l = list()
        for c in self.couples:
            if c.name1 == dancer_name or c.name2 == dancer_name:
                l.append(c.pair_name)
        return l
    

    ############### HEAT ROUTINES  ######################################################
    # the following methods deal with heats and their participants
    #####################################################################################
    # this method finds the dancer of a given name and returns a list of their heats
    def find_heats_for_dancer(self, dancer_name):
        for d in self.dancers:
            if d.name == dancer_name:
                return d.heats
        return None

    # given a heat, this method returns a list of dancers in that heat
    def list_of_dancers_in_heat(self, heat):
        output_list = list()
        for d in self.dancers:
            for ht in d.heats:
                if heat == ht:
                    output_list.append(ht.info_list())
                    break
        return output_list

    # given a heat, this method returns a list of couples in that heat
    def list_of_couples_in_heat(self, heat):
        output_list = list()
        for c in self.couples:
            for ht in c.heats:
                if heat == ht:
                    output_list.append(ht.info_list())
                    break
        return output_list
    
    
    def heat_report(self, heat):
        report = dict()
        report["category"] = heat.category
        report["number"] = heat.heat_number
        report["entries"] = list()
        for c in self.couples:
            for ht in c.heats:
                if heat == ht:
                    entry = dict()
                    entry["dancer"] = ht.dancer
                    entry["code"] = ht.scoresheet_code
                    entry["partner"] = ht.partner
                    entry["shirt"] = ht.shirt_number
                    if len(report["entries"]) == 0:
                        report["info"] = ht.info
                    report["entries"].append(entry)
                    
        return report

    ############### AGE DIVISION ROUTINES  ###############################################
    # the following methods deal with age divisions
    ######################################################################################

    # add the age_div to the list of age divisions, if it is not already there
    def add_age_division(self, age_div):
        if age_div not in self.age_divisions:
            self.age_divisions.append(age_div)

    # given a dancer's name, return a list of their age divisions
    def find_age_divisions_for_dancer(self, dancer_name):
        for d in self.dancers:
            if d.name == dancer_name:
                return d.age_divisions
        return None

    # given an age division, return a list of dancer names that are in that division
    def find_dancers_in_age_division(self, division):
        results = list()
        for d in self.dancers:
            if division == "* ALL *" or division in d.age_divisions:
                results.append(d.name)
        return results

    # given an age division, return a list of couple names that are in that division
    def find_couples_in_age_division(self, division):
        results = list()
        for c in self.couples:
            if division == "* ALL *" or division in c.age_divisions:
                results.append(c.pair_name)
        return results

    ################# READING THE HEATSHEET HTML FILE ################################
    # this routine processes the HTML data file in CompMngr heatsheet format
    # and populates the data structures
    ##################################################################################
    # open the heatsheet filename and process all the lines
    def process(self, filename):
        dancer = None       # variables for the current dancer
        couple = None       # and the current couple

        # open the file and loop through all the lines
        fhand = open(filename,encoding="utf-8")
        for line in fhand:
            # look for TABLE_CODE to find the name of each dancer entered in the competition
            if "Show entries" in line:
                dancer = Dancer(line.strip())
                self.dancers.append(dancer)
            # if we see the line that says "size="", extract the name of the competition
            if 'size=' in line:
                self.comp_name = self.get_comp_name(line.strip())
            # A line with "Entries For" indicates the start of a new dancer's heat information
            if "Entries for" in line:
                dancer_name = self.get_dancer_name(line.strip())
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
                    heat_obj = Heat("Heat", line, dancer.name, dancer.scoresheet_code, partner)
                    if heat_obj.heat_number > self.max_heat_num:
                        self.max_heat_num = heat_obj.heat_number
                    couple.add_heat(heat_obj)
                    dancer.add_heat(heat_obj)

            # look for lines with solo number information
            if "Solo " in line:
                if couple is not None:
                    # turn this line into a heat object and add it to the couple and dancer
                    solo_obj = Heat("Solo", line, dancer.name, dancer.scoresheet_code, partner)
                    couple.add_heat(solo_obj)
                    dancer.add_heat(solo_obj)
                    # add this solo to the list of solos for the comp
                    if solo_obj not in self.solos:
                        self.solos.append(solo_obj)

            # look for lines with pro heat number information
            if "Pro heat " in line:
                if couple is not None:
                    # turn that heat info into an object and add it to the couple
                    pro_heat = Heat("Pro heat", line, dancer.name, dancer.scoresheet_code, partner)
                    if pro_heat.heat_number > self.max_pro_heat_num:
                        self.max_pro_heat_num = pro_heat.heat_number
                    couple.add_heat(pro_heat)
                    dancer.add_heat(pro_heat)

            if "Formation" in line:
                if dancer is not None:
                    # turn that heat info into an object and add it to the couple
                    form_heat = Heat("Formation", line, dancer.name, dancer.scoresheet_code, "")
                    dancer.add_heat(form_heat)
                    self.formations.append(form_heat)


        # close the file and sort the lists
        fhand.close()
#        self.couples.sort()
        self.formations.sort()
        self.solos.sort()
        self.age_divisions.sort()
