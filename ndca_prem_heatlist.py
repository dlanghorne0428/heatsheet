import requests

from couple import Couple
from dancer import Dancer
from heat import Heat, Heat_Report
from heatlist import Heatlist


def get_name(line):
    first_space_pos = line.find(" ")
    return line[first_space_pos+1:] + ", " + line[:first_space_pos]  

def get_partner(line):
    if 'partner-name' in line:
        start_pos = line.find("With ") + len("With ")
        return get_name(line[start_pos:-5])
    else:
        return None


class NdcaPremHeat(Heat):
    def __init__(self, line="", dancer=None, partner=None, category="", number=0):
        super().__init__()
        if len(category) > 0:
            self.category = category
        if number != 0:
            self.heat_number = number
        if len(line) > 0:
            cols = line.split("</td>")
            start_pos = cols[0].find("-sess") + len("-sess") + 2
            self.session = cols[0][start_pos:]
            start_pos = cols[2].find("-time") + len("-time") + 2
            self.time = cols[2][start_pos:]
            start_pos = cols[1].find("-heat") + len("-heat") + 2      
            number_string = cols[1][start_pos:]
            try:
                self.heat_number = int(number_string)
            except:
                index = 0
                while number_string[index].isdigit():
                    index += 1
                self.heat_number = int(number_string[:index])
                self.extra = number_string[index:]
            start_pos = cols[3].find("-desc") + len("-desc") + 2
            self.info = cols[3][start_pos:]
            if "Professional" in self.info:
                self.category = "Pro heat"
                self.set_level()
            elif "Formation" in self.info:
                self.category = "Formation"
            elif "Solo Star" in self.info:
                self.category = "Heat"
            elif "Solo" in self.info:
                self.category = "Solo"        
            self.dancer = dancer.name
            self.code = dancer.code
            self.partner = partner
        
    
class NdcaPremDancer(Dancer):
    def __init__(self, line):
        super().__init__()
        
        # find the dancer's name
        fields = line.split(">")
        self.name = get_name(fields[1])
        
        # find the ID code for this dancer
        pos = fields[0].find("competitor=") + len("competitor=")
        self.code = fields[0][pos+1:-1]
        

class NdcaPremHeatlist(Heatlist):
    
    def __init__(self):
        super().__init__()
        
        
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
    
        
    # look for an age division on the given line. Return it or None if no age division found
    def get_age_division(self, line):
        prefixes = ("L-", "G-", "AC-", "Professional", "AM/AM", "Amateur", "Youth", "MF-", "M/F")  # valid prefixes for division
        return super().get_age_division(line, prefixes)
    
        
    def get_heats_for_dancer(self, dancer, heat_data):
        fields = heat_data.split("</div>")
        # isolate the list of heats
        if len(fields) == 5:
            rows = fields[3].split("</tr>")
            if len(rows) <= 1:
                print("Error parsing heat rows")
            row_index = 0
            while row_index < len(rows) - 1:
                p = get_partner(rows[row_index])
                if p is not None:
                    partner = p
                    # skip row with headings
                    row_index += 1
                    couple = Couple(dancer.name, partner)
                    new_couple = True  # assume this is a new couple
                    for c in self.couples:
                        if couple.same_names_as(c):
                            new_couple = False
                            couple = c   # set the couple variable to the existing couple object
                            break
                    # if this actually is a new couple, add them to the couples list
                    if new_couple:
                        self.couples.append(couple)                    
                elif "heatlist-sess" in rows[row_index]:
                    h = NdcaPremHeat(rows[row_index], dancer, partner)
                    if h.category == "Formation":
                        self.formations.append(h)
                        self.max_formation_num = max(h.heat_number, self.max_formation_num)
                    elif h.category == "Solo":
                        if h not in self.solos:
                            self.solos.append(h)
                            self.max_solo_num = max(h.heat_number, self.max_solo_num)
                    age = self.get_age_division(h.info)
                    if age is not None:
                        self.add_age_division(age)
                        dancer.add_age_division(age)
                        couple.add_age_division(age)
                        if age == "Professional":
                            self.max_pro_heat_num = max(h.heat_number, self.max_pro_heat_num)
                        else:
                            self.max_heat_num = max(h.heat_number, self.max_heat_num)
                    dancer.add_heat(h)
                    couple.add_heat(h)
                    
                row_index += 1
    
        else:
            print("Error parsing heat data")   
            
            
    # given a heat, this method returns a heat report, which is a list of 
    # all entries in the heat. This list can optionally be sorted by shirt number
    def build_heat_report(self, heat, heat_name_only=False, sorted=False):
        report = Heat_Report()
        for c in self.couples:
            for ht in c.heats:
                if heat == ht:
                    report.append(ht)
                    if heat_name_only:
                        return report
        if sorted:
            report.sort()
        return report    
            
        
    def open(self, url):
        #extract comp name and comp_id from URL
        start_pos = url.find("cyi=") + len("cyi=")
        comp_id = url[start_pos:]
        self.comp_name = self.get_comp_name(comp_id)
        url = "http://www.ndcapremier.com/scripts/competitors.asp?cyi=" + comp_id
        response = requests.get(url)
        competitors = response.text.split("</a>")
        for c in range(len(competitors) - 1): 
            if 'class="team"' in competitors[c]: 
                #print(c)
                continue
            d = NdcaPremDancer(competitors[c])
            #print(d.name, d.code)
            try:
                code_num = int(d.code)
                url = "http://ndcapremier.com/scripts/heatlists.asp?cyi=" + comp_id + "&id=" + d.code + "&type=competitor"
                response = requests.get(url)
                self.get_heats_for_dancer(d, response.text)
                self.dancers.append(d)
                
            except:
                print("Invalid competitor", d.name, d.code)
        
        self.formations.sort()
        self.solos.sort()
        self.age_divisions.sort()        

            
'''Main program'''
if __name__ == '__main__':
    heat_list = NdcaPremHeatlist()
    heat_list.open("http://www.ndcapremier.com/heatlists.htm?cyi=748")