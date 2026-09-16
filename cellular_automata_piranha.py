import pygame, random
import numpy as np

col_new_fish = (89, 150, 243)    # light blue
col_young_fish = (153, 102, 255)    # purple
col_breeding_fish = (220,35,157)    #fucsia

col_new_bear = (150,75,0)   # brown
col_parent_bear = (255, 153, 51)   # orange
col_breeding_bear = (0, 179, 60) # green
col_starving_bear = (75,75,75)  # grey

col_piranha = (255,0,0)
col_pir_full_stomach = (0 ,0  ,0)

col_empty = (213, 196, 161)
col_grid = (30, 30, 60)

FRAMES_PER_SECOND = 5
SPEED = 1

limit_pir = 100

ID = 0  # to identify each animal uniquely (for checking correctness)
def new_ID():
    global ID
    currentID = ID
    ID += 1
    return currentID

# Fish initial definition
def new_fish():
    ID_fish = new_ID()
    fish = {'type': 'fish', 'id':ID_fish, 'col':col_new_fish, 'age':0}
    return fish

# Bear initial definition
def new_bear():
    ID_bear = new_ID()
    bear = {'type': 'bear', 'id':ID_bear, 'col':col_new_bear, 'age':0, 'hunger':0}
    return bear

def new_piranha():
    ID_piranha = new_ID()
    piranha = {'type': 'piranha', 'id':ID_piranha, 'col':col_piranha, 'age': 0, 'stomach': 0 }
    return piranha

def empty():
    return {'type': 'empty'}

def init(dimx, dimy, fish, bear, piranha):
    """Creates a starting grid, of dimension dimx * dimy and inserts {fish} new fishes and {bear} new bears.
       The rest of the cells in the grid are filled with empty dictionaries. """
    # create a list with fish fishes, bear bears and the rest (dimx*dimy-fish-bear) are empty  and shuffle them

    content_list = []
    for i in range(fish):
        content_list.append(new_fish())
    for i in range(bear):
        content_list.append(new_bear())
    for i in range(piranha):
        content_list.append(new_piranha())
    for i in range((dimx * dimy - fish - bear - piranha)):
        content_list.append(empty())
    random.shuffle(content_list)

    # typecast the into a numpy array and reshape the 1 dimensional array to dimx * dimy
    cells_array = np.array(content_list)
    cells = np.reshape(cells_array, (dimy, dimx))  # the shape information is given in an  odd order
    return cells

# cur: the current array of cells,  r and c the row and column position which we are finding neighbours for.
def get_neighbors(cur, r, c):
    """Computes a list with the neighbouring cell positions of (r,c) in the grid {cur}"""
    r_min, c_min = 0 , 0
    r_max, c_max = cur.shape
    r_max, c_max = r_max -1 , c_max-1 # it's off by one
    # r-1,c-1 | r-1,c  | r-1,c+1
    # --------|--------|---------
    # r  ,c-1 | r  ,c  | r  ,c+1
    # --------|--------|---------
    # r+1,c-1 | r+1,c  | r+1,c+1
    neighbours = []
    # r-1:
    if r-1 >= r_min :
        if c-1 >= c_min: neighbours.append((r-1,c-1))
        neighbours.append((r-1,c))  # c is inside cur
        if c+1 <= c_max: neighbours.append((r - 1, c+1))
    # r:
    if c-1 >= c_min: neighbours.append((r,c-1))
    # skip center (r,c) since we are listing its neighbour positions
    if c + 1 <= c_max: neighbours.append((r,c+1))
    # r+1:
    if r + 1 <= r_max:
        if c - 1 >= c_min: neighbours.append((r+1,c-1))
        neighbours.append((r+1, c))  # c is inside cur
        if c + 1 <= c_max: neighbours.append((r+1,c+1))
    return neighbours

def neighbour_fish_empty_rest(cur,neighbours):
    """ Given a current grid and a set of neighbouring positions, it divides the neighbours into three lists of positions: """
    """ fish-neighbours, empty-neighbours cells and the rest"""
    # divide the neighbours into fish, empty cells and the rest
    fish_neighbours =[]
    empty_neighbours =[]
    bear_neighbours =[]
    piranha_neighbours =[]
    for neighbour in neighbours:
        if cur[neighbour]['type'] == "fish":
            fish_neighbours.append(neighbour)
        elif cur[neighbour]['type'] == "bear":
            bear_neighbours.append(neighbour)
        elif cur[neighbour]['type'] == "piranha":
            piranha_neighbours.append(neighbour)
        else:
            empty_neighbours.append(neighbour)

    return fish_neighbours, empty_neighbours, bear_neighbours, piranha_neighbours

def fish_rules(cur,r,c,neighbour_fish, neighbour_empty):
    """ Given the current grid {cur}, a position (r,c) which contains a fish, and a list of grid-positions for the
    fish-neighbours  and a list of grid-positions of empty neighbour cells. Update the grid according to the fish-rules"""

    # implement the fish rules
    cur[r, c]['age'] = cur[r, c]['age'] + 1     # update age

    # it breeds if it's been alive for 12 states
    if cur[r, c]['age'] >= 12:
        cur[r, c]['col'] = col_breeding_fish
        if neighbour_empty != []:  # check if the list is not empty
            new_location = random.choice(neighbour_empty)  # pick a random empty cell from the list
            cur[new_location] = new_fish()
            cur[new_location]['col'] = col_new_fish
            neighbour_fish.append(new_location)
            neighbour_empty.remove(new_location)
    else:
        cur[r, c]['col'] = col_young_fish

    # dies if overcrowded
    if len(neighbour_fish) >= 2:
        cur[r,c] = empty()  #fish dies

    # if it does not die, moves
    if neighbour_empty != []:   # check if the list is not empty
            new_location_empty = random.choice(neighbour_empty)  # pick a random empty cell from the list
            cur[new_location_empty] = cur[r, c]
            cur[r, c] = empty()

    return cur

def bear_rules(cur,r,c,neighbour_fish, neighbour_empty):
    """Given the current grid {cur}, a position (r,c) which contains a bear, and a list of grid-positions for the
    fish-neighbours  and a list of grid-positions of empty neighbour cells. Update the grid according to the fish-rules"""

    # implement the bear rules
    cur[r, c]['age'] = cur[r, c]['age'] + 1
    cur[r, c]['hunger'] = cur[r, c]['hunger'] + 1

    # bear dies of starvation
    if cur[r, c]['hunger'] >= 9:
        cur[r, c] = empty()

    # bear breeds if not dead
    elif cur[r, c]['age'] >= 8 and neighbour_empty != [] and cur[r, c]['hunger'] >= 3:  # check if the list is not empty
        cur[r, c]['col'] = col_breeding_bear
        new_location = random.choice(neighbour_empty)  # pick a random empty cell from the list
        cur[new_location] = new_bear()
        cur[new_location]['col'] = col_new_bear
        cur[r, c]['col'] = col_parent_bear


    # finds a fish and eats it
    elif neighbour_fish != []:   # check if the list is not empty
            fish_food = random.choice(neighbour_fish)  # pick a random empty cell from the list and store in fish_food
            neighbour_fish.remove(fish_food)
            neighbour_empty.append(fish_food)
            cur[fish_food] = empty()  # fish dies
            cur[r, c]['hunger'] = cur[r, c]['hunger'] - 1

    # bear moves
    elif neighbour_empty != []:  # check if the list is not empty
        bear_moves = random.choice(neighbour_empty)  # pick a random empty cell from the list
        cur[bear_moves] = cur[r, c]   # moves to the new location
        cur[r, c] = empty()     # erase actual location

    return cur

def piranha_rules(cur, r, c, neighbour_fish, neighbour_empty, neighbour_bear, limit):
    # get the position to the "right"
    """dimy, dimx = cur.shape
    print("dim", dimx, dimy)
    print('r,c', r, c)"""

    # Eats a random fish
    if neighbour_fish != []:
        fish_location = random.choice(neighbour_fish)
        cur[fish_location] = empty()
        neighbour_fish.remove(fish_location)
        neighbour_empty.append(fish_location)
        cur[r, c]['stomach'] = cur[r, c]['stomach'] + 1


    # Eats a random bear
    elif neighbour_bear != []:
        bear_location = random.choice(neighbour_bear)
        cur[bear_location] = empty()
        neighbour_bear.remove(bear_location)
        neighbour_empty.append(bear_location)
        cur[r, c]['stomach'] = cur[r, c]['stomach'] + 2


    # piranha dies
    if cur[r, c]['stomach'] <= (limit - 20):
        cur[r, c]['col'] = col_piranha
    else:
        cur[r, c]['col'] = col_pir_full_stomach
    if cur[r, c]['stomach'] > limit:
        cur[r, c] = empty()


    # piranha moves
    if neighbour_empty != []:
        piranha_location = random.choice(neighbour_empty)
        cur[piranha_location] = cur[r, c]
        cur[r, c] = empty()

    # move to the right
    """if c < dimx - 1:
        r_new, c_new = r, c + 1
        print('case 1: rnew,cnew', r_new, c_new)
    elif c == dimx - 1 and r < dimy - 1:
        r_new, c_new = 0, 0
        print('case 2: rnew,cnew', r_new, c_new)
    elif c == dimx - 1:
        r_new, c_new = (r + 1, 0)
        print('case 3: rnew,cnew', r_new, c_new)
    else:
        print('case 4: r,c', r, c)

    # Move piranha  to the right
    cur[r_new, c_new] = cur[r, c]
    cur[r, c] = empty()"""

    return cur

def update(surface, cur, sz):
    # for each cell
    for r, c in np.ndindex(cur.shape):
        # if there is a bear or a fish
        if cur[r, c]['type'] == "fish" or cur[r, c]['type'] == "bear" or cur[r, c]['type'] == "piranha":
            # calculate neighbours and find the empty and the fish neighbours (other bears are not important, currently)
            neighbours = get_neighbors(cur, r, c)
            neighbour_fish, neighbour_empty, neighbour_bear, neighbour_piranha = neighbour_fish_empty_rest(cur, neighbours)
            # For checking the state of the animal (correctness)
            print(f"Pos: ({r},{c}), Animal: {cur[r, c]}")
            # if it is a fish
            if cur[r, c]['type'] == "fish":
                cur = fish_rules(cur, r, c, neighbour_fish, neighbour_empty)

            # if it is a bear
            if cur[r, c]['type'] == "bear":
                cur = bear_rules(cur, r, c, neighbour_fish, neighbour_empty)

            # if it is a piranha
            elif cur[r, c]['type'] == "piranha":
                cur = piranha_rules(cur, r, c, neighbour_fish, neighbour_empty, neighbour_bear, limit_pir)

    return cur

def draw_grid(surface,cur,sz):
    """Given a grid {cur}, the size of the drawn cells, and a surface to draw on. Draw the """
    for r, c in np.ndindex(cur.shape):
        col = col_empty # if the cell is empty, the color should be that of "empty"
        if cur[r, c]['type'] != 'empty': # if the cell is not empty update the color according to its content
            col = cur[r, c]['col']
        pygame.draw.rect(surface, col, (c * sz, r * sz, sz - 1, sz - 1))

def main(dimx, dimy, cellsize, fish, bear, piranha):
    pygame.init()
    surface = pygame.display.set_mode((dimx * cellsize, dimy * cellsize))
    pygame.display.set_caption("Animal Kingdom")

    cells = init(dimx, dimy, fish, bear, piranha) # creates the grid representation
    draw_grid(surface, cells, cellsize)
    pygame.display.update()

    clock = pygame.time.Clock()
    speed_count = 1
    while True:
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        surface.fill(col_grid)
        if(speed_count % SPEED == 0):   # slows down the time step without slowing down the frame rate
            # update grid
            print(f"timestep: {speed_count // SPEED}")
            cells = update(surface, cells, cellsize)
        # draw the updated grid
        draw_grid(surface, cells, cellsize)
        pygame.display.update()
        clock.tick(FRAMES_PER_SECOND)
        speed_count = speed_count +1

if __name__ == "__main__":
    fish = 50
    bear = 5
    piranha = 5
    main(40, 10, 16, fish, bear, piranha)
