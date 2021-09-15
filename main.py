import pygame 
import random
import os
from player import *
from platforms import *
from settings import  *
import neat
import numpy as np
#import  visualize 

class Game:
    def __init__(self):
        # initialize game window, etc
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("GEO-Jump")
        self.clock = pygame.time.Clock()
        self.gernation = 0

    def eval_genomes(self, genomes, config):
        """
        runs the simulation of the current population of
        players and sets their fitness based on differnt parameters.
        """

        self.gernation += 1
        self.score = 0

        self.platforms = []        
        # load start platforms
        for plat in START_PLATFORMS:
            p = Platform(*plat)
            self.platforms.append(p)


        # start by creating lists holding the genome itself, the
        # neural network associated with the genome and the
        # bird object that uses that network to play

        # list with neural network of each genum
        self.nets = []
        # list with player
        self.players = []
        # list with genums
        self.myGenomes = []
        # list which holds the index of the last hiting platform for each player 
        self.hitPlatforms = []

        
        for genome_id, genome in genomes: # len(genomes) == 30 because of POP_SITZE = 30 
            genome.fitness = 0  # start with fitness level of 0
            #creat the first version of a neural network for each genum
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            self.nets.append(net)
            self.players.append(Player(self))
            self.myGenomes.append(genome)
            self.hitPlatforms.append(0)
        
        self.run()

    def run(self):
        # Game Loop
        self.playing = True
        while self.playing and len(self.players) > 0: # only run the game if at least one player is alife
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()

    def update(self):
        # Game Update
        for player in self.players:
            player.update() 

        # check if player hits a platform and save the platform index in self.hitPlatforms
        # reward player for hiting different platforms with an higher index
        # punish player for hiting platforms with lower index  
        for x, player in enumerate(self.players):
                for i,plat in enumerate(self.platforms):
                    hits = pygame.sprite.collide_rect(player, plat)
                    if hits:  
                        if player.rect.bottom < plat.rect.bottom: #for better collision
                            #put the player ontop of the platform and his vellocity.y = 0
                            player.pos.y = plat.rect.top 
                            player.vellocity.y = 0
                        
                        if player.vellocity.y > 5: #needed because of bad performance
                            #put the player ontop of the platform and his vellocity.y = 0
                            player.pos.y = plat.rect.top 
                            player.vellocity.y = 0
                        
                        #reward player 
                        if i > self.hitPlatforms[x]:
                            self.myGenomes[x].fitness  += 5
                        
                        #punish player
                        if  i < self.hitPlatforms[x]:
                            self.myGenomes[x].fitness  -= 1

                        #reward player for staying at the same platform
                        if  i == self.hitPlatforms[x]:
                            self.myGenomes[x].fitness  += 0.01
                        self.hitPlatforms[x]= i


        #kill old platforms,count score and correct the hitPlatforms value
        for plat in self.platforms:
            if plat.rect.top >= HEIGHT:
                self.platforms.pop(0)
                self.score += 10
                for i,hit in enumerate(self.hitPlatforms):
                    self.hitPlatforms[i] = hit-1
                    if self.hitPlatforms[i] < 0:
                        self.hitPlatforms[i] = 0


        # if player reaches top 1/4 of screen move everything for the amount of the player.vellocity.y down
        for player in self.players:
            if player.rect.top <= HEIGHT / 4:
                #you only can reach the top 1/4 of the screen while Jumping
                for player1 in self.players:
                    player1.pos.y += abs(player1.vellocity.y) #abs -> |self.player.vellocity.y|
                for plat in self.platforms:
                    plat.rect.y += abs(player.vellocity.y)
                break
        

        #move screen to kill faulty players/Genomes
        for player1 in self.players:
            player1.pos.y += 1
        for plat in self.platforms:
            plat.rect.y += 1


        #ckeck if player dies
        for i,player in enumerate(self.players):
            if player.rect.bottom > HEIGHT:
                        self.myGenomes[i].fitness -= 5
                        self.nets.pop(i)
                        self.myGenomes.pop(i)
                        self.players.pop(i)
                        self.hitPlatforms.pop(i)
            if len(self.players) == 0:
                self.playing = False


        #spawn new platforms to keep same average number
        if self.playing and self.platforms[-1].rect.bottom > -600:
            #level of difficulty
            if self.score < 500:
                minWidth, maxWidth = 140, 160
            else:
                minWidth, maxWidth = 20, 100

            width = random.randrange(minWidth, maxWidth)
            p = Platform(random.randrange(0, WIDTH - width),
                        random.randrange(-770, -760),
                        width, 10)
            self.platforms.append(p)
        

        for x, player in enumerate(self.players):             
            #Var. for Input layer
            self.nextPlat = self.platforms[self.hitPlatforms[x]+1]
            self.nextPlat_hight = player.rect.bottom - self.nextPlat.rect.bottom
            self.nextPlat_right = player.rect.left - self.nextPlat.rect.left
            self.nextPlat_left = player.rect.right - self.nextPlat.rect.right
            
            # Imput Var. myPlace is always 0 when the Player isnt at the x-range of the last hiten platform
            # the Player reaches the highest myPlace value if he is in the center of the last hiten platform 
            self.myPlatform = self.platforms[self.hitPlatforms[x]]
            self.player_X = player.rect.x + 15 # +15 to get the players center
            self.myPlace = self.player_X - self.myPlatform.rect.left

            if self.myPlace > self.myPlatform.rect.width/ 2:
                self.myPlace = (self.player_X - self.myPlatform.rect.right) * -1
            if self.myPlace < 0:
                self.myPlace = 0
            self.playerFintes = self.myGenomes[x].fitness


            #feed the networks with myplace, next obstacle distance, next obstacle hight, next obstacle widht of each player
            output = self.nets[x].activate((self.nextPlat_right,self.nextPlat_left, self.nextPlat_hight, self.myPlace))
            #determine from network whether to jump or not
            #determine from network whether to move or not
            if output[0] < 0.5:  #i use the tanh activation function so result will be between -1 and 1. if over 0.5 jump
                player.jump()
            if output[1] > 0.5:
                player.left = True
            if output[2] > 0.5:
                player.right = True


    def events(self):
        # Game Loop - events
        for event in pygame.event.get():
            # check for closing window
            if event.type == pygame.QUIT:
                self.playing = False
                quit()



    def draw(self):
        # Game Loop - draw
        self.screen.fill(BLACK)
        for player in self.players:
            player.draw(self.screen)
        for platform in self.platforms:
            platform.draw(self.screen)
        
        # draw text
        self.draw_text("Score: "+str(self.score), 25, WHITE, 1, 20,True)
        self.draw_text("Fitnes: " +str(np.around(self.playerFintes)), 20, WHITE, 1, 43,True) 
        self.draw_text("Generation: " + str(self.gernation), 20, WHITE, 20, 90)
        self.draw_text("Alive: " +str(len(self.players)), 20, WHITE, 20, 110)
        self.draw_text("nextPlat_dist: " +str(self.nextPlat_hight), 15, WHITE,20, 440)
        self.draw_text("NextPlat_left: " +str(self.nextPlat_left), 15, WHITE, 20, 460)
        self.draw_text("NextPlat_right: " +str(self.nextPlat_right), 15, WHITE, 20, 480)
        self.draw_text("Player_co: " +str(self.myPlace), 15, WHITE, 20, 500)
    
        # draw lines 
        for x,player in enumerate(self.players):
            playerCenter = (player.rect.x + 15. , player.rect.y + 15)
            pygame.draw.line(self.screen, RED, playerCenter, (self.nextPlat.rect.left, self.nextPlat.rect.bottom))
            pygame.draw.line(self.screen, RED, playerCenter, (self.nextPlat.rect.right, self.nextPlat.rect.bottom))

        # *after* drawing everything, flip the display
        pygame.display.flip()


    def draw_text(self, text, size, color, x, y,middle = False):
        font = pygame.font.Font(pygame.font.match_font(FONT_NAME), size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.top = y
        text_rect.left = x
        if middle:
            text_rect.midtop = (WIDTH/2,y)
        self.screen.blit(text_surface, text_rect)



def run(config_file):
    # runs the NEAT algorithm to train a neural network.
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,neat.DefaultSpeciesSet, neat.DefaultStagnation,config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    stats = neat.StatisticsReporter()
    p.add_reporter(neat.StdOutReporter(True))
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(5)) #generate checkpoints every 5 generations
    
    # eval_genomes is called once per gernation (eval_genomes is the Fitness_Function)
    winner = p.run(g.eval_genomes, 100)  #Run for up to 100 generations.

    # use visualize file
    visualize.draw_net(config, winner)
    visualize.plot_stats(stats, ylog=False, view=True)
    visualize.plot_species(stats, view=True)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    g = Game()
    # Determine path to configuration file. 
    # So that the script will run successfully regardless of the current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'configuration file.txt')
    run(config_path)
