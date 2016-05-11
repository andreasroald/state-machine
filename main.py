import random

import pygame

import settings
import sprites
import tiles
import levels
import resources

# State template class
class States(object):
    # Initialize the states class
    def __init__(self):
        self.done = False
        self.next = None
        self.quit = False
        self.previous = None

        # give all states joystick support
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.joystick_plugged = True
            print("Controller detected! Using {}".format(self.joystick.get_name()))
        else:
            self.joystick_plugged = False

# Menu state
class Menu(States):
    # Initialize the menu state
    def __init__(self):
        States.__init__(self)
        self.next = "game"

    # Cleaning up the menu state
    def cleanup(self):
        pass

    # Starting the menu state
    def startup(self):
        pass

    # State event handling
    def get_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.done = True

        if event.type == pygame.JOYBUTTONDOWN:
            if self.joystick.get_button(7) == 1:
                self.done = True


    # Update the menu state
    def update(self, display):
        self.draw(display)

    # Menu state drawing
    def draw(self, screen):
        screen.fill((settings.red))

# Game state
class Game(States):
    # Initialize the game state
    def __init__(self):
        States.__init__(self)
        self.next = "menu"

    # Cleaning up the game state
    def cleanup(self):
        pass

    # Function that creates a level from a list and returns the level list
    def create_level(self, level, solid=True, bg=False):
        level_x = 0

        # Make the bottom-left tile aligned with the bottom-left of the screen
        if len(level) <= 20:
            level_y = 0
        else:
            level_y = 0 - (32 * (len(level) - 20))

        for rows in level:
            for cols in rows:
                for tilesets in tiles.tileset_list:
                    if int(cols) == tilesets.id:
                        for tile in tilesets.all_tiles:
                            if cols == tile["id"]:
                                # If the tile ID is divisible by 5, top solid is true
                                if int(cols) % 5 == 0:
                                    w = sprites.Wall(level_x, level_y, 32, 32, image=tile["image"], top_solid = True)
                                else:
                                    w = sprites.Wall(level_x, level_y, 32, 32, image=tile["image"])
                                if solid:
                                    self.walls.add(w)
                                elif bg:
                                    self.background_details.add(w)
                                else:
                                    self.details.add(w)

                level_x += 32
            level_x = 0
            level_y += 32

        return level

    # Starting the game state
    def startup(self):
        # Sprite groups
        self.background_details = pygame.sprite.Group()
        self.walls = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        self.fires = pygame.sprite.Group()
        self.dust = pygame.sprite.Group()
        self.animals = pygame.sprite.Group()
        self.details = pygame.sprite.Group()
        self.clouds = pygame.sprite.Group()

        # Creating an instance of the player
        self.player = sprites.Player(self.walls, None)
        if self.joystick_plugged:
            self.player.controller = self.joystick

        # Creating Animals
        self.bird_1 = sprites.Bird(120, 400, self.walls)
        self.bird_2 = sprites.Bird(550, 200, self.walls)
        self.bird_3 = sprites.Bird(900, 200, self.walls)

        self.animals.add(self.bird_1)
        self.animals.add(self.bird_2)
        self.animals.add(self.bird_3)

        # Create the background details layer
        self.create_level(levels.level_background_details, solid = False, bg = True)

        # Create the level and set current_level to its level list (used for camera movement)
        self.current_level = self.create_level(levels.level)

        # Create the details Layer
        self.create_level(levels.level_details, solid=False)

        # Level borders
        self.left_border = sprites.Wall(-1, 0, 1, settings.display_height)
        self.walls.add(self.left_border)

        self.right_border = sprites.Wall(len(self.current_level[0]) * 32, 0, 1, settings.display_height)
        self.walls.add(self.right_border)


        # We blit surfaces to the world surface, then blit the world surface to the game display
        self.world_surface = pygame.Surface((len(self.current_level[0]) * 32, settings.display_height))
        self.background = pygame.Surface((settings.display_width, settings.display_height))
        self.background.blit(resources.sky_background, (0, 0))

        # Camera variables
        self.cam_x_offset = 0

        # fireball variables
        self.previous_fireball = 0

        # Screen shake variables
        self.shake_amount = 10

    # Player fireball function
    def shoot_fireball(self):
        # Only allow fireballs to be shot every 250 milliseconds
        if pygame.time.get_ticks() - self.previous_fireball > 250:
            # Creating the fireball object based on player direction
            if self.player.direction == "left":
                fb = sprites.Fireball(self.player.rect.center[0], self.player.rect.center[1] + random.randint(-10, 10), "left", self.walls, self.details)
            elif self.player.direction == "right":
                fb = sprites.Fireball(self.player.rect.center[0], self.player.rect.center[1] + random.randint(-10, 10), "right", self.walls, self.details)

            self.projectiles.add(fb)

            self.player.knockback = True

            # Screen shake
            self.shake_amount = 4

            # Play the fireball sound
            pygame.mixer.Sound.play(resources.fireball_sound)

            # Set previous_fireball to current time
            self.previous_fireball = pygame.time.get_ticks()

    # State event handling
    def get_event(self, event):
        if event.type == pygame.QUIT:
            self.quit = True
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_SPACE:
                if self.player.jumping:
                    self.player.test_for_jump()
                else:
                    self.player.jump()

            if event.key == pygame.K_k:
                self.shoot_fireball()

        if event.type == pygame.JOYBUTTONDOWN:
            if self.joystick.get_button(2) == 1:
                self.shoot_fireball()

            if self.joystick.get_button(0) == 1:
                if self.player.jumping:
                    self.player.test_for_jump()
                else:
                    self.player.jump()

    # Update the game state
    def update(self, display):
        self.player.update()

        self.fires.update()
        self.dust.update()
        self.projectiles.update()
        self.animals.update()
        self.clouds.update()

        # Determine if player is shooting
        if pygame.time.get_ticks() - self.previous_fireball < 250:
            self.player.shooting = True
        else:
            self.player.shooting = False

        # Horizontal Camera scrolling
        self.cam_x_offset = self.player.rect.x - settings.display_width / 2

        if self.cam_x_offset < 0:
            self.cam_x_offset = 0

        if self.cam_x_offset > (len(self.current_level[0]) - 25) * 32:
            self.cam_x_offset = (len(self.current_level[0]) - 25) * 32

        # Reset game if player is out of the screen
        if self.player.rect.y > settings.display_height+64:
            self.startup()

        # Randomly spawn clouds
        cloud_num = random.randint(0, 700)

        if cloud_num == 700:
            c = sprites.Cloud(settings.display_width, random.randint(0, 300))
            self.clouds.add(c)

        # Delete off screen clouds
        for clouds in self.clouds:
            if clouds.rect.x == 0 - clouds.rect.width:
                clouds.kill()

        # Kill of screen animals
        for animals in self.animals:
            if animals.rect.y > settings.display_height:
                animals.kill()

        # Remove dead fireballs
        for fireballs in self.projectiles:
            if fireballs.dead:
                if fireballs.direction == "right":
                    for x in range(5):
                        d = sprites.Dust(fireballs.rect.right, fireballs.rect.center[1], 8, -4, random.randint(-4, 4), self.walls)
                        self.dust.add(d)
                if fireballs.direction == "left":
                    for x in range(5):
                        d = sprites.Dust(fireballs.rect.left, fireballs.rect.center[1], 8, 4, random.randint(-4, 4), self.walls)
                        self.dust.add(d)
                fireballs.kill()

        # Make fireballs Burn
        for fireballs in self.projectiles:
            if fireballs.direction == "right":
                f = sprites.Fire(fireballs.rect.center[0] - 8, fireballs.rect.center[1] + random.randint(-16, 16),
                         random.randint(1, 3)*8, 8, fireballs.speed - 5, 0, self.walls)
            elif fireballs.direction == "left":
                f = sprites.Fire(fireballs.rect.center[0] + 8, fireballs.rect.center[1] + random.randint(-16, 16),
                         random.randint(1, 3)*8, 8, fireballs.speed + 5, 0, self.walls)

            self.fires.add(f)

        # Remove plants destroyed by fireballs
        for remove_plants in self.details:
            if remove_plants.dead:
                for x in range(5):
                    f = sprites.Fire(remove_plants.rect.center[0] + random.randint(-4, 4),
                             remove_plants.rect.bottom, 8, random.randint(1, 3) * 8,
                             0, -2 + random.randint(-1, 1), self.walls, 35)
                    self.fires.add(f)
                remove_plants.kill()

        # Dust effect when player rolls
        if self.player.should_roll:
            d = sprites.Dust(self.player.rect.center[0], self.player.rect.bottom, 8, random.randint(-5, 5), -4, self.walls)
            self.dust.add(d)

        # Dust effect upon ground impact:
        if self.player.dust > 0:
            d = sprites.Dust(self.player.rect.center[0], self.player.rect.bottom, 8, random.randint(-5, 5), -3, self.walls)
            self.dust.add(d)
            self.player.dust -= 1

        # Randomly spawn dust particles when player is moving
        dust_num = random.randint(0, 40)

        if self.player.moving and not self.player.jumping and dust_num == 30:
            d = sprites.Dust(self.player.rect.center[0], self.player.rect.bottom, 8, random.randint(-5, 5), -3, self.walls)
            self.dust.add(d)

        # Remove dead fires
        for fire in self.fires:
            if fire.dead:
                fire.kill()

        # Remove dead dust
        for du in self.dust:
            if du.dead:
                du.kill()

        # Slowly stop screen shake
        if self.shake_amount > 0:
            self.shake_amount -= 0.5

        self.draw(display)

    # game state drawing
    def draw(self, screen):

        self.background.blit(resources.sky_background, (0, 0))
        self.clouds.draw(self.background)
        self.world_surface.blit(self.background, (0+self.cam_x_offset, 0))

        self.background_details.draw(self.world_surface)

        self.projectiles.draw(self.world_surface)
        self.dust.draw(self.world_surface)

        self.walls.draw(self.world_surface)

        self.player.draw(self.world_surface)

        self.animals.draw(self.world_surface)
        self.details.draw(self.world_surface)

        self.fires.draw(self.world_surface)

        # If shake amount is more than 0, blit the world at a random location between
        # negative and positive shake amount, instead of 0, 0
        if self.shake_amount > 0:
            screen.blit(self.world_surface, (random.randint(int(-self.shake_amount), int(self.shake_amount))-self.cam_x_offset,
                                                        random.randint(int(-self.shake_amount), int(self.shake_amount))))
        else:
            screen.blit(self.world_surface, (0-self.cam_x_offset, 0))

# Control class
class Control:
    # Initialize the control class
    def __init__(self):
        pygame.init()
        self.playing = True
        self.game_display = pygame.display.set_mode((settings.display_width, settings.display_height))
        self.clock = pygame.time.Clock()

    # Setup the state control
    def setup_states(self, state_dict, start_state):
        self.state_dict = state_dict
        self.state_name = start_state
        self.state = self.state_dict[self.state_name]

    # Function that runs when switching state
    def switch_state(self):
        self.state.done = False
        previous, self.state_name = self.state_name, self.state.next

        self.state.cleanup()
        self.state = self.state_dict[self.state_name]
        self.state.startup()

        self.state.previous = previous

    # Game loop
    def loop(self):
        while self.playing:
            self.clock.tick(settings.FPS)
            self.events()
            self.update()
            pygame.display.update()
            pygame.display.set_caption(settings.title + " running at " + str(int(self.clock.get_fps())) + " frames per second")

    # Event handling
    def events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.playing = False
            self.state.get_event(event)

    # Update the control class
    def update(self):
            if self.state.quit:
                self.playing = False
            elif self.state.done:
                self.switch_state()
            self.state.update(self.game_display)

game = Control()
state_dict = {
    "menu": Menu(),
    "game": Game()
}
game.setup_states(state_dict, "menu")
game.loop()

pygame.quit()
quit()
