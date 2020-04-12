from season_ranking import RankingDataFile, get_name
from datetime import date
from enum import Enum
import json

class Dancer_Type(Enum):
    '''Enumrate the different types of dancers.'''
    PRO = 1
    ADULT_STUDENT = 2
    JUNIOR_STUDENT = 3
    ADULT_AMATEUR = 4
    JUNIOR_AMATEUR = 5


class Dancer_List():
    '''This class creates a list of names for a specific Dancer_Type by reading the appropriate
       ranking data files.'''
    def __init__(self, dancer_type=Dancer_Type.PRO):

        self.names = list()
        self.couples = list()
        folder_name = "./data/" + str(date.today().year)
        if dancer_type == Dancer_Type.PRO: 
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Pro/smooth_rankings.json"))
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Pro/rhythm_rankings.json"))
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Pro/standard_rankings.json"))
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Pro/latin_rankings.json"))
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Pro/cabaret_showdance_rankings.json"))
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Pro/nightclub_rankings.json"))
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Pro/country_rankings.json"))
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Pro-Am/smooth_rankings.json"))
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Pro-Am/rhythm_rankings.json"))
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Pro-Am/standard_rankings.json"))
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Pro-Am/latin_rankings.json"))
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Pro-Am/nightclub_rankings.json"))
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Pro-Am/country_rankings.json"))
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Jr.Pro-Am/smooth_rankings.json"))
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Jr.Pro-Am/rhythm_rankings.json"))
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Jr.Pro-Am/standard_rankings.json"))
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Jr.Pro-Am/latin_rankings.json"))  
            print("Total number of professionals:", len(self.names))
        elif dancer_type == Dancer_Type.ADULT_STUDENT:  
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Pro-Am/smooth_rankings.json"), Dancer_Type.ADULT_STUDENT)
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Pro-Am/rhythm_rankings.json"), Dancer_Type.ADULT_STUDENT)
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Pro-Am/standard_rankings.json"), Dancer_Type.ADULT_STUDENT)
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Pro-Am/latin_rankings.json"), Dancer_Type.ADULT_STUDENT)
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Pro-Am/nightclub_rankings.json"), Dancer_Type.ADULT_STUDENT)
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Pro-Am/country_rankings.json"), Dancer_Type.ADULT_STUDENT)       
            print("Total number of adult students:", len(self.names))        
        elif dancer_type == Dancer_Type.JUNIOR_STUDENT:  
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Jr.Pro-Am/smooth_rankings.json"), Dancer_Type.JUNIOR_STUDENT)
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Jr.Pro-Am/rhythm_rankings.json"), Dancer_Type.JUNIOR_STUDENT)
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Jr.Pro-Am/standard_rankings.json"), Dancer_Type.JUNIOR_STUDENT)
            self.add_single_name(RankingDataFile(folder_name + "/Rankings/Jr.Pro-Am/latin_rankings.json"), Dancer_Type.JUNIOR_STUDENT)      
            print("Total number of junior students:", len(self.names))
        elif dancer_type == Dancer_Type.ADULT_AMATEUR:  
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Amateur/smooth_rankings.json"), Dancer_Type.ADULT_AMATEUR)
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Amateur/rhythm_rankings.json"), Dancer_Type.ADULT_AMATEUR)
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Amateur/standard_rankings.json"), Dancer_Type.ADULT_AMATEUR)
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Amateur/latin_rankings.json"), Dancer_Type.ADULT_AMATEUR)
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Amateur/nightclub_rankings.json"), Dancer_Type.ADULT_AMATEUR)     
            print("Total number of adult amateurs:", len(self.names))     
        elif dancer_type == Dancer_Type.JUNIOR_AMATEUR:  
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Jr.Amateur/smooth_rankings.json"), Dancer_Type.JUNIOR_AMATEUR)
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Jr.Amateur/rhythm_rankings.json"), Dancer_Type.JUNIOR_AMATEUR)
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Jr.Amateur/standard_rankings.json"), Dancer_Type.JUNIOR_AMATEUR)
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Jr.Amateur/latin_rankings.json"), Dancer_Type.JUNIOR_AMATEUR)
            self.add_both_names(RankingDataFile(folder_name + "/Rankings/Jr.Amateur/nightclub_rankings.json"), Dancer_Type.JUNIOR_AMATEUR)     
            print("Total number of junior amateurs:", len(self.names))           
            
        self.names.sort()
        self.couples.sort()
            
        
    def add_both_names(self, data_file, dancer_type=Dancer_Type.PRO):
        '''This method reads one data file and for each couple found, adds both names to the list.'''
        for index in range(data_file.length()):
            couple = data_file.get_couple_at_index(index)
            if couple["name"] not in self.couples:
                self.couples.append(couple["name"])
            new_name = get_name(couple["name"], True)
            if new_name not in self.names:
                self.names.append(new_name)
                
            new_name = get_name(couple["name"], False)
            if new_name not in self.names:
                self.names.append(new_name)        

            
    def add_single_name(self, data_file, dancer_type=Dancer_Type.PRO):
        '''This method reads one data file and for each couple found, adds the dancer name of the desired type to the list.'''
        for index in range(data_file.length()):
            couple = data_file.get_couple_at_index(index)
            if dancer_type == Dancer_Type.PRO:
                flag = False
            else:       # store pro-am couples
                flag = True
                if couple["name"] not in self.couples:
                    self.couples.append(couple["name"])
            new_name = get_name(couple["name"], flag)
            if new_name not in self.names:
                self.names.append(new_name)
                
    
    def index_of_name(self, name):
        try:
            index = self.names.index(name)
            return index
        except:
            return -1
        
                
     
class Dancer_DB_Fixture():
    def __init__(self):
        self.fixture = list()   

    def add_dancers_to_fixture(self, names, dancer_type):
        for name in names:
            fixture_entry = dict()
            fixture_entry["model"] = "rankings.dancer"
            fixture_entry["pk"] = len(self.fixture) + 1
            fixture_entry["fields"] = dict()
            #fixture_entry["fields"]["name"] = name
            name_fields = name.split(",")
            num_names = len(name_fields)
            if num_names == 1:
                fixture_entry["fields"]["name_first"] = "?"
                fixture_entry["fields"]["name_middle"] = ""
                fixture_entry["fields"]["name_last"] = name
            else:
                first_split = name_fields[1].split()
                fixture_entry["fields"]["name_first"] = first_split[0]
                if len(first_split) == 1:
                    fixture_entry["fields"]["name_middle"] = ""
                else:
                    fixture_entry["fields"]["name_middle"] = first_split[1]
                fixture_entry["fields"]["name_last"] = name_fields[0]            
            fixture_entry["fields"]["dancer_type"] = dancer_type
            print(fixture_entry)
            self.fixture.append(fixture_entry)
        
        
    def add_couple_to_fixture(self, couple_name, couple_type, couple_offset,
                              dancer_1_list, dancer_1_offset, dancer_2_list, dancer_2_offset):
        
        fixture_entry = dict()
        dancer_1_name = get_name(couple_name, True)
        dancer_2_name = get_name(couple_name, False)
        dancer_1_key = dancer_1_list.index_of_name(dancer_1_name) + dancer_1_offset
        dancer_2_key = dancer_2_list.index_of_name(dancer_2_name) + dancer_2_offset
        if dancer_1_key > 0 and dancer_2_key > 0:
            fixture_entry["model"] = "rankings.couple"
            fixture_entry["pk"] = len(self.fixture) - couple_offset + 1
            fixture_entry["fields"] = dict()
            fixture_entry["fields"]["dancer_1"] = dancer_1_key
            fixture_entry["fields"]["dancer_2"] = dancer_2_key
            fixture_entry["fields"]["couple_type"] = couple_type            
            print(fixture_entry)
            self.fixture.append(fixture_entry)            
        else:
            print("ERROR", dancer_1_name, dancer_1_key, dancer_2_name, dancer_2_key)
        
    
                       
        
'''Main program'''
if __name__ == '__main__':
    fixture = Dancer_DB_Fixture()
    
    instructor_key_offset = 1
    instructors = Dancer_List(Dancer_Type.PRO)
    pro_couples = instructors.couples
    print("Found", len(pro_couples), "professional couples")

    adult_student_key_offset = instructor_key_offset + len(instructors.names)
    adult_students = Dancer_List(Dancer_Type.ADULT_STUDENT)
    pro_am_couples = adult_students.couples
    print("Found", len(pro_am_couples), "pro-am couples")

    junior_student_key_offset = adult_student_key_offset + len(adult_students.names)
    junior_students = Dancer_List(Dancer_Type.JUNIOR_STUDENT)
    jr_pro_am_couples = junior_students.couples
    print("Found", len(jr_pro_am_couples), "junior pro-am couples")
    
    amateur_key_offset = junior_student_key_offset + len(junior_students.names)
    adult_amateurs = Dancer_List(Dancer_Type.ADULT_AMATEUR)
    adult_amateur_couples = adult_amateurs.couples
    print("Found", len(adult_amateur_couples), "adult amateur couples")
   
    junior_amateur_key_offset = amateur_key_offset + len(adult_amateurs.names)
    junior_amateurs = Dancer_List(Dancer_Type.JUNIOR_AMATEUR)
    junior_amateur_couples = junior_amateurs.couples
    print("Found", len(junior_amateur_couples), "junior amateur couples")    
    
    fixture.add_dancers_to_fixture(instructors.names, "PRO")
    fixture.add_dancers_to_fixture(adult_students.names, "PAS")    
    fixture.add_dancers_to_fixture(junior_students.names, "JRS")  
    fixture.add_dancers_to_fixture(adult_amateurs.names, "AAM") 
    fixture.add_dancers_to_fixture(junior_amateurs.names, "JAM")  
    
    couple_key_offset = junior_amateur_key_offset + len(junior_amateurs.names) - 1

    for c in pro_couples:
        fixture.add_couple_to_fixture(c, "PRC", couple_key_offset, instructors, 1, instructors, 1)   
  
    for c in pro_am_couples:
        fixture.add_couple_to_fixture(c, "PAC", couple_key_offset, adult_students, adult_student_key_offset, instructors, 1)     
   
    for c in jr_pro_am_couples:
        fixture.add_couple_to_fixture(c, "JPC", couple_key_offset, junior_students, junior_student_key_offset, instructors, 1)  

    for c in adult_amateur_couples:
        fixture.add_couple_to_fixture(c, "AMC", couple_key_offset, adult_amateurs, amateur_key_offset, adult_amateurs, amateur_key_offset)  

    for c in junior_amateur_couples:
        fixture.add_couple_to_fixture(c, "JAC", couple_key_offset, junior_amateurs, junior_amateur_key_offset, junior_amateurs, junior_amateur_key_offset)         
    
    fp = open("db_fixture.json", "w", encoding="utf-8")
    json.dump(fixture.fixture, fp, indent=2)     
    fp.close()