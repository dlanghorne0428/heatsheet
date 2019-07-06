


def calc_points(level, placement, num_competitors = 6, rounds = "F", accum = 0):
    '''
    Point values are awarded based on the level of the event (Open, Rising Star, Novice) 
    and the number of rounds (Final only, Semi-Final, and Quarter-Final).
    Extra points are awarded for events that had prelim rounds.
    '''    
    place = placement - 1
    max_pts = level
    if num_competitors >= 5:
        percent_table = [100, 80, 65, 50, 40, 35, 30, 25, 25]
        if rounds == "S":
            max_pts = level + 10
            if placement == -2: # semis
                percent = min(25, max(1, accum))
            else:
                percent = percent_table[place] 
        elif rounds == "Q":
            max_pts = level + 20
            if placement == -2: # semis
                percent = min(25, max(15, accum))
            elif placement == -1: # quarters
                percent = min(10, max(1, accum))            
            else:
                percent = percent_table[place]         
        elif rounds == "R1":
            max_pts = level + 30
            if placement == -2: # semis
                percent = min(25, max(20, accum))
            elif placement == -1: # quarters
                percent = min(15, max(10, accum))
            elif placement == -10: # round 1
                percent = min(15, max(10, accum))              
            else:
                percent = percent_table[place]      
        else:
            percent = percent_table[place]   
        return max_pts * percent / 100 
    elif num_competitors == 4:
        percent_table = [100, 70, 50, 35];
        return max_pts * percent_table[place] / 100  
    elif num_competitors == 3:
        percent_table = [90, 60, 35];
        return max_pts * percent_table[place] / 100
    elif num_competitors == 2:
        percent_table = [75, 35];
        return max_pts * percent_table[place] / 100
    else:  # only one entry
        return max_pts * 0.6

        
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
                