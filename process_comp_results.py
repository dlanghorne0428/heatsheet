
import json
from operator import itemgetter

from comp_results_file import Comp_Results_File

Dance_Styles = [
    "American Rhythm",
    "American Smooth", 
    "International Ballroom",
    "International Latin",
    "Showdance / Cabaret / Theater Arts"
    ]

def event_level(e):
    if "Rising Star" in e:
        level = "Rising Star"
    elif "Novice" in e:
        level = "Novice"
    else:
        level = "Open"
    return level


def get_last_name(couple_names):
    if "," in couple_names:
        f = couple_names.split(",")[0]
    else:
        f = couple_names.split(" and ")[0]
    return f


class RankingDataFile():
    '''
    This class maintains a year-long results file for a particular style,
    such as American Smooth, International Latin, etc. 
    
    It is implemented as a JSON file, containing a list of couples, 
    their results at each comp, their total points and their average points.
    '''
    
    def __init__(self, filename):
        ''' Open the filename and load the data.'''
        self.filename = filename
        fp = open(filename, encoding="utf-8")
        self.info = json.load(fp)
        # Sort by name in ascending order after opening the file.
        self.sort_couples()
        fp.close()
        
        
    def add_result_to_couple(self, index, result):
        couple = self.info[index]
        # make sure this is a new result
        if result not in couple["results"]:
            couple["results"].append(result)
            couple["total_pts"] += int(result["points"])
            couple["avg_pts"] = round(i["total_pts"] / len(i["results"]), 2)  
            
    
    def find_couple_by_last_name(self, couple_name):
        couple_last_name = get_last_name(couple_name)
        index = -1
        for i in self.info:
            index += 1
            db_last_name = get_last_name(i["name"])
            # search for the couple, using last names only
            if db_last_name == couple_last_name:
                # exit loop after couple found, let user determine match
                return index
        else:        
            return -1    
        

    def find_couple(self, couple_name):
        ''' 
        This routine searches the data for the specified couple.
        If the couple is found, and the result is not in their list, it
        is added, and the points are recalculated 
        
        If this is a new couple, an error message is printed.
        #TODO: support adding new couples when this becomes part of the GUI app
        '''
        index = -1
        for i in self.info:
            index += 1
            # search for the couple, using the entire string
            if i["name"] == couple_name:
                # exit loop after couple found
                return index
        else:        
            return -1
    
    
    def format_item_as_columns(self, index):
        '''
        This method returns the data for the couple at the specified index as a list.
        It is meant to be called by the GUI.
        '''
        info_list = [index+1]  # first column is the index
        info_list.append(self.info[index]["name"])  # then the name
        info_list.append(len(self.info[index]["results"])) # then how many events
        info_list.append(self.info[index]["total_pts"])  # then total points
        info_list.append(self.info[index]["avg_pts"])  # last is average points - the ranking
        return info_list
        
        
    def length(self):
        '''This method returns the number of couples in the Ranking Data.'''
        return len(self.info)
    
    
    def get_name_at_index(self, index):
        return self.info[index]["name"]
    

    def sort_couples(self, key="name", reverse=False):
        '''This method sorts the couples by the selected key.'''    
        self.info.sort(key=itemgetter(key), reverse=reverse)
        
                
    def save(self):
        ''' This method sorts the data, writes it to the file, and closes the file.''' 
        self.sort_couples(key="avg_pts", reverse=True)
        fp = open(self.filename, "w", encoding="utf-8")
        json.dump(self.info, fp, indent=2)
        fp.close()


def process_comp_results(filename):
    '''
    This function reads in the results of a competition and adds the info to the 
    year-long ranking files.
    '''
    
    # open the five ranking files
    smooth_couples = RankingDataFile("data/2019/!!2019_Results/smooth_results.json")
    rhythm_couples = RankingDataFile("data/2019/!!2019_Results/rhythm_results.json")
    standard_couples = RankingDataFile("data/2019/!!2019_Results/standard_results.json")
    latin_couples = RankingDataFile("data/2019/!!2019_Results/latin_results.json")
    showdance_couples = RankingDataFile("data/2019/!!2019_Results/cabaret_showdance_results.json")
    
    # open the competition results, get the comp name and heat info
    comp_results = Comp_Results_File(filename)
    comp_name = comp_results.get_comp_name()
    heats = comp_results.get_heats()
    
    # loop through the heats
    for h in heats:
    
        # get the title and the event level of the current heat
        event_name = h["title"]
        print(event_name)
        level = event_level(event_name)
    
        # Determine what style this heat is (e.g. SMOOTH)
        # and get access to the ranking data for that style
        if "Smooth" in event_name:
            print("-----SMOOTH-------", level)
            couples = smooth_couples
        elif "Rhythm" in event_name:
            print("-----RHYTHM-------", level)
            couples = rhythm_couples
        elif "Latin" in event_name:
            print("-----LATIN-------", level)
            couples = latin_couples
        elif "Standard" in event_name or "Ballroom" in event_name:
            print("-----STANDARD-------", level)
            couples = standard_couples
        else:
            print("-----SHOWDANCE / CABARET -------", level)
            couples = showdance_couples
    
        # For each couple in this heat, get their name, then build 
        # a result structure. Add those results to the year-long rankings. 
        for entry in h["entries"]:
            couple = entry["couple"]
            result = dict()
            result["comp_name"] = comp_name
            result["level"] = level
            result["place"] = entry["place"]
            result["points"] = entry["points"]
            couples.add_result_to_couple(couple, result)
    
    # once all the heats have been processed, save the ranking files and
    # close the competition result file
    smooth_couples.save()
    rhythm_couples.save()
    standard_couples.save()
    latin_couples.save()
    showdance_couples.save()
    comp_results.close()


if __name__ == '__main__':
    # When this module is run (not imported) call the function with a filename
    process_comp_results("./data/2019/First_Coast_Classic/results.txt")