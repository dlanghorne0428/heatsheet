import requests

# This class parses the scoresheet and extract results of the competition
class CompMngrScoresheet():

    def __init__(self):
        self.payload = dict()
        self.url = ""
        self.point_values = {
           "Open": [0, 20, 15, 12, 9, 7, 5, 3, 3, 3, 3, 3],
           "Rising Star": [0, 10, 7, 5, 3, 2, 1, 1, 1, 1, 1],
           "Novice": [0,  5, 4, 3, 2, 1, 1, 1, 1, 1, 1]
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
            
            
    def open_scoresheet(self, url):
        r = requests.get(url)
        line_list = r.text.splitlines()
        for line in line_list:
            if "<form" in line:
                self.find_url(line)
            if "<input" in line:
                self.find_payload_field(line)
                
        # should save the file 
        
                
    def open_scoresheet_from_file(self, filename):
        # open the file and loop through all the lines
        fhand = open(filename,encoding="utf-8")
        for line in fhand:
            if "<form" in line:
                self.find_url(line)
            if "<input" in line:
                self.find_payload_field(line)
        print(self.payload["COMP_NAME"])
            
    def get_table_data(self, line):
        start_pos = line.find("<td>") + len("<td>")
        end_pos = line.find("<", start_pos)
        name = line[start_pos:end_pos]
        return name    

    def process_results(self, heat_report):
        lines = self.result_file.text.splitlines()
        heat_string = heat_report["category"] + " " + str(heat_report["number"]) + ":"
        
        if "(" in heat_report["info"] and ")" in heat_report["info"]:
            event = "Multi-Dance"
        else:
            event = "Single Dance"
            
        if "Open" in heat_report["info"]:
            level = "Open"
        elif "Novice" in heat_report["info"]:
            level = "Novice"
        else:
            level = "Rising Star"
            
        # these are state variables
        looking_for_result_column = False
        looking_for_competitors = False
        result = None
 
        for line in lines:
            if looking_for_result_column:
                if "<tr>" in line:
                    count = 0
                elif "<td>" in line and "Result" in line:
                    result_column = count
                    looking_for_competitors = True
                    looking_for_result_column = False
                    count = 0
                elif "<td>" in line:
                    count += 1
            elif looking_for_competitors:
                if "<td>" in line:
                    if count == 0:
                        current_competitor = self.get_table_data(line)
                        count += 1
                    elif count == result_column:
                        # need to check for parenthesis, as the result could include a tiebreaker rule
                        result_place = int(self.get_table_data(line).split('(')[0])
                        for e in heat_report["entries"]:
                            if current_competitor.startswith(e["shirt"]):
                                e["result"] = result_place
                                e["points"] = self.point_values[level][result_place]
                                break
                        count = 0
                    else:
                        count += 1
                elif "</table>" in line:
                    looking_for_competitors = False
                    break;
                
            elif heat_string in line and "Quarter-final" in line and "<p>" in line:
                result = "quarters"
            elif heat_string in line and "Semi-final" in line and "<p>" in line:
                result = "Semis"
            elif heat_string in line and "Final" in line and "<p>" in line:
                result = "Finals"
                if event == "Single Dance":
                    looking_for_result_column = True
            elif result == "Finals" and "Final summary" in line and "<p>" in line:
                if event == "Multi-Dance":
                    looking_for_result_column = True    
        
        return result


    def perform_request_for_results(self, heat_report):
        print(heat_report["category"], heat_report["number"], heat_report["info"])
        for entry in heat_report["entries"]:
            if entry["result"] is None:
                search_string = entry["code"] + "=" + entry["dancer"]
                self.payload["PERSON_LIST"] = search_string 

                self.result_file = requests.post(self.url, data = self.payload)
                result = self.process_results(heat_report)
                if result != "Finals":
                    entry["result"] = result
                 
        for e in heat_report["entries"]:
            if e["result"] is not None:
                print(e["dancer"] + " and " + e["partner"] + '\t' + str(e["result"]) + "\t" + str(e["points"]))  
                
        print()





