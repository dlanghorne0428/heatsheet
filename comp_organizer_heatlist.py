import requests

from couple import Couple
from dancer import Dancer
from heat import Heat, Heat_Report
from heatlist import Heatlist


def get_name(line):
    '''This method converts the dancer's name into last, first format.'''
    first_space_pos = line.find(" ")
    return line[first_space_pos+1:] + ", " + line[:first_space_pos]  

def get_partner(line):
    '''This method searches for the partner's name on the given line.'''
    if "class='partner'" in line:
        start_pos = line.find("with ") + len("with ")
        substr = line[start_pos:]
        stripped = substr.strip()
        return stripped
        #return line[start_pos:-1]
    else:
        return None


class CompOrgHeat(Heat):
    '''
    This is a derived class for reading Heat information from a website in CompOrganizer format.
    It derives from the generic Heat class and presents the same interface.
    Only the constructor that reads in the information is unique.
    '''
    def __init__(self, items="", item_index=0, dancer=None, partner=None, category="", number=0):
        super().__init__()
        if len(category) > 0:
            self.category = category
        if number != 0:
            self.heat_number = number
        if len(items) > 0:
            # parse the info from the item list, starting with the session 
            start_pos = items[item_index].find("-sess") + len("-sess") + 2
            self.session = items[item_index][start_pos:]
            
            # get the heat number string and convert it to an integer
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
                # split out extra non-digit info from the heat number
                if index == len(number_string):
                    self.extra = number_string
                else:
                    end_index = index
                    while number_string[end_index].isdigit():
                        end_index += 1
                    self.heat_number = int(number_string[index:end_index])
                    self.extra = number_string[end_index:]
                    
            # save the heat time, determine if there are multiple rounds
            start_pos = items[item_index+2].find("-time") + len("-time") + 2
            heat_time = items[item_index+2][start_pos:] 
            if "<br>" in heat_time:
                time_fields = heat_time.split("<br>")
                if len(time_fields) == 4:
                    self.rounds = "Q"  # start with quarter-final
                else:
                    self.rounds = "S"  # start with semi-final            
                self.time = time_fields[0] + "-" + self.rounds  # truncate "Later rounds" from time string
            else:
                self.time = heat_time + "-" + self.rounds
            
            # save the shirt number and heat description information
            self.shirt_number = items[item_index+3][start_pos:]             
            start_pos = items[item_index+4].find("-desc") + len("-desc") + 2
            self.info = items[item_index+4][start_pos:]
            
            # update the heat category and level if necessary
            if "Professional" in self.info:
                self.category = "Pro heat"
            elif "Formation" in self.info:
                self.category = "Formation"
                print("Formation")
            elif "Solo Star" in self.info:
                self.category = "Heat"
                print("Solo Star")
            elif "Solo" in self.info:
                self.category = "Solo"  
            self.set_level()
            
            # save dancer name, scoresheet code, and partner name
            self.dancer = dancer.name
            self.code = dancer.code
            self.partner = partner
        
    
class CompOrgDancer(Dancer):
    '''
    This is a derived class for reading Dancer information from a website in CompOrganizer format.
    It derives from the generic Dancer class and presents the same interface.
    Only the constructor that reads in the information is unique.
    '''    
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
    '''
    This is a derived class for reading Heatlist information from a website in CompOrganizer format.
    It derives from the generic Heatlist class and presents the same interface.
    '''     
    def __init__(self):
        '''This method initializes the class'''
        super().__init__()
        self.base_url = None
        

    def get_age_division(self, line):
        '''
        This method looks for an age division on the given line. 
        Return it or None if no age division found
        '''
        prefixes = ("L-", "G-", "AC-", "Professional", "AM/AM", "Amateur", "Youth", "MF-", "M/F")  # valid prefixes for division
        return super().get_age_division(line, prefixes)
    
        
    def get_heats_for_dancer(self, dancer, heat_data):
        '''
        This method extracts heat information from the heat_data read in from a URL.
        The information is saved into the specified dancer object.
        '''
        # all the heat information is in a series of table data cells.
        # split them into a list
        items = heat_data.split("</td>")
        if len(items) <= 1:
            print("Error parsing heat")
        item_index = 0
        # process all the list items
        while item_index < len(items):
            # check if this item specifies a partner name
            p = get_partner(items[item_index])
            if p is not None:
                partner = p
                #print(dancer.name, "and", partner)
                # partner found, go to next item
                item_index += 1
                # create a couple object for this dancer and partner 
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
            # no partner, check if this item has the start of a new heat
            elif "heatlist-sess" in items[item_index]:
                # build heat object, which takes up the next five items
                h = CompOrgHeat(items, item_index, dancer, partner)
                item_index += 5

                if h.category == "Formation":
                    # special processing for formation heats
                    self.formations.append(h)
                    self.max_formation_num = max(h.heat_number, self.max_formation_num)
                elif h.category == "Solo":
                    # special processing for solo heats
                    if h not in self.solos:
                        self.solos.append(h)
                        self.max_solo_num = max(h.heat_number, self.max_solo_num)
                
                # determine if this heat indicates a new age division
                age = self.get_age_division(h.info)
                if age is not None:
                    self.add_age_division(age)
                    dancer.add_age_division(age)
                    couple.add_age_division(age)
                    # update the maximum heat numbers
                    if age == "Professional":
                        self.max_pro_heat_num = max(h.heat_number, self.max_pro_heat_num)
                    else:
                        self.max_heat_num = max(h.heat_number, self.max_heat_num)
                        if h.multi_dance():
                            self.add_multi_dance_heat(h.heat_number)                       
                
                # add this heat to both the dancer and couple objects
                dancer.add_heat(h)
                couple.add_heat(h)
             
            else:
                # try the next item
                item_index += 1  
            
    
    def get_next_dancer(self, index):
        '''This method reads the heat information for the dancer at the given index.'''
        d = self.dancers[index]
        url = self.base_url + "&competitor=" + d.code
        response = requests.get(url)
        self.get_heats_for_dancer(d, response.text)
        return d.name
            
    
    def complete_processing(self):
        '''
        This method sorts data structures after all the heat information 
        has been obtained from the website.
        '''
        self.formations.sort()
        self.solos.sort()
        self.age_divisions.sort()   
        self.multi_dance_heat_numbers.sort()
        
        
    def open(self, url):
        '''
        This method obtains the name of the competition and a list of all the dancers.
        '''
        #extract comp name from URL
        response = requests.get(url)
        lines = response.text.splitlines()
        for l in lines:
            if "var cmid" in l:
                # this line is in this format"
                # var cmid = "beachbash2019";
                # extract the name from between the quotes
                self.comp_name = l.split('= "')[1][:-2]
                #print(self.comp_name)
                break

        end_pos = url.find("/pages")        

        # save this string for later use
        self.base_url = url[:end_pos] + "/scripts/heatlist_scrape.php?comp=" + self.comp_name
        #print(self.base_url)
        
        # open the base URL to extract a list of dancers
        response = requests.get(self.base_url)
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
        
       
            
'''Main program'''
if __name__ == '__main__':
    heat_list = CompOrgHeatlist()
    #heat_list.open("https://www.californiaopen.com/pages/heat_list/Default.asp")
    heat_list.open("https://www.ballroombeachbash.com/pages/heatlists/Default.asp")