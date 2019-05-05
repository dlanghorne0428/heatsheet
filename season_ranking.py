
import json
from operator import itemgetter

from comp_results_file import Comp_Results_File


def event_level(e):
    '''
    This routine determines the level (Open, Rising Star, or Novice)
    from the title string. This only support Professional Event Categories.
    '''
    if "Rising Star" in e:
        level = "Rising Star"
    elif "Novice" in e:
        level = "Novice"
    else:  # open is the default
        level = "Open"
    return level


def get_last_name(couple_names):
    '''
    This function splits a string with two couple names to return
    the last name of the first dancer in the couple.
    '''
    if "," in couple_names:
        # there is a comma, so return the portion of the string in 
        # front of the first comma
        f = couple_names.split(",")[0]
    else:
        # return the entire name of the first dancer
        f = couple_names.split(" and ")[0]
    return f


class RankingDataFile():
    '''
    This class maintains a year-long results file for a particular style,
    such as American Smooth, International Latin, etc. 
    
    It is implemented as a JSON file, containing a list of couples, 
    their results at each comp, their total points and their average points.
    
    #TODO: support adding new couples
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
        '''
        This routine checks the couple at the specified index.
        If this result is not in their list, it is added, and the 
        points are recalculated.
        '''
        couple = self.info[index]
        # make sure this is a new result
        if result not in couple["results"]:
            couple["results"].append(result)
            couple["total_pts"] += result["points"]
            couple["total_pts"] = round(couple["total_pts"], 2)
            couple["avg_pts"] = round(couple["total_pts"] / len(couple["results"]), 2)  
            
          
    def delete_all_results_from_couple(self, index):
        couple = self.info[index]
        couple["results"] = list()
        couple["total_pts"] = 0
        couple["avg_pts"] = 0
        
    
    def find_highest_rank(self, index):
        '''
        This routine is called on a list of couples sorted by ranking.
        It starts at the given index and moves upward in the list to 
        see if the couple at that index is tied with any couples listed above.
        If ties are found, it returns the highest index as a string, with a
        T- prefix to indicate a tie.
        '''
        tie_found = False
        while index > 0:
            if self.info[index-1]["avg_pts"] == self.info[index]["avg_pts"]:
                tie_found = True
                index -= 1
            else:
                break;
        # add one to the zero-based index to obtain the ranking
        if tie_found:
            return "T-" + str(index+1)
        else:
            return str(index+1)

    
    def find_couple_by_last_name(self, couple_name, start=0):
        ''' 
        This routine searches the list for the specified couple 
        based on last name only.
        '''
        couple_last_name = get_last_name(couple_name)
        index = start
        while index < len(self.info):
            db_last_name = get_last_name(self.info[index]["name"])
            # search for the couple, using last names only
            if db_last_name == couple_last_name:
                # exit loop after couple found, let user determine match
                return index
            else:
                index += 1
        else:        
            return -1    
        

    def find_couple(self, couple_name):
        ''' 
        This routine searches the list for the specified couple 
        based on the entire name.
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
    
    def get_couple_at_index(self, index):
        return self.info[index]
    
    def get_name_at_index(self, index):
        '''This method returns the name of the couple at the specified index.'''
        return self.info[index]["name"]
    
    
    def set_name_at_index(self, index, new_name):
        '''This method updates the name of the couple at the specified index.'''
        self.info[index]["name"] = new_name
    

    def get_list_of_names(self):
        '''This method returns a list of all the couple names in the data.'''
        name_list = []
        i = 0
        while i < len(self.info):
            name_list.append(self.get_name_at_index(i))
            i += 1
        return name_list
            

    def sort_couples(self, key1="name", key2=None, reverse=False):
        '''This method sorts the couples by the selected key.'''  
        if key2 is None:
            self.info.sort(key=itemgetter(key1), reverse=reverse)
        else:
            self.info.sort(key=itemgetter(key1, key2), reverse=reverse)


    def add_couple(self, couple_name, result=None):
        '''This routine adds a new couple to the database with their first result'''
        new_item = dict()
        new_item["name"] = couple_name
        new_item["results"] = []
        if result is not None:
            new_item["results"].append(result)
            new_item["total_pts"] = result["points"]
            new_item["avg_pts"] = result["points"]
        else:
            new_item["total_pts"] = 0
            new_item["avg_pts"] = 0
        self.info.append(new_item)
        
                
    def save(self):
        ''' This method sorts the data, writes it to the file, and closes the file.''' 
        self.sort_couples(key1="avg_pts", key2="total_pts", reverse=True)
        fp = open(self.filename, "w", encoding="utf-8")
        json.dump(self.info, fp, indent=2)
        fp.close()

