import json

class Entry_Result():
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
        

class Heat_Result():
    def __init__(self):
        self.heat = dict()
        self.heat["title"] = "Unknown Heat"
        self.heat["entries"] = []
        
    def set_title(self, title):
        self.heat["title"] = title
        
    def set_next_entry(self, entry):
        self.heat["entries"].append(entry)


class Comp_Results_File():
    def __init__(self, filename, mode="r"):
        self.filename = filename
        self.mode = mode
        if mode.upper().startswith("W"):
            self.fp = open(filename, "w", encoding="UTF-8")
            self.info = dict()
            self.info["comp name"] = "Unknown Competition"
            self.info["heats"] = []
        else:
            self.fp = open(filename, encoding="UTF-8")
            self.info = json.load(self.fp)            
            
            
    def save_comp_name(self, name):
        self.info["comp name"] = name
        
    def get_comp_name(self):
        return self.info["comp name"]
    
    def save_heat(self, h):
        self.info["heats"].append(h)
        
    def get_heats(self):
        return self.info["heats"]
    
    def close(self):
        if self.mode.upper().startswith("W"):
            json.dump(self.info, self.fp, indent=2)
        self.fp.close()
