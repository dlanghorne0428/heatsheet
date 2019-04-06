import requests

from couple import Couple
from dancer import Dancer
from heat import Heat
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
    def __init__(self, line, dancer, partner=None):
        super().__init__()
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
                        # print("--->", couple.pair_name)
                        self.couples.append(couple)                    
                elif "heatlist-sess" in rows[row_index]:
                    h = NdcaPremHeat(rows[row_index], dancer, partner)
                    age = self.get_age_division(h.info)
                    if age is not None:
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
            
        
    def open(self, comp_id):
        url = "http://www.ndcapremier.com/scripts/competitors.asp?cyi=" + comp_id
        response = requests.get(url)
        competitors = response.text.split("</a>")
        for c in range(len(competitors) - 1):     
            d = NdcaPremDancer(competitors[c])
            print(d.name, d.code)
            try:
                code_num = int(d.code)
                url = "http://ndcapremier.com/scripts/heatlists.asp?cyi=" + comp_id + "&id=" + d.code + "&type=competitor"
                response = requests.get(url)
                self.get_heats_for_dancer(d, response.text)
                self.dancers.append(d)

                for h in d.heats:
                    if h.category == "Formation" or h.category == "Solo":
                        print(h.info_list())
                if len(d.age_divisions) == 0:
                    print(d.name, d.age_divisions)
                    
                # print("Max Pro Heat #:", self.max_pro_heat_num, "Max Heat #:", self.max_heat_num)
                
            except:
                print("Invalid competitor", d.name, d.code)

            

heat_list = NdcaPremHeatlist()
heat_list.open("748")