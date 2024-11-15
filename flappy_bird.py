import pygame
import random
import sys

pygame.init()

window_width = 480
window_height = 620

window = pygame.display.set_mode((window_width,window_height))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
fps = 60
running = True
base_image = pygame.image.load("Bitmaps/base.png").convert_alpha()
base_image = pygame.transform.smoothscale(base_image,(window_width,base_image.get_height()))
background_image = pygame.image.load("Bitmaps/background-day.png").convert_alpha()
background_image = pygame.transform.smoothscale(background_image,(window_width,window_height-base_image.get_height()))
bird_down_image = pygame.image.load("Bitmaps/yellowbird-downflap.png").convert_alpha()
bird_down_image = pygame.transform.smoothscale_by(bird_down_image,1.6)
bird_up_image = pygame.image.load("Bitmaps/yellowbird-upflap.png").convert_alpha()
bird_up_image = pygame.transform.smoothscale_by(bird_up_image,1.6)
bird_mid_image = pygame.image.load("Bitmaps/yellowbird-midflap.png").convert_alpha()
bird_mid_image = pygame.transform.smoothscale_by(bird_mid_image,1.6)
game_over_image = pygame.image.load("Bitmaps/gameover.png").convert_alpha()
bird_rotated_image = pygame.transform.rotate(bird_mid_image,-90)
start_image = pygame.image.load("Bitmaps/message.png").convert_alpha()
pipe_image_bottom = pygame.image.load("Bitmaps/pipe-green.png").convert_alpha()
pipe_image_top = pygame.transform.flip(pipe_image_bottom,False,True)
pipe_gap = 160
pipe_freq = 1.3
joysticks = []

class Animation():
    def __init__(self,images,max_count=0):
        self.index = 0
        self.counter = 0
        self.max_count = max_count
        self.frames = images
        self.image = self.frames[self.index]

    def update(self):
        self.counter+=1
        if self.counter > self.max_count:
            self.index += 1
            if self.index > len(self.frames)-1:
                self.index = 0
            self.image = self.frames[self.index]
            self.counter = 0

class Pipe():
    def __init__(self,x,y,position):
        self.image = pipe_image_top
        self.rect = self.image.get_rect()
        if position == 1:
            self.image = pipe_image_top
            self.rect.bottomleft = (x,y-int(pipe_gap / 2))
        if position == -1:
            self.image = pipe_image_bottom
            self.rect.topleft = (x,y+int(pipe_gap / 2))
        self.vel_x = 2

    def update(self):
        self.rect.x -= self.vel_x

    def draw(self):
        window.blit(self.image,self.rect)

class Bird():
    def __init__(self,game):
        self.game = game
        self.animations = {"flying":Animation((bird_down_image.copy(),bird_mid_image.copy(),
                          bird_up_image.copy()),5),"collided":Animation((bird_rotated_image,))}
        self.animation = self.animations["flying"]
        self.rect = self.animation.image.get_rect()
        self.x = 90
        self.y = 200
        self.vel_y = 0
        self.rect.centerx = self.x
        self.rect.centery = self.y
        self.jump_power = 12
        self.game_started = False
        self.game_over = False
        self.jump_sound = pygame.mixer.Sound("Sounds/wing.wav")
        self.hit_sound = pygame.mixer.Sound("Sounds/hit.wav")

    def jump(self):
        self.vel_y = -self.jump_power
        self.jump_sound.play()
        self.game_started = True

    def collide_with_pipes(self):
         for pipe in self.game.pipes:
            if pipe.rect.colliderect(self.rect):
                self.game.base_vel_x = 0
                if not self.game_over:
                    game.can_flash = True
                    self.hit_sound.play()
                self.game_over = True
                self.animation = self.animations["collided"]
                for pipe in self.game.pipes:
                    pipe.vel_x = 0

    def collide_with_floor(self):
        if game.base_rect.colliderect(self.rect):
            if not self.game_over:
                self.hit_sound.play()
                self.game.can_flash = True
            self.game.base_vel_x = 0
            self.animation = self.animations["collided"]
            self.rect.bottom = game.base_rect.top
            self.vel_y = 0
            self.game_over = True
            for pipe in self.game.pipes:
                pipe.vel_x = 0
        if game.second_base_rect.colliderect(self.rect):
            if not self.game_over:
                self.game.can_flash = True
                self.hit_sound.play()
            self.game.base_vel_x = 0
            self.animation = self.animations["collided"]
            self.rect.bottom = game.second_base_rect.top
            self.vel_y = 0
            self.game_over = True
            for pipe in self.game.pipes:
                pipe.vel_x = 0

    def update(self):
        self.animation.update()
        self.rect = self.animation.image.get_rect()
        self.rect.centerx = self.x
        self.y += self.vel_y
        self.rect.centery = self.y
        if self.game_started:
            self.vel_y += 1.4
            if self.vel_y > 35:
              self.vel_y = 35
            if self.rect.y < 0:
                if not self.game_over: 
                    self.game.can_flash = True
                    self.hit_sound.play()
                self.game.base_vel_x = 0
                self.animation = self.animations["collided"]
                self.game_over = True
            self.collide_with_pipes()
            self.collide_with_floor()

    def draw(self):
        window.blit(self.animation.image,self.rect)

class MainMenu():
    def __init__(self):
        self.alpha = 255
        self.start_menu = True
        self.in_game = False
        self.swoosh_sound = pygame.mixer.Sound("Sounds/swoosh.wav")
        self.mm_font = pygame.font.Font("Fonts/flappy font.ttf",100)
        self.title_image = self.mm_font.render("Flappy Bird",True,(255,255,255))
        self.title_rect = self.title_image.get_rect()
        self.title_x = 100
        self.title_y = 100
        self.accel = 0.25
        self.vel_y = 0
        self.bird_animation = Animation((bird_down_image,bird_mid_image,bird_up_image),5)
        self.bird_animation_rect = self.bird_animation.image.get_rect()
        self.bird_animation_rect.x = 210
        self.bird_animation_rect.y = 210

    def start_game(self):
        self.swoosh_sound.play()
        self.start_menu = False

    def update(self):
        self.vel_y += self.accel
        if self.vel_y > 4.5:
            self.accel = -0.5
        if self.vel_y < -4.5:
            self.accel = 0.5
        self.bird_animation.update()
        self.bird_animation_rect = self.bird_animation.image.get_rect()
        self.bird_animation_rect.x = 210
        self.bird_animation_rect.y = 210 + self.vel_y
        if not self.start_menu:
            self.alpha -= 14
            if self.alpha < 0:
                self.alpha = 255
                self.in_game = True

    def draw(self):
        if not self.in_game:
            window.blit(self.title_image,(self.title_x,self.title_y+self.vel_y))
            window.blit(self.bird_animation.image,self.bird_animation_rect)
        
class Game():
    def __init__(self):
        pygame.mouse.set_visible(False)
        window_icon = pygame.image.load("Bitmaps/icon.ico")
        pygame.display.set_icon(window_icon)
        self.base_vel_x = 4
        self.base_rect = base_image.get_rect()
        self.base_width = self.base_rect.width
        self.base_height = self.base_rect.height
        self.base_rect.x = 0
        self.base_rect.y = window_height - self.base_rect.height
        self.second_base_rect = base_image.get_rect()
        self.second_base_rect.x = window_width
        self.second_base_rect.y = window_height - self.base_rect.height
        self.main_menu = MainMenu()
        self.start_image_rect = start_image.get_rect()
        self.start_image_rect.x = 145
        self.start_image_rect.y = 220
        self.start_image_alpha = 255
        self.make_invisible = False
        self.pipes = []
        self.score_pipes = []
        self.bird = Bird(self)
        self.last_pipe = (pygame.time.get_ticks()/1000)-pipe_freq
        self.score_font = pygame.font.Font("Fonts/score font.ttf",40)
        self.score = 0
        self.score_image = self.score_font.render(str(self.score),True,(255,255,255))
        self.score_rect = self.score_image.get_rect()
        self.score_rect.centerx = 240
        self.score_rect.centery = 60
        self.score_sound = pygame.mixer.Sound("Sounds/point.wav")
        self.alpha = 255
        self.reset_game = False
        self.can_flash = False
        self.flash_time = 0
        self.flash_image = pygame.Surface((window_width,window_height))
        self.flash_image.fill((255,255,255))
        self.set_go_ease_settings()

    def set_go_ease_settings(self):
        self.go_ease = 0.1
        self.game_over_x = 140
        self.game_over_y = 250
        self.game_over_rect = game_over_image.get_rect()
        self.game_over_rect.x = 140
        self.game_over_rect.y = 350

    def spawn_pipes(self):
        if pygame.time.get_ticks()/1000 - self.last_pipe > pipe_freq:
            pipe_height = random.randint(-70,70)
            bottom_pipe = Pipe(window_width,int(window_height/2)+pipe_height,-1)
            top_pipe = Pipe(window_width,int(window_height/2)+pipe_height,1)
            self.pipes.append(bottom_pipe)
            self.pipes.append(top_pipe)
            self.score_pipes.append((bottom_pipe,top_pipe))
            self.last_pipe = pygame.time.get_ticks()/1000

    def move_pipes(self):
        for pipe in self.pipes[:]:
            pipe.update()
            if pipe.rect.x + pipe.rect.width < 0:
                self.pipes.remove(pipe)

    def move_base(self):
        self.base_rect.x -= self.base_vel_x
        self.second_base_rect.x -= self.base_vel_x
        if self.base_rect.x <= -self.base_width:
            self.base_rect.x = 0
            self.second_base_rect.x = window_width

    def add_score(self):
        for bottom_pipe, top_pipe in self.score_pipes[:]:
            if bottom_pipe.rect.x + bottom_pipe.rect.width // 2 < self.bird.rect.x + self.bird.rect.width // 2:
                self.score+=1
                self.score_sound.play()
                self.score_image = self.score_font.render(str(self.score),True,(255,255,255))
                self.score_pipes.remove((bottom_pipe,top_pipe))

    def restart(self):
        bird_mid_image.set_alpha(255)
        bird_up_image.set_alpha(255)
        bird_down_image.set_alpha(255)
        bird_rotated_image.set_alpha(255)
        self.bird = Bird(self)
        self.pipes.clear()
        self.score_pipes.clear()
        self.score = 0
        self.can_flash = False
        self.base_vel_x = 4
        self.score_image = self.score_font.render(str(self.score),True,(255,255,255))
        self.start_image_alpha = 255
        self.reset_game = False
        self.set_go_ease_settings()
        self.make_invisible = False

    def ease_go_image(self):
        dx = self.game_over_x - self.game_over_rect.x
        dy = self.game_over_y - self.game_over_rect.y
        if abs(dx) < 0.1 and abs(dy) < 0.1:
            self.game_over_rect.x = self.game_over_x
            self.game_over_rect.y = self.game_over_y
        vel_x = dx * self.go_ease
        vel_y = dy * self.go_ease
        self.game_over_rect.x += vel_x
        self.game_over_rect.y += vel_y
        
    def update(self):
        if not self.main_menu.in_game:
            self.main_menu.update()
        else:
            if self.make_invisible:
                if not self.bird.game_over:
                    self.base_vel_x = 2
                    self.spawn_pipes()
                    self.move_pipes()
                    self.add_score()
                if self.reset_game:
                    self.restart()
                self.start_image_alpha -= 5
                if self.start_image_alpha < 0:
                    self.start_image_alpha = 0
                if self.bird.game_over:
                    self.ease_go_image()
            self.bird.update()
        self.move_base()

    def draw_base(self):
        window.blit(base_image,self.base_rect)
        window.blit(base_image,self.second_base_rect)

    def draw_background(self):
        background_image.set_alpha(self.main_menu.alpha)
        base_image.set_alpha(self.main_menu.alpha)
        self.main_menu.title_image.set_alpha(self.main_menu.alpha)
        self.main_menu.bird_animation.image.set_alpha(self.main_menu.alpha)
        window.fill((0,0,0),pygame.Rect(0,0,window_width,window_height))
        window.blit(background_image,(0,0))

    def draw_start_image(self):
        window.blit(start_image,self.start_image_rect)
        start_image.set_alpha(self.start_image_alpha)

    def draw_pipes(self):
        for pipe in self.pipes:
            pipe.draw()

    def display_score(self):
        window.blit(self.score_image,self.score_rect)

    def flash_screen(self):
        window.blit(game_over_image,self.game_over_rect)
        if self.can_flash:
            self.flash_time = pygame.time.get_ticks()/1000
            self.can_flash = False
            self.flash = True
        if self.flash:
             if pygame.time.get_ticks()/1000 - self.flash_time > 0.05:
                 self.flash_time = pygame.time.get_ticks()/1000
                 self.flash = False
             window.blit(self.flash_image,(0,0))

    def draw(self):
        self.draw_background()
        if not self.main_menu.in_game:
            self.draw_base()
            self.main_menu.draw()
        else:
            self.draw_start_image()
            self.draw_pipes()
            self.draw_base()
            self.bird.draw()
            self.display_score()
            if self.bird.game_over:
                self.flash_screen()
                
game = Game()

while running:
    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.JOYDEVICEADDED:
            joystick = pygame.joystick.Joystick(event.device_index)
            joysticks.append(joystick)
        if event.type == pygame.KEYDOWN and game.main_menu.start_menu:
            if event.key == pygame.K_SPACE:
                game.main_menu.start_game()
        elif event.type == pygame.JOYBUTTONDOWN and event.button == 0 and game.main_menu.start_menu:
            game.main_menu.start_game()
        elif event.type == pygame.KEYDOWN and not game.main_menu.start_menu and not game.bird.game_over:
            if event.key == pygame.K_SPACE:
                game.make_invisible = True
                game.bird.jump()
        elif event.type == pygame.JOYBUTTONDOWN and event.button == 0 and not game.main_menu.start_menu and not game.bird.game_over:
            game.make_invisible = True
            game.bird.jump()
        elif event.type == pygame.KEYDOWN and not game.reset_game and game.bird.game_over:
            if event.key == pygame.K_e:
                game.main_menu.swoosh_sound.play()
                game.reset_game = True
        elif event.type == pygame.JOYBUTTONDOWN and event.button == 1 and not game.reset_game and game.bird.game_over:
                game.main_menu.swoosh_sound.play()
                game.reset_game = True
    game.update()
    game.draw()
    pygame.display.update()
    
pygame.quit()
sys.exit()
