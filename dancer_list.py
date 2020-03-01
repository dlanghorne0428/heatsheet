from season_ranking import RankingDataFile, get_name
from datetime import date
from enum import Enum

class Dancer_Type(Enum):
    PRO = 1
    ADULT_STUDENT = 2
    JUNIOR_STUDENT = 3
    ADULT_AMATEUR = 4
    JUNIOR_AMATEUR = 5
    
def add_both_names(current_list, data_file, dancer_type=Dancer_Type.PRO):
    for index in range(data_file.length()):
        if dancer_type == Dancer_Type.JUNIOR_AMATEUR and not data_file.is_junior(index):
            continue
        if dancer_type == Dancer_Type.ADULT_AMATEUR and data_file.is_junior(index):
            continue
        couple = data_file.get_couple_at_index(index)
        new_name = get_name(couple["name"], True)
        if new_name not in current_list:
            current_list.append(new_name)
            
        new_name = get_name(couple["name"], False)
        if new_name not in current_list:
            current_list.append(new_name)        
            
    return current_list.sort()

def add_student_names(current_list, data_file, dancer_type=Dancer_Type.PRO):
    for index in range(data_file.length()):
        if dancer_type == Dancer_Type.PRO:
            flag = False
        else:
            flag = True
        if dancer_type == Dancer_Type.JUNIOR_STUDENT and not data_file.is_junior(index):
            continue
        if dancer_type == Dancer_Type.ADULT_STUDENT and data_file.is_junior(index):
            continue
        couple = data_file.get_couple_at_index(index)
        new_name = get_name(couple["name"], flag)
        if new_name not in current_list:
            current_list.append(new_name)
            
    return current_list.sort()



class Dancer_List():
    
    def __init__(self, dancer_type=Dancer_Type.PRO):

        self.names = list()
        folder_name = "./data/" + str(date.today().year)
        if dancer_type == Dancer_Type.PRO: 
            print("Adding Professional Smooth Competitors")
            add_both_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro/smooth_rankings.json"))
            print("Adding Professional Rhythm Competitors")
            add_both_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro/rhythm_rankings.json"))
            print("Adding Professional Standard Competitors")
            add_both_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro/standard_rankings.json"))
            print("Adding Professional Latin Competitors")
            add_both_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro/latin_rankings.json"))
            print("Adding Professional Showdance Competitors")
            add_both_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro/cabaret_showdance_rankings.json"))
            print("Adding Professional NightClub Competitors")
            add_both_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro/nightclub_rankings.json"))
            add_both_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro/country_rankings.json"))
            print("Adding Pro-Am Smooth Instructors")
            add_student_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro-Am/smooth_rankings.json"))
            print("Adding Pro-Am Rhythm Instructors")
            add_student_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro-Am/rhythm_rankings.json"))
            print("Adding Pro-Am Standard Instructors")
            add_student_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro-Am/standard_rankings.json"))
            print("Adding Pro-Am Latin Instructors")
            add_student_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro-Am/latin_rankings.json"))
            print("Adding Pro-Am Nightclub Instructors")
            add_student_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro-Am/nightclub_rankings.json"))
            print("Adding Pro-Am Country Instructors")
            add_student_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro-Am/country_rankings.json"))
            print("Total number of professionals:", len(self.names))
        elif dancer_type == Dancer_Type.ADULT_STUDENT:  
            print("Adding Pro-Am Smooth Students")
            add_student_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro-Am/smooth_rankings.json"), Dancer_Type.ADULT_STUDENT)
            print("Adding Pro-Am Rhythm Students")
            add_student_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro-Am/rhythm_rankings.json"), Dancer_Type.ADULT_STUDENT)
            print("Adding Pro-Am Standard Students")
            add_student_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro-Am/standard_rankings.json"), Dancer_Type.ADULT_STUDENT)
            print("Adding Pro-Am Latin Students")
            add_student_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro-Am/latin_rankings.json"), Dancer_Type.ADULT_STUDENT)
            print("Adding Pro-Am Nightclub Students")
            add_student_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro-Am/nightclub_rankings.json"), Dancer_Type.ADULT_STUDENT)
            print("Adding Pro-Am Country Students")
            add_student_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro-Am/country_rankings.json"), Dancer_Type.ADULT_STUDENT)       
            print("Total number of adult students:", len(self.names))        
        elif dancer_type == Dancer_Type.JUNIOR_STUDENT:  
            print("Adding Pro-Am Smooth Junior Students")
            add_student_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro-Am/smooth_rankings.json"), Dancer_Type.JUNIOR_STUDENT)
            print("Adding Pro-Am Rhythm Junior Students")
            add_student_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro-Am/rhythm_rankings.json"), Dancer_Type.JUNIOR_STUDENT)
            print("Adding Pro-Am Standard Junior Students")
            add_student_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro-Am/standard_rankings.json"), Dancer_Type.JUNIOR_STUDENT)
            print("Adding Pro-Am Latin Junior Students")
            add_student_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro-Am/latin_rankings.json"), Dancer_Type.JUNIOR_STUDENT)
            print("Adding Pro-Am Nightclub Junior Students")
            add_student_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro-Am/nightclub_rankings.json"), Dancer_Type.JUNIOR_STUDENT)
            print("Adding Pro-Am Country Junior Students")
            add_student_names(self.names, RankingDataFile(folder_name + "/Rankings/Pro-Am/country_rankings.json"), Dancer_Type.JUNIOR_STUDENT)       
            print("Total number of junior students:", len(self.names))
        elif dancer_type == Dancer_Type.ADULT_AMATEUR:  
            print("Adding Pro-Am Smooth Adult Amateur")
            add_both_names(self.names, RankingDataFile(folder_name + "/Rankings/Amateur/smooth_rankings.json"), Dancer_Type.ADULT_AMATEUR)
            print("Adding Pro-Am Rhythm Adult Amateur")
            add_both_names(self.names, RankingDataFile(folder_name + "/Rankings/Amateur/rhythm_rankings.json"), Dancer_Type.ADULT_AMATEUR)
            print("Adding Pro-Am Standard Adult Amateur")
            add_both_names(self.names, RankingDataFile(folder_name + "/Rankings/Amateur/standard_rankings.json"), Dancer_Type.ADULT_AMATEUR)
            print("Adding Pro-Am Latin Adult Amateur")
            add_both_names(self.names, RankingDataFile(folder_name + "/Rankings/Amateur/latin_rankings.json"), Dancer_Type.ADULT_AMATEUR)
            print("Adding Pro-Am Nightclub Adult Amateur")
            add_both_names(self.names, RankingDataFile(folder_name + "/Rankings/Amateur/nightclub_rankings.json"), Dancer_Type.ADULT_AMATEUR)     
            print("Total number of adult amateurs:", len(self.names))     
            
        elif dancer_type == Dancer_Type.JUNIOR_AMATEUR:  
            print("Adding Pro-Am Smooth Junior Amateurs")
            add_both_names(self.names, RankingDataFile(folder_name + "/Rankings/Amateur/smooth_rankings.json"), Dancer_Type.JUNIOR_AMATEUR)
            print("Adding Pro-Am Rhythm Junior Amateurs")
            add_both_names(self.names, RankingDataFile(folder_name + "/Rankings/Amateur/rhythm_rankings.json"), Dancer_Type.JUNIOR_AMATEUR)
            print("Adding Pro-Am Standard Junior Amateurs")
            add_both_names(self.names, RankingDataFile(folder_name + "/Rankings/Amateur/standard_rankings.json"), Dancer_Type.JUNIOR_AMATEUR)
            print("Adding Pro-Am Latin Junior Amateurs")
            add_both_names(self.names, RankingDataFile(folder_name + "/Rankings/Amateur/latin_rankings.json"), Dancer_Type.JUNIOR_AMATEUR)
            print("Adding Pro-Am Nightclub Junior Amateurs")
            add_both_names(self.names, RankingDataFile(folder_name + "/Rankings/Amateur/nightclub_rankings.json"), Dancer_Type.JUNIOR_AMATEUR)     
            print("Total number of junior amateurs:", len(self.names))             
        
    def save_to_file(self, filename):
        output_file = open(filename, "w", encoding="UTF-8")
        for name in self.names:
            output_file.write(name + "\n")
        output_file.close()        
        
        
'''Main program'''
if __name__ == '__main__':
    instructors = Dancer_List(Dancer_Type.PRO)
    print(instructors.names)
    instructors.save_to_file("data/2019/Rankings/professionals.txt")
    
    adult_students = Dancer_List(Dancer_Type.ADULT_STUDENT)
    print(adult_students.names)
    adult_students.save_to_file("data/2019/Rankings/adult_students.txt")    
    
    junior_students = Dancer_List(Dancer_Type.JUNIOR_STUDENT)
    print(junior_students.names)
    junior_students.save_to_file("data/2019/Rankings/junior_students.txt")  
    
    adult_am_students = Dancer_List(Dancer_Type.ADULT_AMATEUR)
    print(adult_am_students.names)
    adult_am_students.save_to_file("data/2019/Rankings/adult_amateur_students.txt")  
    
    junior_am_students = Dancer_List(Dancer_Type.JUNIOR_AMATEUR)
    print(junior_am_students.names)
    junior_am_students.save_to_file("data/2019/Rankings/junior_amateur_students.txt")     