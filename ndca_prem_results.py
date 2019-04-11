import requests

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
        self.finalists = []
        
        
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
    
    
    def process_scoresheet_for_event(self, event_id):
        looking_for_final_round = True
        looking_for_final_summary = False
        looking_for_result_column = False
        looking_for_finalists = False
        process_finalists = False
        url = "http://www.ndcapremier.com/scripts/results.asp?cyi=" + self.comp_id + "&event=" + event_id
        response = requests.get(url)
        lines = response.text.splitlines()
        i = 0
        while i < len(lines):  #        for l in lines:
            l = lines[i]
            if looking_for_final_round:
                if 'class="roundHeader"' in l:
                    print(l)
                    looking_for_final_summary = True
                    looking_for_final_round = False
                else:
                    i += 1
            elif looking_for_final_summary:
                if "Final Summary" in l:
                    print(l)
                    looking_for_final_summary = False
                    looking_for_result_column = True
                    col_count = 0
                else:
                    i += 1
            elif looking_for_result_column:
                fields = l.split("</th>")
                col_count += len(fields) - 1
                print(col_count)
                if "Final Result" in l:
                    print("Result Column is ", col_count)
                    looking_for_result_column = False
                    looking_for_finalists = True
                else:
                    i += 1
            elif looking_for_finalists:
                # skip the first field, it is not a row
                rows = fields[-1].split("</tr>")[1:]
                if "</table>" in rows[-1]:
                    rows = rows[:-1]
                    looking_for_finalists = False
                    process_finalists = True
                else:
                    i += 1
                for r in rows: 
                    self.finalists.append(r)
            elif process_finalists:
                for f in self.finalists:
                    fields = f.split("</td>")
                    print(fields[0], fields[col_count-1]) 
                i += 1
                    
                
                
                
    
    
    def determine_heat_results(self, event_name):
        for e in self.events:
            if e.name == event_name:
                print("Found", e.name)
                self.process_scoresheet_for_event(e.id)
                

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
                if "Professional" in category:
                    self.categories.append(category)
        for cat in self.categories:
            url = "http://www.ndcapremier.com/scripts/event_list.asp?cyi=" + self.comp_id + "&cat=" + cat
            response = requests.get(url)
            event_lines = response.text.split("</a>")
            for e in event_lines:
                if len(e) > 0:
                    event = NdcaPremEvent(e)
                    self.events.append(event)


if __name__ == '__main__':
    results = NdcaPremResults()
    results.open("http://www.ndcapremier.com/results.htm?cyi=748")
    results.determine_heat_results("Professional Rising Star Events Amer. Smooth (W,T,F,VW)")