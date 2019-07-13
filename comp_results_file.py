import json
from operator import itemgetter

from heat import Heat, Heat_Report

''' This module writes the results of a competition to a JSON file.
    There are three classes: 
    Comp_Result: the results for the entire competition.
                 It has a name and a list of Heat Results  
                
    Heat_Result: the results for a single heat. 
                 It has a title and a list of Entry Results
                
    Entry_Result: the resuls for a couple in that heat
    '''


class Entry_Result():
    ''' This class is basically a simple dictionary.
        The use of a single attribute as the dictionary is ugly,
        but this needs to be JSON serializable.
    '''
    def __init__(self):
        self.entry = dict()
        self.entry["couple"] = "Thing, One and Thing, Two"
        self.entry["place"] = 0
        self.entry["points"] = 0
        
    def set_couple(self, c):
        self.entry["couple"] = c
        
    def set_place(self, p):
        self.entry["place"] = p
    
    def set_points(self, p):
        self.entry["points"] = p
        
    #def format_as_columns(self):
        #info_list = [self.entry["couple"]]
        #info_list.append(self.entry["place"])
        #return info_list
        

class Heat_Result():
    ''' This class is basically a simple dictionary.
        The use of a single attribute as the dictionary is ugly,
        but this needs to be JSON serializable.
    '''    
    def __init__(self):
        self.heat = dict()
        self.heat["number"] = 0
        self.heat["title"] = "Unknown Heat"
        self.heat["entries"] = []
        
    def length(self):
        return len(self.heat["entries"])
        
    def sort_entries(self):
        self.heat["entries"].sort(key=itemgetter("place"))
        
    def set_title(self, title):
        self.heat["title"] = title
        
    def set_heat_number(self, num):
        self.heat["number"] = num
        
    def set_next_entry(self, e):
        self.heat["entries"].append(e.entry)


class Comp_Results_File():
    ''' Here is the class for the Comp_Results_File
        It supports reading and writing of the results for a single competition.
    '''
    def __init__(self, filename, mode="r"):
        self.filename = filename
        self.mode = mode
        
        # if the mode is write, open the file and create an 
        # empty dictionary 
        if mode.upper().startswith("W"):
            self.fp = open(filename, "w", encoding="UTF-8")
            self.info = dict()
            self.info["comp name"] = "Unknown Competition"
            self.info["heats"] = []
        else:
            # if the mode is read, load the JSON file
            self.fp = open(filename, encoding="UTF-8")
            self.info = json.load(self.fp)            
            
    def save_comp_name(self, name):
        ''' set the name of the competition.'''
        self.info["comp name"] = name
        
    def get_comp_name(self):
        ''' return the name of the competition.'''
        return self.info["comp name"]
        
    def save_heat(self, heat_report):
        ''' add a set of heat results to the structure.'''        
        index = 0 
        current_info = heat_report.description()
        heat_result = Heat_Result()
        heat_result.set_title(current_info)
        heat_result.set_heat_number(heat_report.heat_number())   
        
        while index < heat_report.length():
            e = heat_report.entry(index)
            if e.info != current_info:
                if heat_result.length() > 0:
                    heat_result.sort_entries()
                    self.info["heats"].append(heat_result.heat)
                heat_result = Heat_Result()
                current_info = e.info
                heat_result.set_title(current_info)
                heat_result.set_heat_number(heat_report.heat_number())        
            if e.result is not None:
                ent_result = Entry_Result()
                # Write out the couple names, their placement, and the points
                ent_result.set_couple(e.dancer + " and " + e.partner)
                ent_result.set_place(str(e.result))
                ent_result.set_points(e.points)
                heat_result.set_next_entry(ent_result)
            index += 1
            
        if heat_result.length() > 0:        
            heat_result.sort_entries()
            self.info["heats"].append(heat_result.heat)    
            
    
    def save_updated_heat_result(self, heat_result):
        self.info["heats"].append(heat_result)
            
        
    def get_heats(self):
        ''' return all the heat results.'''
        return self.info["heats"]
    
    def get_heat(self, index):
        ''' return the results of a single heat.'''
        return self.info["heats"][index]
    
    
    def num_heats(self):
        return len(self.info["heats"])
        
    
    def close(self):
        ''' If the file is open for writing, dump the 
            data structure to the file.
            In both read and write modes, close the file.
        '''
        if self.mode.upper().startswith("W"):
            json.dump(self.info, self.fp, indent=2)
        self.fp.close()
