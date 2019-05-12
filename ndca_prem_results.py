import requests
from calc_points import calc_points
from heat import Heat, Heat_Report
from ndca_prem_heatlist import get_name

class NdcaPremEvent():
    def __init__(self, line):
        fields = line.split(">")
        # extract the event id for future use
        start_pos = fields[0].find("eventid=") + len("eventid=") + 1
        self.id = fields[0][start_pos:-1]
        # extract the event name
        self.name = fields[1]
        
        
class NdcaPremResults():
    
    def __init__(self):
        self.categories = []
        self.comp_id = None
        self.events = []
        
        
    def get_comp_name(self, comp_id):
        url = "http://www.ndcapremier.com/scripts/compyears.asp?cyi=" + comp_id
        response = requests.get(url)
        lines = response.text.splitlines()
        for l in lines:
            start_pos = l.find("<comp_name>")
            if start_pos > -1:
                start_pos += len("<comp_name>")
                end_pos = l.find("</comp_name>")
                comp_name = l[start_pos:end_pos]
                break
        return comp_name
    
    
    def process_scoresheet_for_event(self, heat_report, event_id):
        looking_for_final_round = True
        looking_for_final_summary = False
        looking_for_final_dance = False
        looking_for_result_column = False
        looking_for_recall_column = False
        looking_for_finalists = False
        looking_for_quarterfinal = False
        process_finalists = False
        looking_for_semifinal = False
        url = "http://www.ndcapremier.com/scripts/results.asp?cyi=" + self.comp_id + "&event=" + event_id
        # this should be based on event id
        num_dances = heat_report.description().count(",") + 1
        
        response = requests.get(url)
        lines = response.text.splitlines()
        i = 0
        while i < len(lines): 
            l = lines[i]
            if looking_for_final_round:
                if 'class="roundHeader"' in l:
                    #print(l)
                    looking_for_final_summary = True
                    looking_for_final_round = False
                else:
                    i += 1
            elif looking_for_final_summary:
                if "Final Summary" in l:
                    #print(l)
                    looking_for_final_summary = False
                    looking_for_result_column = True
                    col_count = 0
                else:
                    i += 1
            elif looking_for_result_column:
                fields = l.split("</th>")
                col_count += len(fields) - 1
                if "Final Result" in l:
                    #print("Result Column is ", col_count)
                    looking_for_result_column = False
                    looking_for_finalists = True
                else:
                    i += 1
            elif looking_for_recall_column:
                fields = l.split("</th>")
                recall_column = len(fields) - 2
                accum_column = recall_column - 1
                #print("Recall Column is ", recall_column)
                i += 1
                looking_for_recall_column = False
                looking_for_eliminations = True
            elif looking_for_finalists:
                # skip the first field, it is not a row
                rows = fields[-1].split("</tr>")[1:]
                if "</table>" in rows[-1]:
                    rows = rows[:-1]
                    looking_for_finalists = False
                    looking_for_semifinal = True
                else:
                    i += 1
                for r in rows: 
                    fields = r.split("</td>")
                    couple_field = fields[0].split("<td>")[1]
                    result_place = int(fields[col_count-1].split("<td>")[1])
                    sub_fields = couple_field.split(" &amp; ")
                    first_space = sub_fields[0].find(" ")
                    shirt_number = sub_fields[0][:first_space]
                    dancer = get_name(sub_fields[0][first_space+1:])
                    partner = get_name(sub_fields[1])
                    for index in range(heat_report.length()):
                        entry = heat_report.entry(index)
                        if entry.dancer == dancer:
                            entry.shirt_number = shirt_number
                            entry.result = result_place
                            break
                        elif entry.partner == dancer:
                            entry.swap_names()
                            entry.shirt_number = shirt_number
                            entry.result = result_place
                            break
                    else:
                        h = heat_report.build_late_entry()
                        h.dancer = dancer
                        h.partner = partner
                        h.shirt_number = shirt_number
                        h.result = result_place
                        h.code = "LATE"
                        heat_report.append(h)
            elif looking_for_semifinal:
                if 'class="roundHeader"' in l:
                    print("Found semi-final")
                    heat_report.set_rounds("S")
                    looking_for_semifinal = False
                    looking_for_final_dance = True
                    dance_count = 0
                else:
                    i += 1            
            elif looking_for_final_dance:
                if 'class="eventResults"' in l:
                    dance_count += 1
                if dance_count == num_dances:
                    #print(l)
                    looking_for_final_dance = False
                    looking_for_recall_column = True
                i += 1
            elif looking_for_eliminations:
                if "</table>" in l:
                    looking_for_eliminations = False
                else:
                    fields = l.split("</td>")
                    couple_field = fields[0].split("<td>")[1]
                    recall_place = fields[recall_column].split("<td>")[1]
                    if recall_place != "Recall":
                        accum_value = fields[accum_column].split("<td>")[1]
                        sub_fields = couple_field.split(" &amp; ")
                        first_space = sub_fields[0].find(" ")
                        shirt_number = sub_fields[0][:first_space]
                        dancer = get_name(sub_fields[0][first_space+1:])
                        partner = get_name(sub_fields[1])
                        for index in range(heat_report.length()):
                            entry = heat_report.entry(index)
                            if entry.dancer == dancer:
                                entry.shirt_number = shirt_number
                                entry.result = "Semis"
                                entry.points = calc_points(entry.level, -2, rounds="S", accum=int(accum_value))
                                break
                            elif entry.partner == dancer:
                                entry.swap_names()
                                entry.shirt_number = shirt_number
                                entry.result = "Semis"   
                                entry.points = calc_points(entry.level, -2, rounds="S", accum=int(accum_value))
                                break                        
                        else:
                            h = heat_report.build_late_entry()
                            h.dancer = dancer
                            h.partner = partner
                            h.shirt_number = shirt_number
                            h.result = "Semis"
                            h.code = "LATE"
                            h.points = calc_points(h.level, -2, rounds="S", accum=int(accum_value))
                            heat_report.append(h)
                    i += 1
            else:
                i+= 1

        
        total_entries = heat_report.length()        
        for index in range(heat_report.length()):
            e = heat_report.entry(index)
            if e.result is None:
                total_entries -= 1
                e.rounds = heat_report.rounds()
        for index in range(heat_report.length()):
            e = heat_report.entry(index)
            if e.points is None and e.result is not None:
                e.points = calc_points(e.level, e.result, num_competitors=total_entries, rounds=heat_report.rounds())
#            print(e.dancer, "and", e.partner, "finish", e.result, "for", e.points, "points")    
                
    
    
    def determine_heat_results(self, heat_report):
        event_name = heat_report.description()
        for e in self.events:
            if e.name == event_name:
#                print("Found", e.name)
                self.process_scoresheet_for_event(heat_report, e.id)
                

    def open(self, url):
        #extract comp name and comp_id from URL
        start_pos = url.find("cyi=") + len("cyi=")
        self.comp_id = url[start_pos:]
        self.comp_name = self.get_comp_name(self.comp_id)
        url = "http://www.ndcapremier.com/scripts/event_categories.asp?cyi=" + self.comp_id
        response = requests.get(url)
        categories = response.text.split("</a>")
        for cat_link in categories:
            if len(cat_link) > 0:
                start_pos = cat_link.find("style=") + len("style=") + 1
                end_pos = cat_link.find('">', start_pos)
                category = cat_link[start_pos:end_pos]
                # this limits the result processing to pro events
                #if "Professional" in category:
                self.categories.append(category)
        for cat in self.categories:
            url = "http://www.ndcapremier.com/scripts/event_list.asp?cyi=" + self.comp_id + "&cat=" + cat
            response = requests.get(url)
            event_lines = response.text.split("</a>")
            for e in event_lines:
                if len(e) > 0:
                    event = NdcaPremEvent(e)
                    self.events.append(event)
                    
    def close(self):
        pass


if __name__ == '__main__':
    results = NdcaPremResults()
    results.open("http://www.ndcapremier.com/results.htm?cyi=748")
    h = Heat()
    h.info = "Professional Open Championships  Amer. Smooth Championship (W,T,F,VW)" #"Professional Open Championships  Int'l Ballroom Championship (W,T,VW,F,Q)"
    h.set_category("Pro heat")
    h.set_level()
    h.dancer = "McCann, Stephen" #"Alitto, Oreste"
    h.partner = "McCann, Elisa" # "Belozerova, Valeriia"
    h.rounds = "F"
    hr = Heat_Report()
    hr.append(h)
    results.determine_heat_results(hr)
    print("Results Processed")
#    results.determine_heat_results("Professional Rising Star Events Amer. Rhythm (CC,R,SW,B,M)")
#    results.determine_heat_results("Professional Rising Star Events Int'l Ballroom (W,T,VW,F,Q)")
#    results.determine_heat_results("Professional Rising Star Events Int'l Latin (CC,S,R,PD,J)")
     # this heat had a semi final
#    results.determine_heat_results("Professional Open Championships  Int'l Ballroom Championship (W,T,VW,F,Q)")
#    results.determine_heat_results("Professional Open Championships  Amer. Rhythm Championship (CC,R,SW,B,M)")
#    results.determine_heat_results("Professional Open Championships  Int'l Latin Championship (CC,S,R,PD,J)")	    
#    results.determine_heat_results("Professional Open Championships  Amer. Smooth Championship (W,T,F,VW)")	
#    results.determine_heat_results("Professional Open Championships  Show Dance Championship (SD)")  