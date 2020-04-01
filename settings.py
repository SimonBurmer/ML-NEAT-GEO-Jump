#GEO-Jump Settings

#Colors (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
LIGHTBLUE = (0, 155, 155)
BGCOLOR = LIGHTBLUE

#Window
WIDTH = 480
HEIGHT = 600

#Game settings
TITLE = "GEO-Jump"
FPS = 60
FONT_NAME = 'arial'
HS_FILE = "highscore.txt"


#Player properties
PLAYER_ACC = 0.5
PLAYER_FRICTION = -0.12
PLAYER_GRAV = 0.8
PLAYER_JUMP = 20

#Start platforms (x,y,width,height)
START_PLATFORMS = [(0, HEIGHT - 40, WIDTH, 40),(WIDTH / 2 - 50, HEIGHT * 3 / 4, 100, 10),(330, 250, 150, 10),(100, 100, 130, 10),(40, -100, 200, 10),(350, -250, 150, 10),(10, -400, 200, 10),(60, -550, 100, 10)]