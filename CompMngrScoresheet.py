import os.path
import requests
from comp_results_file import Comp_Results_File, Heat_Result, Entry_Result

# This class parses the scoresheet and extract results of the competition
class CompMngrScoresheet():

    def __init__(self):
        self.payload = dict()
        self.url = ""
        self.point_values = {
           "Open": {
               "F": [0, 20, 15, 12,  9,  7,  4, 3, 2],
               "S": [0, 30, 24, 20, 16, 12,  9, 7, 5, 4, 0],
               "Q": [0, 40, 32, 25, 20, 15, 12, 9, 7, 6, 3]
            },
           "Rising Star": {
               "F": [0, 10,  7,  5,  3,  2,  1, 1, 1],
               "S": [0, 20, 15, 12,  9,  7,  4, 3, 2, 2, 0],
               "Q": [0, 30, 24, 20, 16, 12,  9, 7, 5, 5, 2]
               },
           "Novice": {
               "F": [0,  5,  4,  3,  2,  1,  1, 1, 1],
               "S": [0, 10,  8,  6,  4,  3,  2, 1, 1, 1, 0],
               "Q": [0, 15, 12, 10,  8,  6,  5, 4, 3, 3, 1]
           }
        }

    def find_url(self, line):
        fields = line.split()
        for f in fields:
            if "action=" in f:
                self.url = f[len("action=")+1:-1]
#                print(self.url)

    def find_payload_field(self, line):
        key = None
        value = None
        start_pos = line.find("name=") + len("name=") + 1
        end_pos = line.find('"', start_pos)  # add 1 to get past first quote
        key = line[start_pos:end_pos]
        start_pos = line.find("value=") + len("value=") + 1
        end_pos = line.find('"', start_pos)  # add 1 to get past first quote
        value = line[start_pos:end_pos]
        self.payload[key] = value


        # open the file and loop through all the lines
        fhand = open(filename,encoding="utf-8")
        for line in fhand:
            if "<form" in line:
                self.find_url(line)
            if "<input" in line:
                self.find_payload_field(line)
        fhand.close()
        
        output_filename = os.path.dirname(filename) + "/results.txt"
        self.output_file = Comp_Results_File(output_filename, "w")
        self.output_file.save_comp_name(self.payload["COMP_NAME"])


    def close(self):
        self.output_file.close()


    def get_table_data(self, line):
        start_pos = line.find("<td>") + len("<td>")
        end_pos = line.find("<", start_pos)
        name = line[start_pos:end_pos]
        return name

    def get_shirt_number(self, competitor):
        fields = competitor.split()
        if len(fields) != 2:
            print("error", fields)
        return fields[0]

    def get_couple_names(self, competitor):
        couple_names = []
        entrant_fields = competitor.split()
        if len(entrant_fields) != 2:
            print("Error", entrant_fields)
        else:
            couple_names = entrant_fields[1].split("/")
            if len(couple_names) != 2:
                print("Error", couple_names)
        return couple_names
        
    def swap_couple_names(self, entry):
        temp = entry["dancer"]
        entry["dancer"] = entry["partner"]
        entry["partner"] = temp


    def process_results(self, heat_report, rounds):
        lines = self.result_file.text.splitlines()
        heat_string = heat_report["category"] + " " + str(heat_report["number"]) + ":"

        if "(" in heat_report["info"] and ")" in heat_report["info"]:
            event = "Multi-Dance"
        else:
            event = "Single Dance"

        level = heat_report["level"]
        # these are state variables
        looking_for_recall_column = False
        looking_for_result_column = False
        looking_for_eliminations = False
        looking_for_finalists = False
        result = None

        for line in lines:
            if looking_for_result_column:
                if "<tr>" in line:
                    count = 0
                elif "<td>" in line and "Result" in line:
                    result_column = count
                    looking_for_finalists = True
                    looking_for_result_column = False
                    count = 0
                elif "<td>" in line:
                    count += 1
            elif looking_for_recall_column:
                if "<tr>" in line:
                    count = 0
                elif "<td>" in line and "Recall" in line:
                    recall_column = count
                    looking_for_eliminations = True
                    looking_for_recall_column = False
                    count = 0
                elif "<td>" in line:
                    count += 1

            elif looking_for_eliminations:
                if "<td>" in line:
                    if count == 0:
                        current_competitor = self.get_table_data(line)
                        found = False
                        count += 1
                    elif count == recall_column:
                        if self.get_table_data(line) != "Recall":
                            for e in heat_report["entries"]:
                                if current_competitor.startswith(e["shirt"]):
                                    couple_names = self.get_couple_names(current_competitor)
                                    if e["dancer"].startswith(couple_names[1]):
                                        self.swap_couple_names(e)
                                    e["result"] = result
                                    e["points"] = self.point_values[level][rounds][result_index]
                                    break
                            else:
                                late_entry = dict()
                                late_entry["shirt"] = self.get_shirt_number(current_competitor)
                                couple_names = self.get_couple_names(current_competitor)    
                                late_entry["dancer"] = couple_names[0] 
                                late_entry["partner"] = couple_names[1] 
                                late_entry["code"] = "LATE"
                                late_entry["result"] = result
                                late_entry["points"] = self.point_values[level][rounds][result_index]
                                heat_report["entries"].append(late_entry)
                        count = 0
                    else:
                        count += 1
                elif "</table>" in line:
                    looking_for_eliminations = False

            elif looking_for_finalists:
                if "<td>" in line:
                    if count == 0:
                        current_competitor = self.get_table_data(line)
                        count += 1
                    elif count == result_column:
                        # need to check for parenthesis, as the result could include a tiebreaker rule
                        result_place = int(self.get_table_data(line).split('(')[0])
                        for e in heat_report["entries"]:
                            if current_competitor.startswith(e["shirt"]):
                                couple_names = self.get_couple_names(current_competitor)
                                if e["dancer"].startswith(couple_names[1]):
                                    self.swap_couple_names(e)
                                e["result"] = result_place
                                e["points"] = self.point_values[level][rounds][result_place]
                                break
                        else:    # this runs when competitor not found in heat
                            late_entry = dict()
                            late_entry["shirt"] = self.get_shirt_number(current_competitor)
                            couple_names = self.get_couple_names(current_competitor)
                            late_entry["dancer"] = couple_names[0] 
                            late_entry["partner"] = couple_names[1]
                            late_entry["code"] = "LATE"
                            late_entry["result"] = result_place
                            late_entry["points"] = self.point_values[level][rounds][result_place]
                            heat_report["entries"].append(late_entry)
                        count = 0
                    else:
                        count += 1
                elif "</table>" in line:
                    looking_for_finalists = False
                    break;

            elif heat_string in line and "Quarter-final" in line and "<p>" in line:
                result = "quarters"
                result_index = -1
                looking_for_recall_column = True
            elif heat_string in line and "Semi-final" in line and "<p>" in line:
                result = "Semis"
                result_index = -2
                looking_for_recall_column = True
            elif heat_string in line and "Final" in line and "<p>" in line:
                result = "Finals"
                if event == "Single Dance":
                    looking_for_result_column = True
            elif result == "Finals" and "Final summary" in line and "<p>" in line:
                if event == "Multi-Dance":
                    looking_for_result_column = True

        return result


    def determine_heat_results(self, heat_report):
        #self.output_file.save_heat_title(heat_report["category"] + " " + str(heat_report["number"]) + " " + heat_report["info"])\
        #level = heat_report["level"]
        rounds = heat_report["rounds"]
        for entry in heat_report["entries"]:
            if entry["result"] is None:
                search_string = entry["code"] + "=" + entry["dancer"]
                self.payload["PERSON_LIST"] = search_string

                self.result_file = requests.post(self.url, data = self.payload)
                result = self.process_results(heat_report, rounds)
                # if this competitor made the finals, we are done with this heat
                if result == "Finals":
                    break
                
        heat_result = Heat_Result()
        heat_result.set_title(heat_report["info"])
        for e in heat_report["entries"]:
            if e["result"] is not None:
                ent_result = Entry_Result()
                ent_result.set_couple(e["dancer"] + " and " + e["partner"])
                ent_result.set_place(str(e["result"]))
                ent_result.set_points(e["points"])
                heat_result.set_next_entry(ent_result.entry)
        
        self.output_file.save_heat(heat_result.heat)

