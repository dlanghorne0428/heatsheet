import requests

from couple import Couple
from dancer import Dancer
from heat import Heat, Heat_Report
from heatlist import Heatlist


def get_name(line):
    first_space_pos = line.find(" ")
    return line[first_space_pos+1:] + ", " + line[:first_space_pos]  

def get_partner(line):
    if "class='partner'" in line:
        start_pos = line.find("with ") + len("with ")
        return line[start_pos:-1]
    else:
        return None


class CompOrgHeat(Heat):
    def __init__(self, items="", item_index=0, dancer=None, partner=None, category="", number=0):
        super().__init__()
        if len(category) > 0:
            self.category = category
        if number != 0:
            self.heat_number = number
        if len(items) > 0:
            start_pos = items[item_index].find("-sess") + len("-sess") + 2
            self.session = items[item_index][start_pos:]
            start_pos = items[item_index+1].find("-heat") + len("-heat") + 2      
            number_string = items[item_index+1][start_pos:]
            index = 0
            while not (number_string[index].isdigit()):
                index += 1
                if index == len(number_string):
                    break
            try:
                self.heat_number = int(number_string[index:])
            except:
                if index == len(number_string):
                    self.extra = number_string
                else:
                    end_index = index
                    while number_string[end_index].isdigit():
                        end_index += 1
                    self.heat_number = int(number_string[index:end_index])
                    self.extra = number_string[end_index:]
            start_pos = items[item_index+2].find("-time") + len("-time") + 2
            self.time = items[item_index+2][start_pos:] 
            start_pos = items[item_index+3].find("-numb") + len("-numb") + 2
            self.shirt_number = items[item_index+3][start_pos:]             
            start_pos = items[item_index+4].find("-desc") + len("-desc") + 2
            self.info = items[item_index+4][start_pos:]
            #print(self.session, self.heat_number, self.time, self.shirt_number, self.info)
            if "Professional" in self.info:
                self.category = "Pro heat"
                self.set_level()
            elif "Formation" in self.info:
                self.category = "Formation"
                print("Formation")
            elif "Solo Star" in self.info:
                self.category = "Heat"
                print("Solo Star")
            elif "Solo" in self.info:
                self.category = "Solo"        
            self.dancer = dancer.name
            self.code = dancer.code
            self.partner = partner
        
    
class CompOrgDancer(Dancer):
    def __init__(self, line):
        super().__init__()
        
        # find the ID code for this dancer
        start_pos = line.find('"id":"') + len('"id":"')
        end_pos = line.find('"', start_pos)
        self.code = line[start_pos:end_pos]
        
        # find the dancer's name
        start_pos = line.find('"name":"') + len('"name":"')
        end_pos = line.find('"', start_pos)        
        self.name = get_name(line[start_pos:end_pos])
        

class CompOrgHeatlist(Heatlist):
    
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
        items = heat_data.split("</td>")
        if len(items) <= 1:
            print("Error parsing heat")
        item_index = 0
        while item_index < len(items):
            p = get_partner(items[item_index])
            if p is not None:
                partner = p
                print(dancer.name, "and", partner)
                item_index += 1
                couple = Couple(dancer.name, partner)
                new_couple = True  # assume this is a new couple
                for c in self.couples:
                    if couple.same_names_as(c):
                        new_couple = False
                        couple = c   # set the couple variable to the existing couple object
                        break
                #if this actually is a new couple, add them to the couples list
                if new_couple:
                    self.couples.append(couple)                    
            elif "heatlist-sess" in items[item_index]:
                h = CompOrgHeat(items, item_index, dancer, partner)
                item_index += 5
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
            else:
                item_index += 1  
            
            
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
        #extract comp name from URL
        response = requests.get(url)
        lines = response.text.splitlines()
        for l in lines:
            if "var cmid" in l:
                # this line is in this format"
                # var cmid = "beachbash2019";
                # extract the name from between the quotes
                self.comp_name = l.split('= "')[1][:-2]
                print(comp_name)
                break
        # TODO: need to build this URL
        end_pos = url.find("/pages")
        
        
        base_url = url[:end_pos] + "/scripts/heatlist_scrape.php?comp=" + comp_name
        print(base_url)
        response = requests.get(base_url)
        competitors = response.text.split("},")
        for c in range(len(competitors) - 1):
            start_pos = competitors[c].find('"id')
            d = CompOrgDancer(competitors[c][start_pos:])#
            try:
                code_num = int(d.code)
                if d.code != "0":
                    self.dancers.append(d)    
            except:
                print("Invalid competitor", d.name, d.code)
        
        for d in self.dancers:
            url = base_url + "&competitor=" + d.code
            response = requests.get(url)
            self.get_heats_for_dancer(d, response.text)            
        
        self.formations.sort()
        self.solos.sort()
        self.age_divisions.sort()        

            
'''Main program'''
if __name__ == '__main__':
    heat_list = CompOrgHeatlist()
    heat_list.open("https://www.californiaopen.com/pages/heat_list/Default.asp")
    #heat_list.open("https://www.ballroombeachbash.com/pages/heatlists/Default.asp")