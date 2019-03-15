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


def get_first_name(couple_names):
    if "," in couple_names:
        f = couple_names.split(",")[0]
    else:
        f = couple_names.split(" and ")[0]
    return f


class RankingDataFile():
    def __init__(self, filename):
        self.filename = filename
        fp = open(filename, encoding="utf-8")
        self.info = json.load(fp)
        fp.close()

    def add_result_to_couple(self, couple, result):
        for i in self.info:
            if i["name"] == couple:
                if result not in i["results"]:
                    i["results"].append(result)
                    i["total_pts"] += int(result["points"])
                    i["avg_pts"] = round(i["total_pts"] / len(i["results"]), 2)
                    #print(i)
                break
        else:
            c_dancer = get_first_name(couple)
            for i in self.info:
                i_dancer = get_first_name(i["name"])
                if i_dancer == c_dancer:
                    response = input("Match " + i["name"] + " with " + couple + " (y/n)? ")
                    if response.upper() == 'Y':
                        if result not in i["results"]:
                            i["results"].append(result)
                            i["total_pts"] += int(result["points"])
                            i["avg_pts"] = round(i["total_pts"] / len(i["results"]), 2)
                            #print(i)
                        break
            else:
                print("COULD NOT FIND:", couple, result)
    
    
    
    def swap_couples(self, i, j):
        temp = self.info[i]
        self.info[i] = self.info[j]
        self.info[j] = temp;        
    
    
    def sort_couples(self):
        i = 1
        while i < len(self.info):
            j = i
            # sort list in descending order of average points
            while j > 0 and self.info[j-1]["avg_pts"] < self.info[j]["avg_pts"]:
                self.swap_couples(j, j-1)
                j = j - 1
            i = i + 1

        for entry in self.info:
            print(entry["name"], entry["avg_pts"])
        
                
    def save(self):
        self.sort_couples()
        fp = open(self.filename, "w", encoding="utf-8")
        json.dump(self.info, fp, indent=2)
        fp.close()


def process_comp_results(filename):
    
    smooth_couples = RankingDataFile("data/2019/!!2019_Results/smooth_results.json")
    rhythm_couples = RankingDataFile("data/2019/!!2019_Results/rhythm_results.json")
    standard_couples = RankingDataFile("data/2019/!!2019_Results/standard_results.json")
    latin_couples = RankingDataFile("data/2019/!!2019_Results/latin_results.json")
    showdance_couples = RankingDataFile("data/2019/!!2019_Results/cabaret_showdance_results.json")
    
    comp_results = Comp_Results_File(filename)
    comp_name = comp_results.get_comp_name()
    heats = comp_results.get_heats()
    
    for h in heats:
    
        event_name = h["title"]
        print(event_name)
        level = event_level(event_name)
    
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
    
        for entry in h["entries"]:
            couple = entry["couple"]
            result = dict()
            result["comp_name"] = comp_name
            result["level"] = level
            result["place"] = entry["place"]
            result["points"] = entry["points"]
            #print(couple, result)
            couples.add_result_to_couple(couple, result)
    
    smooth_couples.save()
    rhythm_couples.save()
    standard_couples.save()
    latin_couples.save()
    showdance_couples.save()
    
    comp_results.close()


if __name__ == '__main__':
    # When this module is run (not imported) call the function with a filename
    process_comp_results("./data/2019/First_Coast_Classic/results.txt")