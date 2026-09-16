''' Cannon game: First Assignment 1 for Scientific Computing at Roskilde University

 Program functionality description:

   The following program displays a (2000m broad and 1000m high) field with a blue canon (20m wide, 16m high) positioned
   200m from the left side of the field. The scaling factor is 0.5, thus the window is 1000 pixels x 500 pixels.
   The cannon's upper left corner is at position (200m,16m) and has a barrel representing the projectiles initial
   velocity (84,84) m/s. The canon is continuously firing a projectile (from the center of the cannon) starting with the
   initial velocity. The projectile is effected by gravity. When the projectile exits the field, it is repositioned to
   the center of the cannon and refired.

Program controles:
    Press q to quit,
          g to show/hide grid

  Authors: Maja H Kirkeby & Ulf R. Pedersen
  
  !!! Remember to update the program description for your version !!!

'''
from email.header import SPACE

# Import modules
import pygame
import sys

# module to generate random wind
import random

# Initialize pygame
pygame.init()


# Define colors
BLACK = 0, 0, 0
WHITE = 255, 255, 255
BLUE = 0, 0, 255
RED = 255, 0, 0
GREEN = 0, 255, 0
PINK = 255, 105, 180
ORANGE = 255, 150, 0

# Define a frame rate
frames_per_second = 60

# Initialize real world parameters
g = 9.8   # Gravitational acceleration (m/s**2)
mass = 1  # Mass of projectile (kg)
D = 0.1  # Coefficient of friction


# Set parameters for time
speedup = 10    # in order to reduce waiting time for impact we speed up by increasing the timestep
t = 0.0        # time in seconds
dt = (1 / frames_per_second)*speedup  # time increment in seconds

width = 2000.0   # Position of wall to the right and width of the coordinate system
height = 1000.0  # Height of the coordinate system
x_grid = 100 # the interval of x-axis grid of the coordinate system
y_grid = 100  # the interval of y-axis grid of the coordinate system

scale_real_to_screen = 0.5 # scale from the real-world to the screen-coordinate system
x_first = 0
x_last = 0
y_first = 0
y_last = 0


# Initialize game loop variables
running = True
shooting = False
show_grid = True
round_counting = 0
turn = 0
v_wind = random.randint(-15,15)  # generating wind velocity
first_position = (0, 0)
last_position = (0, 0)
opposite_turn = (turn + 1) % 2

def convert(real_world_x, real_world_y, scale=scale_real_to_screen, real_world_height=height):
    ''' conversion from real-world coordinates to pixel-coordinates '''
    return int(real_world_x*scale), int((real_world_height-real_world_y)*scale-1)

# initialize real world cannon(s):
# ================================
# The values for the cannon is kept in a dictionary called cannon1. The correctness of some of the functions depend
# on the cannon to have the specified keys defined (you can add other key-value pairs). The intention is that you
# can create extra cannons, i.e., dictionaries with the same keys and different values, and add those to the
# players-list.
# 315.0 m/s Cannonball, e.g., https://www.arc.id.au/CannonBallistics.html
# 120 m/s small gun https://en.wikipedia.org/w/index.php?title=Muzzle_velocity&oldid=970936654

cannon_width, cannon_height = 40, 32
cannon1 = {"x": 200,
           "y": 0+cannon_height,
           "vx": 84.85,  # ≈ 120 m/s angle 45
           "vy": 84.85,  # ≈ 120 m/s angle 45
           "width": cannon_width,
           "height": cannon_height,
           "color": GREEN,
           'ball_radius': 15,  # radius in meters
           'score': 0
            }
cannon2 = {"x": 1760,
           "y": 0+cannon_height,
           "vx": -84.85,
           "vy": 84.85,  # ≈ 120 mx/s angle 45
           "width": cannon_width,
           "height": cannon_height,
           "color": ORANGE,
           'ball_radius': 15,  # radius in meters
           'score': 0
            }

# list of players
players = [cannon1, cannon2]


def calc_init_ball_pos(cannon):
    ''' Finds the center of the cannon '''
    return cannon['x'] + cannon['width']/2, cannon['y'] - cannon['height']/2


def draw_cannon(surface, cannon):
    ''' Draw the cannon (the barrel will be the length of the initial velocity of the ball '''
    rect = (
        convert(cannon['x'], cannon['y']),
        (cannon['width']*scale_real_to_screen, cannon['height']*scale_real_to_screen)
    )
    pygame.draw.rect(surface, cannon['color'], rect)
    cannon_center = calc_init_ball_pos(cannon)
    line_from = convert(cannon_center[0], cannon_center[1])
    line_to = convert(cannon_center[0]+cannon['vx']*scale_real_to_screen, cannon_center[1]+cannon['vy']*scale_real_to_screen)
    line_width = 6
    pygame.draw.line(surface, cannon['color'], line_from, line_to, line_width)


def is_inside_field(real_world_x, real_world_y, field_width=width):
    ''' Return true if input is within world '''
    # Note: there is no ceiling
    return 0 < real_world_x < field_width and real_world_y > 0


# Create PyGame screen:
# 1. specify screen size
screen_width, screen_height = int(width*scale_real_to_screen), int(height*scale_real_to_screen)
# 2. define screen
screen = pygame.display.set_mode((screen_width, screen_height))
# 3. set caption
pygame.display.set_caption("Not Space Invaders")

# Update pygames clock use the framerate
clock = pygame.time.Clock()


def draw_grid(surface, color, real_x_grid, real_y_grid, real_width=width, real_height=height):
    ''' Draw real-world grid on screen '''
    # vertical lines
    for i in range(int(real_width / real_x_grid)):
        pygame.draw.line(surface, color, convert(i * real_x_grid, 0),  convert(i * real_x_grid, real_height))
    # horizontal lines
    for i in range(int(real_height / y_grid)):
        pygame.draw.line(surface, color, convert(0 , i * real_y_grid ), convert(real_width, i * real_y_grid))

# Initialize projectile values (see also function below)
x, y = calc_init_ball_pos(players[turn])
vx = players[turn]['vx']  # x velocity in meters per second
vy = players[turn]['vy']  # y velocity in meters per second
ball_color = players[turn]['color']
ball_radius = players[turn]['ball_radius']


def change_player():
    ''' initialize the global variables of the projectile to be those of the players cannon '''
    # Technical comment concerning the "global" (can be deleted):
    #   we need to tell the program that we want to update the global variables. If we did not, the program would instead
    #   think that we are working with some other variables with the same name.s

    global players, turn, x, y, vx, vy, ball_color, ball_radius, shooting, round_counting
    shooting = False
    turn = (turn + 1) % len(players)   # will rotate through the list of players
    x, y = calc_init_ball_pos(players[turn])
    vx, vy = players[turn]['vx'], players[turn]['vy']
    ball_color = players[turn]['color']
    ball_radius = players[turn]['ball_radius']
    if turn % 2 == 0:
        round_counting = round_counting + 1
        print('Round:', round_counting)

def is_point(real_world_x, real_world_y):
    if (players[opposite_turn]['x'] < real_world_x < players[opposite_turn]['x'] + cannon_width and cannon_height > real_world_y > 0):
        players[turn]['score'] = players[turn]['score'] + 1
    return True


# Game loop:
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_g:
                show_grid = not show_grid
            elif event.key == pygame.K_SPACE:
                shooting = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            print(event)
            x_pix, y_pix = pygame.mouse.get_pos()
            x_first = x_pix / scale_real_to_screen
            y_first = -(y_pix / scale_real_to_screen) + height
        elif event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:
                x_pix, y_pix = pygame.mouse.get_pos()
                x_last = x_pix / scale_real_to_screen
                y_last = -(y_pix / scale_real_to_screen) + height
        elif event.type == pygame.MOUSEBUTTONUP:
            players[turn]['vx'] = x_first - x_last
            players[turn]['vy'] = y_first - y_last

    # Check whether the ball is outside the field
    if not is_inside_field(x,y):
        shooting = False
        change_player() # if there is only one player, the ball will restart at that players center

    # round counting
    if round_counting == 5:
        running = False


    # Game logic
    #   draw a background using screen.fill()
    screen.fill(BLACK)

    # draw grid
    if show_grid:
        draw_grid(screen, PINK, x_grid, y_grid, width, height)

    # draw the player's cannon
    draw_cannon(screen, cannon1)
    draw_cannon(screen, cannon2)

    # convert the real-world coordinates to pixel-coordinates
    x_pix, y_pix = convert(x, y)
    ball_radius_pix = round(scale_real_to_screen * ball_radius)

    # draw ball using the pixel coordinates
    pygame.draw.circle(screen, ball_color, (x_pix,y_pix), ball_radius_pix)

    # print time passed, position and velocity
    # print(f"time: {t}, pos: ({x,y}), vel: ({vx,vy}, pixel pos:({x_pix},{y_pix}))")

    if shooting:
        # update time passed, the projectile 's real-world acceleration, velocity,
        # position for the next time_step using the Leap-Frog algorithm

        # drag force
        drag_force_x = -D * (vx - v_wind)
        drag_force_y = -D * vy

        # Apply force of gravitational acceleration
        Fx = 0 + drag_force_x
        Fy = -mass * g + drag_force_y

        # Compute acceleration
        ax = Fx / mass
        ay = Fy / mass

        # Half velocity
        vx_half = vx + ax * (dt / 2)
        vy_half = vy + ay * (dt / 2)

        # Update positions from velocities
        x = x + vx * dt
        y = y + vy * dt

        # Update velocities from acceleration
        vx = vx_half  + ax * (dt / 2)
        vy = vy_half + ay * (dt / 2)

        #draw arrow for the direction of wind
        if v_wind < 0:
            pygame.draw.rect(screen, players[turn]['color'], (100, 100, 100, 20))
            pygame.draw.polygon(screen, players[turn]['color'], [(100,80),(50,110),(100,140)])
        if v_wind > 0:
            pygame.draw.rect(screen, players[turn]['color'], (100, 100, 100, 20))
            pygame.draw.polygon(screen, players[turn]['color'], [(200,80),(250,110),(200,140)])
        else: print('No wind')

        # change player
        """if x >= width:
            change_player()
        elif x <= 0:
            change_player()"""

        # bounce
        if y >= height:
            y = y - 2 * (y - height)
            vy = -vy
        elif y <= 0:
            y = -y
            vy = -vy

        if is_point(x, y):
            print('player1:', players[0]['score'], 'player2:', players[1]['score'])


    # Redraw the screen
    pygame.display.flip()

    # Limit the framerate (must be called in each iteration)
    clock.tick(frames_per_second)


# Close after the game loop
pygame.quit()
sys.exit()
    