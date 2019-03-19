import json
from operator import itemgetter

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
        
    def format_as_columns(self):
        info_list = [self.entry["couple"]]
        info_list.append(self.entry["place"])
        return info_list
        

class Heat_Result():
    ''' This class is basically a simple dictionary.
        The use of a single attribute as the dictionary is ugly,
        but this needs to be JSON serializable.
    '''    
    def __init__(self):
        self.heat = dict()
        self.heat["title"] = "Unknown Heat"
        self.heat["entries"] = []
        
    def sort_entries(self):
        self.heat["entries"].sort(key=itemgetter("place"))
        
    def set_title(self, title):
        self.heat["title"] = title
        
    def set_next_entry(self, e):
        self.heat["entries"].append(e.entry)


class Comp_Results_File():
    ''' Here is the class for the Comp_Results_File
        It supports reading and writing of the Comp Results
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
    
    def save_heat(self, h):
        ''' add a set of heat results to the structure.'''
        h.sort_entries()
        self.info["heats"].append(h.heat)
        
    def get_heats(self):
        ''' return all the heat results.'''
        return self.info["heats"]
    
    def close(self):
        ''' If the file is open for writing, dump the 
            data structure to the file.
            In both read and write modes, close the file.
        '''
        if self.mode.upper().startswith("W"):
            json.dump(self.info, self.fp, indent=2)
        self.fp.close()
