import os
import random
from random import gauss
import pygame
from DynamicBehaviorPredictor import DynamicBehaviorPredictor


class Actor:
    def __init__(self,
                 surface,
                 surface_size,
                 surface_resistance,
                 id_number,
                 main_state='start_state',
                 category='neutral',
                 color=(0, 255, 0),
                 size=(0, 0),
                 mass=1,
                 default_gravity=9.8,
                 init_resistance=0.01,
                 inherent_natural_action=False,
                 controller=None,
                 init_reaction_effect=False,
                 init_ref_pos=None,
                 init_force=None,
                 init_vel=None,
                 init_pos=None,
                 pixel_meter=10,
                 sample_rate=30,
                 dimension=2,
                 noise_std_deviation=0.1,
                 ai_action=False):

        self.surface = surface
        self.surface_size = surface_size
        self.surface_resistance = surface_resistance
        self.id_number = id_number
        self.main_state = main_state
        self.category = category
        self.color = color
        self.size = size
        self.mass = mass
        self.default_gravity = default_gravity
        self.resistance = init_resistance
        self.inherent_natural_action = inherent_natural_action
        self.controller = controller
        self.reaction_effect = init_reaction_effect
        self.pixel_meter = pixel_meter
        self.sample_rate = sample_rate
        self.sample_period = 1/sample_rate
        self.dimension = dimension
        self.noise_std_deviation = noise_std_deviation
        self.ai_action = ai_action

        if init_force is None:
            self.action_force_input = [0]*self.dimension
        else:
            self.action_force_input = init_force

        self.acl = [self.action_force_input[i]/mass for i in range(self.dimension)]

        if init_vel is None:
            self.vel = [0]*self.dimension
        else:
            self.vel = init_vel

        if init_pos is None:
            self.pos = [dim_size//2 for dim_size in self.surface_size]
        else:
            self.pos = init_pos

        if init_ref_pos is None:
            self.ref_pos = init_pos
        else:
            self.ref_pos = init_ref_pos

    def update_controller_action(self):
        if self.controller is not None:
            self.controller.close_loop_action_control(self, self.ref_pos)

    def update_pos(self):
        for i in range(self.dimension):
            self.acl[i] = (self.action_force_input[i]/self.mass)
            self.vel[i] += self.acl[i] * self.sample_period\
                - self.vel[i]*self.resistance + self.noise
            self.pos[i] += int(self.vel[i] * self.sample_period * self.pixel_meter)

    def check_collision_events(self, actor_list):
        if self.reaction_effect is True:
            for actor in actor_list:
                if actor.reaction_effect is True and actor.id_number != self.id_number:
                    actor.collision(self)
                    self.collision(actor)

    def machine_state(self):
        pass

    def inherent_natural_action_forces(self):
        pass

    def update_key_action(self):
        pass

    def update_ai_action(self):
        pass

    def collision(self, actor):
        pass

    def animation(self):
        pass

    @property
    def noise(self):
        return gauss(mu=0, sigma=self.noise_std_deviation)

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, value):
        if value is not None:
            self._pos = [int(i) for i in value]

    @property
    def ref_pos(self):
        return self._ref_pos

    @ref_pos.setter
    def ref_pos(self, value):
        if value is not None:
            self._ref_pos = [int(i) for i in value]

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, value):
        if value is not None:
            self._size = [int(i) for i in value]

    @property
    def sample_rate(self):
        return int(self._sample_rate)

    @sample_rate.setter
    def sample_rate(self, value):
        self._sample_rate = int(value)
        self.sample_period = 1/value

    @property
    def sample_period(self):
        return self._sample_period

    @sample_period.setter
    def sample_period(self, value):
        self._sample_period = value
        self._sample_rate = 1/value


class Player(Actor):
    def __init__(self,
                 surface,
                 surface_size,
                 surface_resistance,
                 id_number,
                 category='player',
                 default_gravity=9.8,
                 color=(0, 255, 0),
                 size=(15, 15),
                 mass=1,
                 init_resistance=0.01,
                 inherent_natural_action=True,
                 controller=None,
                 init_reaction_effect=True,
                 init_ref_pos=None,
                 init_force=None,
                 init_vel=None,
                 init_pos=None,
                 pixel_meter=10,
                 sample_rate=30,
                 dimension=2,
                 noise_std_deviation=0.1,
                 control_mode='input_force',
                 key_events=True):

        super().__init__(surface,
                         surface_size,
                         surface_resistance,
                         id_number,
                         category=category,
                         default_gravity=default_gravity,
                         color=color,
                         size=size,
                         mass=mass,
                         init_resistance=init_resistance,
                         inherent_natural_action=inherent_natural_action,
                         controller=controller,
                         init_reaction_effect=init_reaction_effect,
                         init_ref_pos=init_ref_pos,
                         init_force=init_force,
                         init_vel=init_vel,
                         init_pos=init_pos,
                         pixel_meter=pixel_meter,
                         sample_rate=sample_rate,
                         dimension=dimension,
                         noise_std_deviation=noise_std_deviation)

        self.control_mode = control_mode
        self.key_events = key_events

    def inherent_natural_action_forces(self):
        if self.inherent_natural_action is True:
            self.action_force_input = [self.noise,
                                       self.default_gravity*self.mass + self.noise]

    def update_key_action(self):
        if self.key_events is True:
            pressed = pygame.key.get_pressed()
            if self.control_mode == 'input_force':
                if pressed[pygame.K_UP]:
                    self.action_force_input[1] -= 700
                if pressed[pygame.K_DOWN]:
                    self.action_force_input[1] += 700
                if pressed[pygame.K_LEFT]:
                    self.action_force_input[0] -= 700
                if pressed[pygame.K_RIGHT]:
                    self.action_force_input[0] += 700
            elif self.control_mode == 'close_loop':
                if pressed[pygame.K_UP]:
                    self.ref_pos[1] -= 5
                if pressed[pygame.K_DOWN]:
                    self.ref_pos[1] += 5
                if pressed[pygame.K_LEFT]:
                    self.ref_pos[0] -= 5
                if pressed[pygame.K_RIGHT]:
                    self.ref_pos[0] += 5

    def collision(self, actor):
        if actor.category == 'side_wall':
            if actor.thickness//2 > self.pos[0]:
                self.action_force_input[0] = 4000
                self.key_events = False
                self.inherent_natural_action = False
                self.resistance = actor.resistance

            elif self.pos[0] > self.surface_size[0] - actor.thickness//2:
                self.action_force_input[0] = -4000
                self.key_events = False
                self.inherent_natural_action = False
                self.resistance = actor.resistance

            elif actor.thickness//2 > self.pos[1]:
                self.action_force_input[1] = 4000
                self.key_events = False
                self.inherent_natural_action = False
                self.resistance = actor.resistance

            elif self.pos[1] > self.surface_size[1] - actor.thickness//2:
                self.action_force_input[1] = -4000
                self.key_events = False
                self.inherent_natural_action = False
                self.resistance = actor.resistance
            else:
                self.key_events = True
                self.inherent_natural_action = True
                self.resistance = self.surface_resistance

    def animation(self):
        if self.main_state == 'start_state':
            pass

        elif self.main_state == 'play_state':
            pygame.draw.circle(self.surface,
                               self.color,
                               self.pos,
                               self.size[0])

        elif self.main_state == 'dead_state':
            pass


class SideWall(Actor):
    def __init__(self,
                 surface,
                 surface_size,
                 surface_resistance,
                 id_number,
                 category='side_wall',
                 default_gravity=9.8,
                 color=(16, 64, 128),
                 size=None,
                 thickness=10,
                 mass=100000,
                 init_resistance=1,
                 inherent_natural_action=False,
                 controller=None,
                 init_reaction_effect=True,
                 init_ref_pos=None,
                 init_force=None,
                 init_vel=None,
                 init_pos=None,
                 pixel_meter=10,
                 sample_rate=30,
                 dimension=2,
                 noise_std_deviation=0.1):

        super().__init__(surface,
                         surface_size,
                         surface_resistance,
                         id_number,
                         category=category,
                         default_gravity=default_gravity,
                         color=color,
                         mass=mass,
                         init_resistance=init_resistance,
                         inherent_natural_action=inherent_natural_action,
                         controller=controller,
                         init_reaction_effect=init_reaction_effect,
                         init_ref_pos=init_ref_pos,
                         init_force=init_force,
                         init_vel=init_vel,
                         init_pos=init_pos,
                         pixel_meter=pixel_meter,
                         sample_rate=sample_rate,
                         dimension=dimension,
                         noise_std_deviation=noise_std_deviation)

        self.start_thickness = 2*surface_size[0]
        self.play_thickness = thickness
        self.thickness = self.start_thickness
        self.animation_period = 10
        self.animation_timer = self.animation_period
        self.animation_complexity = 30
        self.animation_spin = 'up'
        self.animation_complexity_timer = 300

        if size is None:
            self.size = [surface_size[0]-2*thickness,
                         surface_size[1]-2*thickness]
        else:
            self.size = size

        if init_pos is None:
            self.pos = [surface_size[0]//2,
                        surface_size[1]//2]
        else:
            self.pos = init_pos

        self.random_color = []
        for _ in range(self.animation_complexity):
            self.random_color.append([self.color[0] + random.getrandbits(5),
                                      self.color[1] + random.getrandbits(6),
                                      self.color[2] - random.getrandbits(7)])

    def collision(self, actor):
        if actor.category == 'player':
            if self.thickness//2 > actor.pos[0]\
                or actor.pos[0] > self.surface_size[0] - self.thickness//2\
                or self.thickness//2 > actor.pos[1]\
                    or actor.pos[1] > self.surface_size[1] - self.thickness//2:
                self.thickness = self.thickness + 10

    def animation(self):
        for i in range(self.animation_complexity):
            pygame.draw.polygon(self.surface,
                                self.random_color[i],
                                [[self.pos[0] + self.surface_size[0] // 2,
                                  self.pos[0] - self.surface_size[0] // 2],
                                 [self.pos[0] - self.surface_size[0] // 2,
                                  self.pos[1] - self.surface_size[1] // 2],
                                 [self.pos[0] - self.surface_size[0] // 2,
                                  self.pos[1] + self.surface_size[1] // 2],
                                 [self.pos[0] + self.surface_size[0] // 2,
                                  self.pos[1] + self.surface_size[1] // 2]],
                                self.thickness//(i + 1))

    def machine_state(self):
        if self.animation_timer > 0:
            self.animation_timer -= 1

        else:
            self.random_color = []
            for _ in range(self.animation_complexity):
                self.random_color.append([self.color[0] + random.getrandbits(5),
                                          self.color[1] + random.getrandbits(6),
                                          self.color[2] - random.getrandbits(7)])

            self.animation_timer = self.animation_period

        if self.main_state == 'start_state':
            self.thickness = self.start_thickness + self.animation_complexity_timer
            if self.animation_complexity_timer < 0:
                self.animation_spin = 'up'
            elif self.animation_complexity_timer > 300:
                self.animation_spin = 'down'
            if self.animation_spin == 'up':
                self.animation_complexity_timer += 15
            elif self.animation_spin == 'down':
                self.animation_complexity_timer -= 15

        elif self.main_state == 'pre_play_state':
            self.thickness -= 15
            if self.thickness <= self.play_thickness:
                self.thickness = self.play_thickness
                self.main_state = 'play_state'

        elif self.main_state == 'play_state':
            if self.thickness > self.surface_size[0] or self.thickness > self.surface_size[1]:
                self.main_state = 'dead_state'

        elif self.main_state == 'dead_state':
            self.thickness = self.start_thickness + self.animation_complexity_timer
            if self.animation_complexity_timer < 0:
                self.animation_spin = 'up'
            elif self.animation_complexity_timer > 300:
                self.animation_spin = 'down'
            if self.animation_spin == 'up':
                self.animation_complexity_timer += 15
            elif self.animation_spin == 'down':
                self.animation_complexity_timer -= 15


class ComputerAim(Actor):
    def __init__(self,
                 surface,
                 surface_size,
                 surface_resistance,
                 id_number,
                 category='computer_aim',
                 default_gravity=9.8,
                 color=(0, 255, 0),
                 size=[7],
                 mass=0.01,
                 init_resistance=0.1,
                 inherent_natural_action=True,
                 controller=None,
                 init_reaction_effect=True,
                 init_ref_pos=None,
                 init_force=None,
                 init_vel=None,
                 init_pos=None,
                 pixel_meter=10,
                 sample_rate=30,
                 dimension=2,
                 noise_std_deviation=0.1,
                 control_mode='rnn',
                 ai_action=True,
                 ai_target=None):

        super().__init__(surface,
                         surface_size,
                         surface_resistance,
                         id_number,
                         category=category,
                         default_gravity=default_gravity,
                         color=color,
                         mass=mass,
                         init_resistance=init_resistance,
                         inherent_natural_action=inherent_natural_action,
                         controller=controller,
                         init_reaction_effect=init_reaction_effect,
                         init_ref_pos=init_ref_pos,
                         init_force=init_force,
                         init_vel=init_vel,
                         init_pos=init_pos,
                         pixel_meter=pixel_meter,
                         sample_rate=sample_rate,
                         dimension=dimension,
                         noise_std_deviation=noise_std_deviation,
                         ai_action=ai_action)

        self.radius = size[0]
        self.control_mode = control_mode
        self.ai_target = ai_target
        self.shot_area = 20
        self.shot_period = 6
        self.shot_timer = int(abs(self.shot_period * self.noise) + 2*self.shot_period)
        self.shot_pos = [pos for pos in self.pos]
        self.aim_state = 'loading'

        self.shot_hit_image_set_path = 'warped_city_files/SPRITES/misc/enemy-explosion'
        self.shot_hit_image_set = []

        image_path = os.path.join(self.shot_hit_image_set_path, 'enemy-explosion-1.png')
        self.shot_hit_image_set.append(pygame.image.load(image_path))
        image_path = os.path.join(self.shot_hit_image_set_path, 'enemy-explosion-2.png')
        self.shot_hit_image_set.append(pygame.image.load(image_path))
        image_path = os.path.join(self.shot_hit_image_set_path, 'enemy-explosion-3.png')
        self.shot_hit_image_set.append(pygame.image.load(image_path))
        image_path = os.path.join(self.shot_hit_image_set_path, 'enemy-explosion-4.png')
        self.shot_hit_image_set.append(pygame.image.load(image_path))
        image_path = os.path.join(self.shot_hit_image_set_path, 'enemy-explosion-5.png')
        self.shot_hit_image_set.append(pygame.image.load(image_path))
        image_path = os.path.join(self.shot_hit_image_set_path, 'enemy-explosion-6.png')
        self.shot_hit_image_set.append(pygame.image.load(image_path))
        self.animation_complexity = 6
        self.animation_count = 0

        if control_mode == 'rnn':
            self.ai_controller = DynamicBehaviorPredictor(surface_size=self.surface_size,
                                                          num_y_pred_output=5,
                                                          num_neurons=200)
            self.ai_controller.start_train_and_predict_thread()

    def inherent_natural_action_forces(self):
        if self.inherent_natural_action is True:
            self.action_force_input = [self.noise,
                                       self.noise]

    def update_ai_action(self):
        if self.ai_action is True and self.ai_target is not None:
            self.ai_controller.set_data_to_train([self.ai_target.pos[0],
                                                  self.ai_target.pos[1]])
            self.ref_pos = self.ai_controller.y_print[-1][-1]

    def collision(self, actor):
        if self.main_state == 'play_state':
            if actor.category == 'player':
                if self.aim_state == 'fire':
                    if self.shot_pos[0]+self.shot_area > actor.pos[0] > self.shot_pos[0]-self.shot_area and \
                            self.shot_pos[1]+self.shot_area > actor.pos[1] > self.shot_pos[1]-self.shot_area:
                        self.main_state = 'dead_state'

    def machine_state(self):
        if self.main_state == 'play_state':
            if self.aim_state == 'standby' or self.aim_state == 'fire' or self.aim_state == 'boom':
                if self.shot_timer > self.shot_period:
                    self.aim_state = 'standby'
                    self.shot_timer -= 1
                elif self.shot_timer > self.shot_period-1:
                    self.aim_state = 'fire'
                    self.shot_timer -= 1
                    self.shot_pos = [pos for pos in self.pos]
                elif self.shot_timer > 0:
                    self.aim_state = 'boom'
                    self.shot_timer -= 1
                else:
                    self.aim_state = 'loading'
                    self.shot_timer = int(abs(self.shot_period * self.noise) + 2*self.shot_period)

            elif self.aim_state == 'loading':
                if self.ai_controller.service_status == 'online':
                    self.aim_state = 'standby'

    def animation(self):
        if self.main_state == 'start_state':
            pass

        elif self.main_state == 'play_state':
            if self.aim_state == 'standby':
                pass
            elif self.aim_state == 'fire':
                self.animation_count = 0
                pygame.draw.circle(self.surface,
                                   (255, 255, 0),
                                   self.shot_pos,
                                   4*self.shot_period//(self.shot_timer+1),
                                   3)

            elif self.aim_state == 'boom':
                if self.animation_count < self.animation_complexity:
                    self.surface.blit(self.shot_hit_image_set[self.animation_count], self.shot_pos)
                    self.animation_count += 1

            for i, predict in enumerate(self.ai_controller.y_print[-1][-5:][:]):
                pygame.draw.circle(self.surface,
                                   (51*i, 0, 0),
                                   predict,
                                   self.radius,
                                   i+1)

            pygame.draw.circle(self.surface,
                               self.color,
                               self.pos,
                               self.radius)

            pygame.draw.circle(self.surface,
                               self.color,
                               self.pos,
                               10*self.radius,
                               3)

            pygame.draw.circle(self.surface,
                               self.color,
                               self.pos,
                               int((abs(self.vel[0]*self.vel[1]))**(1/2))+10,
                               3)

            pygame.draw.circle(self.surface,
                               self.color,
                               self.pos,
                               int((abs(self.vel[0]*self.vel[1]))**(1/3))+10,
                               4)

            pygame.draw.rect(self.surface,
                             self.color,
                             [self.pos[0]-12*self.radius,
                              self.pos[1]-2,
                              24*self.radius,
                              4])

            pygame.draw.rect(self.surface,
                             self.color,
                             [self.pos[0]-2,
                              self.pos[1]-12*self.radius,
                              4,
                              24*self.radius])

            pygame.draw.rect(self.surface,
                             [self.color[0]//2, self.color[1]//2, self.color[2]//2],
                             [self.pos[0]-12*self.radius+1,
                              self.pos[1]-1,
                              24*self.radius+2,
                              2])

            pygame.draw.rect(self.surface,
                             [self.color[0]//2, self.color[1]//2, self.color[2]//2],
                             [self.pos[0]-1,
                              self.pos[1]-12*self.radius+1,
                              2,
                              24*self.radius+2])

            pygame.draw.circle(self.surface,
                               [self.color[0]//3, self.color[1]//3, self.color[2]//3],
                               self.pos,
                               self.radius//2,
                               3)

            pygame.draw.circle(self.surface,
                               [self.color[0]//10, self.color[1]//10, self.color[2]//10],
                               self.pos,
                               self.radius//2)

        elif self.main_state == 'dead_state':
            pass










