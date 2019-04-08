from operator import itemgetter

class Heatlist():

    def __init__(self):
        # store the name of the comp,
        self.comp_name = "--Click Open to load a Heat Sheet File--"
        self.dancers = list()   # store a list of the individual dancers competing
        self.couples = list()   # store a list of the couples competing
        self.solos = list()     # store a list of the solo performances (as heat objects)
        self.formations = list()    # store a list of the formation performances (as heat objects)
        self.age_divisions = ["* ALL *"]   # store a list of the age divisions
        self.max_heat_num = 0      # store the largest heat number in the comp
        self.max_pro_heat_num = 0  # store the largest pro heat number in the comp
        self.max_solo_num = 0      # store the largest solo number in the comp
        self.max_formation_num = 0 # store the largest formation number in the comp

    ############### EXTRACTION ROUTINES  #################################################
    # the following methods extract specific data items from lines in the CompMngr file
    ######################################################################################
    # look for an age division on the given line. Return it or None if no age division found
    def get_age_division(self, line, prefixes):
        #prefixes = ("L-", "G-", "AC-", "Pro ")  # valid prefixes for division
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
    # sorted by the shirt number
    def list_of_couples_in_heat(self, heat):
        shirt_number_col = 4
        output_list = list()
        for c in self.couples:
            for ht in c.heats:
                if heat == ht:
                    output_list.append(ht.info_list())
                    break
        output_list.sort(key=itemgetter(shirt_number_col))
        return output_list
    
    # given a heat, this method returns a heat report, which is a dictionary, 
    # containing heat information, including a list of entries. 
    # This list can optionally be sorted by shirt number
    def heat_report(self, heat, sorted=False):
        report = dict()
        report["category"] = heat.category
        report["number"] = heat.heat_number
        report["entries"] = list()
        for c in self.couples:
            for ht in c.heats:
                if heat == ht:
                    entry = dict()
                    entry["dancer"] = ht.dancer
                    entry["code"] = ht.code
                    entry["partner"] = ht.partner
                    entry["shirt"] = ht.shirt_number
                    entry["result"] = None
                    entry["points"] = 0
                    if len(report["entries"]) == 0:
                        report["info"] = ht.info
                        report["rounds"] = ht.rounds
                        report["level"]= ht.level()
                    report["entries"].append(entry)
        
        if sorted:
            report["entries"].sort(key=itemgetter("shirt"))
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

