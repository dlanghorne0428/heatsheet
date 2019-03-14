# prepare JSON files for each dance style
import json

def event_level(e):
    if "Rising Star" in e:
        level = "Rising Star"
    elif "Novice" in e:
        level = "Novice"
    else:
        level = "Open"
    return level

def get_first_name(couple_names):
    f = couple_names.split(",")[0]
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
                    i["avg_pts"] = i["total_pts"] / len(i["results"])
                    print(i)
                break
        else:
            for i in self.info:
                i_dancer = get_first_name(i["name"])
                c_dancer = get_first_name(couple)
                if i_dancer == c_dancer:
                    response = input("Match " + i["name"] + " with " + couple + " (y/n)? ")
                    if response.upper() == 'Y':
                        if result not in i["results"]:
                            i["results"].append(result)
                            i["total_pts"] += int(result["points"])
                            i["avg_pts"] = i["total_pts"] / len(i["results"])
                            print(i)
                        break
            else:
                print("Could not find", couple)
                
    def save(self):
        fp = open(self.filename, "w", encoding="utf-8")
        json.dump(self.info, fp, indent=2)
        fp.close()


smooth_couples = RankingDataFile("data/2019/!!2019_Results/smooth_results.json")
rhythm_couples = RankingDataFile("data/2019/!!2019_Results/rhythm_results.json")
standard_couples = RankingDataFile("data/2019/!!2019_Results/standard_results.json")
latin_couples = RankingDataFile("data/2019/!!2019_Results/latin_results.json")
showdance_couples = RankingDataFile("data/2019/!!2019_Results/cabaret_showdance_results.json")

fp = open("data/2019//City_Lights/results.txt", encoding="utf-8")

while True:

    comp_name = fp.readline().strip()
    print(comp_name)
    if comp_name == "No more events":
        break

    event_name = fp.readline().strip()
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

    while True:
        entry = fp.readline().strip()
        if len(entry) == 0:
            break;
        else:
            fields = entry.split("\t")
            couple = fields[0]
            result = dict()
            result["comp_name"] = comp_name
            result["level"] = level
            result["place"] = fields[1]
            result["points"] = fields[2]
            couples.add_result_to_couple(couple, result)

smooth_couples.save()
rhythm_couples.save()
standard_couples.save()
latin_couples.save()
showdance_couples.save()

fp.close()

