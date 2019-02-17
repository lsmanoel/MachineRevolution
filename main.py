import pygame
import time
import threading
import os
import sys
from random import gauss
import Actor
from Controller import Controller


class PgScreen:
    def __init__(self,
                 default_gravity=9.8,
                 screen_size=(800, 600),
                 edge_width=[20],
                 clock_rate=30,
                 pixel_meter=100,
                 surface_resistance=0.1,
                 noise_std_deviation=0.01):

        self.pygame = pygame
        self.pygame.init()
        self.pygame.font.init()

        self.font_color = (175, 0, 0)
        self.title_font = pygame.font.Font('font/CHECKBK0.TTF', 70)
        self.title = self.title_font.render('Machine Revolution', False, self.font_color)
        self.pwr_tensorflow_font = pygame.font.Font('font/CHECKBK0.TTF', 40)
        self.pwr_tensorflow = self.pwr_tensorflow_font.render('AI powered by Google TensorFlow', False, self.font_color)
        self.push_space_font = pygame.font.Font('font/CHECKBK0.TTF', 50)
        self.push_space = self.push_space_font.render('Push Space', False, self.font_color)
        self.push_backspace_font = pygame.font.Font('font/CHECKBK0.TTF', 50)
        self.push_backspace = self.push_space_font.render('Push Backspace', False, self.font_color)
        self.score_font = pygame.font.Font('font/CHECKBK0.TTF', 40)
        self.score_value = 0
        self.score = self.score_font.render(str(self.score_value), False, self.font_color)
        self.start = 0
        self.end = 0

        self.screen = pygame.display.set_mode(screen_size)
        self.screen_size = screen_size

        self.edge_width = edge_width

        self.main_state = 'start_state'
        self.close_app = False
        self.clock = pygame.time.Clock()
        self.clock_rate = clock_rate

        self.surface_resistance = surface_resistance
        self.default_gravity = default_gravity
        self.noise_std_deviation = noise_std_deviation
        self.pixel_meter = pixel_meter

        self.controller_list = []
        self.actor_list = []

        # --------------------------------------------------------------------------------------------------------------
        # Player:
        self.actor_list.append(Actor.Player(surface=self.screen,
                                            surface_size=self.screen_size,
                                            surface_resistance=self.surface_resistance,
                                            id_number=0,
                                            mass=2,
                                            init_resistance=self.surface_resistance,
                                            init_reaction_effect=True,
                                            init_pos=[dim_size//2 for dim_size in screen_size],
                                            sample_rate=clock_rate,
                                            ))

        # --------------------------------------------------------------------------------------------------------------
        # Edge Wall:
        self.actor_list.append(Actor.SideWall(surface=self.screen,
                                              surface_size=self.screen_size,
                                              surface_resistance=self.surface_resistance,
                                              id_number=1,
                                              category='side_wall',
                                              color=(10, 50, 255),
                                              thickness=100,
                                              mass=100,
                                              init_resistance=1,
                                              init_reaction_effect=True,
                                              default_gravity=default_gravity,
                                              sample_rate=clock_rate))

        # --------------------------------------------------------------------------------------------------------------
        # Aim:
        self.controller_list.append(Controller(screen_size=self.screen_size,
                                               noise_std_deviation=0.1))

        self.actor_list.append(Actor.ComputerAim(surface=self.screen,
                                                 surface_size=self.screen_size,
                                                 surface_resistance=self.surface_resistance,
                                                 id_number=2,
                                                 category='computer_aim',
                                                 color=(255, 0, 0),
                                                 size=[7],
                                                 mass=0.1,
                                                 init_resistance=self.surface_resistance,
                                                 init_reaction_effect=True,
                                                 controller=self.controller_list[-1],
                                                 init_pos=[dim_size for dim_size in screen_size],
                                                 sample_rate=clock_rate,
                                                 ai_target=self.actor_list[-2]
                                                 ))

        main_thread = threading.Thread(target=self.main_loop)
        main_thread.start()

    @property
    def noise(self):
        return gauss(mu=0, sigma=self.noise_std_deviation)

    def check_key_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.close_app = True
                for actor in self.actor_list:
                    if actor.ai_action is True:
                        actor.ai_controller.close_app = True

        if self.main_state == 'start_state':
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_SPACE]:
                self.main_state = 'pre_play_state'
            for actor in self.actor_list:
                actor.main_state = self.main_state

        elif self.main_state == 'pre_play_state':
            for actor in self.actor_list:
                if actor.category == 'side_wall':
                    self.main_state = actor.main_state
            for actor in self.actor_list:
                actor.main_state = self.main_state

        elif self.main_state == 'play_state':
            for actor in self.actor_list:
                if actor.category == 'side_wall' or actor.category == 'computer_aim':
                    if actor.main_state == 'dead_state':
                        self.main_state = actor.main_state
            for actor in self.actor_list:
                actor.main_state = self.main_state

        elif self.main_state == 'dead_state':
            pressed = pygame.key.get_pressed()
            if pressed[pygame.K_BACKSPACE]:
                self.main_state = 'restart_state'
            for actor in self.actor_list:
                actor.main_state = self.main_state
        elif self.main_state == 'restart_state':
            os.execl(sys.executable, sys.executable, *sys.argv)

    def main_loop(self):
        while not self.close_app:
            self.check_key_events()
            self.score_update()

            for actor in self.actor_list:
                actor.machine_state()

            if self.main_state == 'play_state':
                for actor in self.actor_list:
                    actor.inherent_natural_action_forces()

                for actor in self.actor_list:
                    actor.update_key_action()

                for actor in self.actor_list:
                    actor.update_ai_action()

                for actor in self.actor_list:
                    actor.update_controller_action()

                for actor in self.actor_list:
                    actor.update_pos()

                for actor in self.actor_list:
                    actor.check_collision_events(self.actor_list)
            elif self.main_state == 'dead_state':
                pass

            self.screen_update()
            time.sleep(1/self.clock_rate)

    def screen_update(self):
        self.screen.fill((0, 0, 0))

        for actor in self.actor_list:
            actor.animation()

        if self.main_state == 'start_state':
            self.screen.blit(self.title, (self.screen_size[0]//2 - self.title.get_width()//2,
                                          self.screen_size[1]//3))
            self.screen.blit(self.push_space, (self.screen_size[0]//2 - self.push_space.get_width()//2,
                                               self.screen_size[1]//2 + self.screen_size[1]//6))
            self.screen.blit(self.pwr_tensorflow, (self.screen_size[0]//2 - self.pwr_tensorflow.get_width()//2,
                                                   self.screen_size[1]//2))
        elif self.main_state == 'play_state':
            self.score = self.score_font.render(str(self.score_value), False, self.font_color)
            self.screen.blit(self.score, (self.screen_size[0]//2 - self.score.get_width()//2,
                                          self.screen_size[1]//20))
        elif self.main_state == 'dead_state':
            self.score = self.score_font.render(str(self.score_value), False, self.font_color)
            self.screen.blit(self.score, (self.screen_size[0]//2 - self.score.get_width()//2,
                                          self.screen_size[1]//2 - self.score.get_height()//2))
            self.screen.blit(self.push_backspace, (self.screen_size[0]//2 - self.push_backspace.get_width()//2,
                                                   self.screen_size[1]//2 + self.screen_size[1]//6))

        self.pygame.display.flip()

    def score_update(self):
        if self.main_state == 'start_state':
            self.start = 0

        elif self.main_state == 'pre_play_state':
            self.start = time.time()

        elif self.main_state == 'play_state':
            self.end = time.time()
            self.score_value = int(100*(self.end - self.start))


# ======================================================================================================================


# screen_1 = PgScreen(screen_size=(1024, 768), noise_std_deviation=0.1)
screen_1 = PgScreen(screen_size=(1000, 800), noise_std_deviation=0.1)

