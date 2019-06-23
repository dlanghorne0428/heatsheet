
'''
Point values are awarded based on the level of the event (Open, Rising Star, Novice) 
and the number of rounds (Final only, Semi-Final, and Quarter-Final).
Extra points are awarded for events that had prelim rounds.
Currently, the program only processes professional heats.
'''

'''max_point_values = {
    # these are values for pro rankings
    "Open":         {"F": 20, "S": 30, "Q": 40, "R1": 50},
    "Rising Star":  {"F": 10, "S": 20, "Q": 30, "R1": 40},
    "Novice":       {"F":  5, "S": 10, "Q": 15, "R1": 20},
    # these are values for pro/am rankings
    "Newcomer":     {"F":  5, "S": 10, "Q": 15},
    "Bronze":       {"F": 10, "S": 20, "Q": 30},
    "Silver":       {"F": 15, "S": 25, "Q": 35},
    "Challenge":    {"F": 15, "S": 25, "Q": 35},
    "Gold":         {"F": 20, "S": 30, "Q": 40},
    "Open-Gold":    {"F": 25, "S": 35, "Q": 45},
    "Scholarship":  {"F": 25, "S": 35, "Q": 45},
    "World":    {"F": 25, "S": 35, "Q": 45},
    # these are values for amateur rankings
    "Pre-Champ":    {"F": 15, "S": 25, "Q": 35},
    "Championship": {"F": 25, "S": 35, "Q": 45}, 
    # if no clue
    "Other":        {"F": 10, "S": 20, "Q": 30}
}'''

def calc_points(level, placement, num_competitors = 6, rounds = "F", accum = 0):
    
    if rounds == "S":
        max_pts = level + 10
    elif rounds == "Q":
        max_pts = level + 20
    elif rounds == "R1":
        max_pts = level + 30
    else:
        max_pts = level 
        
    place = placement - 1
    if num_competitors >= 5:
        if placement == -2: # semis
            percent = min(25, max(12, accum))  
        elif placement == -1:
            percent = min(10, max(1, accum))
        else:
            percent_table = [100, 80, 65, 50, 40, 30, 25, 25, 25]
            percent = percent_table[place]
        return max_pts * percent / 100 
    elif num_competitors == 4:
        percent = [100, 70, 50, 30];
        return max_pts * percent[place] / 100  
    elif num_competitors == 3:
        percent = [100, 60, 30];
        return max_pts * percent[place] / 100
    elif num_competitors == 2:
        percent = [100, 50];
        return max_pts * percent[place] / 100
    else:  # only one entry
        return max_pts

        
'''Main program for testing'''
if __name__ == '__main__':
    rounds = "F"
    for level in ["Open", "Rising Star", "Novice"]:
        for rounds in ["F", "S", "Q"]:
            for competitors in range(1, 9):
                for placement in range (1, competitors + 1):
                    print(level, rounds, competitors, placement, calc_points(level, placement, competitors, rounds=rounds))
            if rounds != "F":        
                print(level, rounds, competitors, "Semis", calc_points(level, -2, competitors, accum = 5, rounds=rounds)) 
                print(level, rounds, competitors, "Semis", calc_points(level, -2, competitors, accum = 15, rounds=rounds))                  
                print(level, rounds, competitors, "Semis", calc_points(level, -2, competitors, accum = 35, rounds=rounds)) 
            if rounds == "Q":
                print(level, rounds, competitors, "quarters", calc_points(level, -1, competitors, accum = 4, rounds=rounds))
                print(level, rounds, competitors, "quarters", calc_points(level, -1, competitors, accum = 14, rounds=rounds)) 
                