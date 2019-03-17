# prepare JSON files for each dance style
import json

from comp_results_file import Comp_Results_File

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
        # TODO: sort by name in ascending order after opening the file.
        #self.sort_couples("name")
        fp.close()

    def add_result_to_couple(self, couple, result):
        ''' 
        This routine searches the data for the specified couple.
        If the couple is found, and the result is not in their list, it
        is added, and the points are recalculated 
        
        If this is a new couple, an error message is printed.
        #TODO: support adding new couples when this becomes part of the GUI app
        '''
        for i in self.info:
            # search for the couple, using the entire string
            if i["name"] == couple:
                
                # couple found, make sure this is a new result
                if result not in i["results"]:
                    i["results"].append(result)
                    i["total_pts"] += int(result["points"])
                    i["avg_pts"] = round(i["total_pts"] / len(i["results"]), 2)
                
                # exit loop after couple found
                break
        else:
            # couple was not found, search again using only the dancer's last name
            # possible reasons for not matching entire string: 
            #    married couples may be out of order 
            #    maiden name may be used 
            #    slight misspelling of names
            c_dancer = get_last_name(couple)
            for i in self.info:
                i_dancer = get_last_name(i["name"])
                
                # if the last name matches, ask the user if this looks like the right couple
                # TODO: make this a GUI input
                if i_dancer == c_dancer:
                    response = input("Match " + i["name"] + " with " + couple + " (y/n)? ")
                    if response.upper() == 'Y':
                        
                        # make sure this is a new result before adding it.
                        if result not in i["results"]:
                            i["results"].append(result)
                            i["total_pts"] += int(result["points"])
                            i["avg_pts"] = round(i["total_pts"] / len(i["results"]), 2)

                        # exit loop, once user confirms a match
                        break
            else:
                # still not found, print an error message
                print("COULD NOT FIND:", couple, result)
    
    
    def swap_couples(self, i, j):
        ''' This method supports sorting the data structure by swapping two entries.'''
        temp = self.info[i]
        self.info[i] = self.info[j]
        self.info[j] = temp;        
    
    def less_than(self, i, j, mode="points"):
        ''' This method supports sorting the data structure by comparing two entries.'''
        if mode.upper() == "NAME":
            return self.info[i]["name"] < self.info[j]["name"]
        else:
            return self.info[i]["avg_pts"] < self.info[j]["avg_pts"]
    
    
    def sort_couples(self, mode="points"):
        '''This method performs an insertion sort on the couples.'''
        # TODO: provide option to sort in ascending order
        i = 1
        while i < len(self.info):
            j = i
            # sort list in descending order of average points
            while j > 0 and self.less_than(j-1, j, mode):
                self.swap_couples(j, j-1)
                j = j - 1
            i = i + 1
            
        # print the sorted list to the console
        for entry in self.info:
            print(entry["name"], entry["avg_pts"])
        
                
    def save(self):
        ''' This method sorts the data, writes it to the file, and closes the file.''' 
        self.sort_couples()
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