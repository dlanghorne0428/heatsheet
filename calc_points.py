
'''
Point values are awarded based on the level of the event (Open, Rising Star, Novice) 
and the number of rounds (Final only, Semi-Final, and Quarter-Final).
Extra points are awarded for events that had prelim rounds.
Currently, the program only processes professional heats.
'''

max_point_values = {
    "Open": {
        "F": 20, #[0, 20, 15, 12,  9,  7,  4, 3, 2],
        "S": 30, #[0, 30, 24, 20, 16, 12,  9, 7, 5, 4, 0],
        "Q": 40  #[0, 40, 32, 25, 20, 15, 12, 9, 7, 6, 3]
    },
    "Rising Star": {
        "F": 10, #[0, 10,  7,  5,  3,  2,  1, 1, 1],
        "S": 20, #[0, 20, 15, 12,  9,  7,  4, 3, 2, 2, 0],
        "Q": 30  #[0, 30, 24, 20, 16, 12,  9, 7, 5, 5, 2]
    },
    "Novice": {
        "F":  5, #[0,  5,  4,  3,  2,  1,  1, 1, 1],
        "S": 10, #[0, 10,  8,  6,  4,  3,  2, 1, 1, 1, 0],
        "Q": 15  #[0, 15, 12, 10,  8,  6,  5, 4, 3, 3, 1]
    }
}

def calc_points(level, placement, num_competitors = 6, rounds = "F", accum = 0):
    
    max_pts = max_point_values[level][rounds]
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
                