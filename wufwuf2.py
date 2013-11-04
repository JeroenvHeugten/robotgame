import math
import random
import pprint
import redis
import itertools

# Open connection with the Redis server:
redis = redis.StrictRedis(host='localhost', port=6379, db=0)

def distance(loc1, loc2):
        return abs(loc1[0] - loc2[0]) + abs(loc1[1] - loc2[1])

class Robot:

    def close_adjacents(self):
        return ((self.location[0], self.location[1] + 1),
                (self.location[0], self.location[1] - 1),
                (self.location[0] + 1, self.location[1]),
                (self.location[0] - 1, self.location[1]))
    def remote_adjacents(self):
        return ((self.location[0] +1, self.location[1] + 1),
                (self.location[0] -1, self.location[1] - 1),
                (self.location[0] + 1, self.location[1] -1),
                (self.location[0] - 1, self.location[1] +1),
		(self.location[0], self.location[1] +2),
		(self.location[0], self.location[1] -2),
                (self.location[0] + 2, self.location[1]),
		(self.location[0] - 2, self.location[1]))
    
    def act(self, game):
    
        restricted_zones = [(0, 0), (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0), (11, 0), (12, 0), (13, 0), (14, 0), (15, 0), (16, 0), (17, 0), (18, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (12, 1), (13, 1), (14, 1), (15, 1), (16, 1), (17, 1), (18, 1), (0, 2), (1, 2), (2, 2), (3, 2), (4, 2), (14, 2), (15, 2), (16, 2), (17, 2), (18, 2), (0, 3), (1, 3), (2, 3), (16, 3), (17, 3), (18, 3), (0, 4), (1, 4), (2, 4), (16, 4), (17, 4), (18, 4), (0, 5), (1, 5), (17, 5), (18, 5), (0, 6), (1, 6), (17, 6), (18, 6), (0, 7), (18, 7), (0, 8), (18, 8), (0, 9), (18, 9), (0, 10), (18, 10), (0, 11), (18, 11), (0, 12), (1, 12), (17, 12), (18, 12), (0, 13), (1, 13), (17, 13), (18, 13), (0, 14), (1, 14), (2, 14), (16, 14), (17, 14), (18, 14), (0, 15), (1, 15), (2, 15), (16, 15), (17, 15), (18, 15), (0, 16), (1, 16), (2, 16), (3, 16), (4, 16), (14, 16), (15, 16), (16, 16), (17, 16), (18, 16), (0, 17), (1, 17), (2, 17), (3, 17), (4, 17), (5, 17), (6, 17), (12, 17), (13, 17), (14, 17), (15, 17), (16, 17), (17, 17), (18, 17), (0, 18), (1, 18), (2, 18), (3, 18), (4, 18), (5, 18), (6, 18), (7, 18), (8, 18), (9, 18), (10, 18), (11, 18), (12, 18), (13, 18), (14, 18), (15, 18), (16, 18), (17, 18), (18, 18), (7, 1), (8, 1), (9, 1), (10, 1), (11, 1), (5, 2), (6, 2), (12, 2), (13, 2), (3, 3), (4, 3),(14, 3), (15, 3), (3, 4), (15, 4), (2, 5), (16, 5), (2, 6), (16, 6), (1, 7), (17, 7),(1, 8), (17, 8), (1, 9), (17, 9), (1, 10), (17, 10), (1, 11), (17, 11), (2, 12), (16, 12),(2, 13), (16, 13), (3, 14), (15, 14), (3, 15), (4, 15), (14, 15), (15, 15), (5, 16), (6, 16),(12, 16), (13, 16), (7, 17), (8, 17), (9, 17), (10, 17), (11, 17)]

        close_locs 	= self.close_adjacents()
	remote_locs 	= self.remote_adjacents()
        robots = game['robots']
    
	# Check current turn:
	if redis.exists("turn"):
	    if int(redis.get("turn")) <> game['turn']:
		redis.flushdb()
	        redis.set("turn", game['turn'])
	else:
            redis.flushdb()
	    redis.set("turn", 1)			

	# Compare orders
	def compare_orders (loc):
	    if redis.exists(loc):
	    	return 1
	    else:
		redis.set(loc,'1')
		return 0 
 
        # Create empty possibilty dict:
        available_zones = {}
        
        def priority (loc, prio):
            if len(available_zones) > 0:
                if available_zones[available_zones.keys()[0]] > prio:
                    available_zones.clear()
                    available_zones[loc] = prio
            else:
                available_zones[loc] = prio
            
	count = 0       
	enemy = 0  
	for loc in remote_locs:
            count = count + 1
  	    if (robots.get(loc) and robots.get(loc)['player_id'] != self.player_id):
		if ((count == 1 or count == 4 or count == 5)and robots.get(self.location[0], self.location[1] + 1) != self.player_id):
			getcloser = (self.location[0], self.location[1] + 1)
			enemy = 1
			break
		elif ((count == 1 or count == 4 or count == 7)and robots.get(self.location[0] +1, self.location[1]) != self.player_id):
                        getcloser = (self.location[0] + 1, self.location[1])
                        enemy = 1
                        break
		elif((count == 2 or count == 3 or count == 6) and robots.get(self.location[0], self.location[1] - 1) != self.player_id):
                        getcloser = (self.location[0], self.location[1] - 1)
			enemy = 1
			break
                elif((count == 2 or count == 3 or count == 8) and robots.get(self.location[0] -1, self.location[1]) != self.player_id):
                        getcloser = (self.location[0] -1, self.location[1])
                        enemy = 1
                        break
		else:
			print "None" 

	for loc in close_locs:
            if loc not in restricted_zones:
                if (robots.get(loc) and robots.get(loc)['player_id'] == self.player_id):
                    # Friendly, do nothing
                    continue
		elif (self.hp < 11):
		    # Suicide
		    print "Suiciding"
		    return ['suicide']
                elif (robots.get(loc)):
                    # Kill enemy robot (immediately, always highest pref)
		    print "Attacking"
                    return ['attack', loc]
		elif enemy:
		    # Enemy at 2 steps away, march!
		    if compare_orders(loc):
			continue
		    if getcloser not in restricted_zones:
			print "Marching"
		        return ['move', getcloser]
                else:
                    # Move, but we need the best option, so send it to the priority function (sorted, min does not work because of limited imports)
                    if compare_orders(loc):
		        continue
		    priority(loc, distance(loc, (9,9)))
            else:
                # Out of playfield, do nothing
                continue

         # Send order to Robot:
        if len(available_zones) == 0:
            # No moves possible, defend!
	    print "Guarding"
            return ['guard']
        else:
            # Do best move possible:
	    print "Moving"
            return ['move', available_zones.keys()[0]]
