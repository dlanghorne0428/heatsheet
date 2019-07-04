import json
from operator import itemgetter
from heat import Heat, Heat_Report, dance_style, non_pro_heat_level
from dancer import Dancer
from couple import Couple

age_div_prefix_list = ("L-", "G-", "AC-", "Pro ", "AC-", "Professional", "AM/AM", "Amateur", "Youth", "MF-", "M/F") 

class Heatlist():

    def __init__(self):
        # store the name of the comp,
        self.comp_name = "--Click Open to load a Heat Sheet File--"
        self.dancers = list()   # store a list of the individual dancers competing
        self.couples = list()   # store a list of the couples competing
        self.solos = list()     # store a list of the solo performances (as heat objects)
        self.formations = list()    # store a list of the formation performances (as heat objects)
        self.event_titles = list() 
        self.multi_dance_heat_numbers = list()  # store a list of multi dance non-pro heat (as integers)
        self.age_divisions = ["* ALL *"]   # store a list of the age divisions
        self.max_heat_num = 0      # store the largest heat number in the comp
        self.max_pro_heat_num = 0  # store the largest pro heat number in the comp
        self.max_solo_num = 0      # store the largest solo number in the comp
        self.max_formation_num = 0 # store the largest formation number in the comp


    ############### EXTRACTION ROUTINES  #################################################
    # the following methods extract specific data items from lines in the CompMngr file
    ######################################################################################
    # look for an age division on the given line. Return it or None if no age division found
    def get_age_division(self, line, prefixes=age_div_prefix_list):
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
    def list_of_couples_in_heat(self, heat, sortby="shirt"):
        if sortby == "info":
            sort_col = 3
        else:
            sort_col = 4    # shirt number column
        output_list = list()
        for c in self.couples:
            for ht in c.heats:
                if heat == ht:
                    output_list.append(ht.info_list())
                    break
        output_list.sort(key=itemgetter(sort_col))
        return output_list
    
    # given a heat, this method returns a heat report, which is a list of 
    # all entries in the heat. This list can optionally be sorted by shirt number
    def build_heat_report(self, heat, sorted=False, heat_type="pro"):
        report = Heat_Report()
        for c in self.couples:
            for ht in c.heats:
                if heat == ht:
                    if heat_type == "Amateur":
                        if ht.multi_dance() and ht.amateur_heat():
                            report.append(ht)
                    elif heat_type == "Pro-Am":
                        if ht.multi_dance() and not ht.amateur_heat():
                            report.append(ht)                        
                    else:  # pro heat
                        report.append(ht)
        if sorted:
            report.sort()
        return report
    
    # add to list of non-pro multi dance heats
    def add_multi_dance_heat(self, num):
        if num not in self.multi_dance_heat_numbers:
            self.multi_dance_heat_numbers.append(num)  
            
    def add_event(self, info):
        if info not in self.event_titles:
            self.event_titles.append(info)
            
    def write_event_list_to_file(self, folder_name):
        filename = folder_name + "/events.csv"
        f = open(filename, "w")
        for title in self.event_titles:
            level = non_pro_heat_level(title)
            f.write(self.comp_name + ',' + title + ',' + dance_style(title) + "," + str(level) + "\n")
        f.close()

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
    
    ############### COMMON FILE FORMAT ROUTINES  #########################################
    # the following methods deal with saving heatlists in a common file format and
    # reloading them. This eliminates the need to return to the original website source.
    ######################################################################################    
    
    def get_next_dancer(self, dancer_index):
        '''Read heat information for the next dance from the common file format.
           Must be called after the file has alrady been opened.
        '''
        line = self.fp.readline().strip()
        fields = line.split(":")
        d = self.dancers[dancer_index]
        num_heats = int(fields[-1])
        for index in range(num_heats):
            line = self.fp.readline().strip()
            heat_info = json.loads(line)
            h = Heat()
            h.populate(heat_info)
            d.add_heat(h)

            if h.partner == "":
                couple = None
            else:
                couple = Couple(h.dancer, h.partner)
                new_couple = True  # assume this is a new couple
                for c in self.couples:      
                    if couple.same_names_as(c):
                        new_couple = False
                        couple = c   # set the couple variable to the existing couple object
                        break
                # if this actually is a new couple, add them to the couples list
                if new_couple:
                    self.couples.append(couple)
                # add the heat to this couple
                couple.add_heat(h)
            
            age_div = self.get_age_division(h.info)
            if age_div is not None:
                self.add_age_division(age_div)
                d.add_age_division(age_div)
                if couple is not None:
                    couple.add_age_division(age_div)
            
            if h.category == "Solo":
                if h.heat_number > self.max_solo_num:
                    self.max_solo_num = h.heat_number   
                if h not in self.solos:
                    self.solos.append(h)
            elif h.category == "Formation": 
                if h.heat_number > self.max_formation_num:
                    self.max_formation_num = h.heat_number 
                self.formations.append(h)
            elif h.category == "Pro heat":
                if h.heat_number > self.max_pro_heat_num:
                    self.max_pro_heat_num = h.heat_number      
            else:
                if h.heat_number > self.max_heat_num:
                    self.max_heat_num = h.heat_number 
                if h.multi_dance():
                    self.add_multi_dance_heat(h.heat_number)
                    self.add_event(h.info)
            
        return self.dancers[dancer_index].name
    
    
    def complete_processing(self):
        '''Complete the process of reading heatsheet data from the common file format.'''
        self.fp.close()
        self.formations.sort()
        self.solos.sort()
        self.age_divisions.sort()
        self.multi_dance_heat_numbers.sort()
        self.event_titles.sort()    
        
        
    def open(self, filename):
        '''Begin the process of reading heatsheet data from the common file format.'''
        self.fp = open(filename, encoding="UTF-8")
        line = self.fp.readline().strip()
        self.comp_name = line.split(":")[1]
        print(self.comp_name)
        line = self.fp.readline().strip()
        while True:
            line = self.fp.readline().strip()
            if line == "Heats":
                break
            else:
                fields = line.split(":")
                d = Dancer(fields[0], fields[1])
                self.dancers.append(d)

        
    
    def save(self, filename):
        '''Save heatsheet data to a common file format.'''
        fp = open(filename, "w", encoding="UTF-8")
        fp.write("Comp Name:" + self.comp_name + "\n")
        fp.write("Dancers" + "\n")
        for d in self.dancers:
            fp.write(d.name + ":" + d.code + "\n")  
        fp.write("Heats" + "\n")
        for d in self.dancers:
            fp.write("Dancer:" + d.name + ":" + d.code + ":Heats:" + str(len(d.heats)) + "\n")
            for h in d.heats:
                json.dump(h.info_list(), fp)
                fp.write("\n")
        fp.close()

