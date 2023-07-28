import pygame, random, time

#game classes
class Player:
    def __init__(self, position, color):
        self.position = position
        self.speed = 500
        self.projectile_speed = 750
        self.color = color
        self.projectile_cooldown = 500
        self.last_projectile_time = 0
        self.last_Direction = 'w'
        self.score = 0
        self.radius = 20
        self.can_move = True

    def move(self, keys, dt, screen_width, screen_height):
        if not self.can_move:
            return

        if keys[pygame.K_w]:
            self.position.y -= self.speed * dt
            self.last_Direction = 'w'
            if self.position.y < 0:
                self.position.y = screen_height
        if keys[pygame.K_s]:
            self.position.y += self.speed * dt
            self.last_Direction = 's'
            if self.position.y > screen_height:
                self.position.y = 0
        if keys[pygame.K_a]:
            self.position.x -= self.speed * dt
            self.last_Direction = 'a'
            if self.position.x < 0:
                self.position.x = screen_width
        if keys[pygame.K_d]:
            self.position.x += self.speed * dt
            self.last_Direction = 'd'
            if self.position.x > screen_width:
                self.position.x = 0
        #for diagonal projectiles and pupil
        if keys[pygame.K_w] and keys[pygame.K_a]:
            self.last_Direction = 'wa'
        if keys[pygame.K_w] and keys[pygame.K_d]:
            self.last_Direction = 'wd'
        if keys[pygame.K_s] and keys[pygame.K_a]:
            self.last_Direction = 'sa'
        if keys[pygame.K_s] and keys[pygame.K_d]:
            self.last_Direction = 'sd'

    def draw(self, surface):
        #main circle
        pygame.draw.circle(surface, self.color, self.position, 20)

        #pupil
        match self.last_Direction:
            case 'w':
                pygame.draw.circle(surface, 'black', (self.position.x, self.position.y - 13), 7)
            case 's':
                pygame.draw.circle(surface, 'black', (self.position.x, self.position.y + 13), 7)
            case 'a':
                pygame.draw.circle(surface, 'black', (self.position.x - 13, self.position.y), 7)
            case 'd':
                pygame.draw.circle(surface, 'black', (self.position.x + 13, self.position.y), 7)
            case 'wa':
                pygame.draw.circle(surface, 'black', (self.position.x - 9, self.position.y - 9), 7)
            case 'wd':
                pygame.draw.circle(surface, 'black', (self.position.x + 9, self.position.y - 9), 7)
            case 'sa':
                pygame.draw.circle(surface, 'black', (self.position.x - 9, self.position.y + 9), 7)
            case 'sd':
                pygame.draw.circle(surface, 'black', (self.position.x + 9, self.position.y + 9), 7)
    
    def can_shoot(self):
        current_time = pygame.time.get_ticks()
        return current_time - self.last_projectile_time > self.projectile_cooldown

    def shoot(self):
        if self.can_shoot():
            projectile_Sound.play()
            self.last_projectile_time = pygame.time.get_ticks()
            projectile_velocity = self.projectile_speed

            #shoot the direction player is pointing
            match self.last_Direction:
                case 'w':
                    projectile_Direction = pygame.Vector2(0, -projectile_velocity)
                case 's':
                    projectile_Direction = pygame.Vector2(0, projectile_velocity)
                case 'a':
                    projectile_Direction = pygame.Vector2(-projectile_velocity, 0)
                case 'd':
                    projectile_Direction = pygame.Vector2(projectile_velocity, 0)
                case 'wa':
                    projectile_Direction = pygame.Vector2(-projectile_velocity, -projectile_velocity)
                case 'wd':
                    projectile_Direction = pygame.Vector2(projectile_velocity, -projectile_velocity)
                case 'sa':
                    projectile_Direction = pygame.Vector2(-projectile_velocity, projectile_velocity)
                case 'sd':
                    projectile_Direction = pygame.Vector2(projectile_velocity, projectile_velocity)

            new_projectile = Projectile(self.position.copy(), projectile_Direction)
            projectiles.append(new_projectile)

class Enemy:
    def __init__(self, count):
        enemy_Triange = [(0, -15), (15, 15), (-15, 15)]
        enemy_Square = [(-15,15), (15,15), (15,-15), (-15,-15)]
        enemy_Pentagon = [(0,-15), (15,0), (7.5, 15), (-7.5, 15), (-15,0)]
        enemy_Hexagon = [(7.5,15), (15,0), (7.5,-15), (-7.5,-15), (-15,0), (-7.5,15)]
        enemy_Shapes = [enemy_Triange, enemy_Square, enemy_Pentagon, enemy_Hexagon]

        enemy_Colors = ['orangered','orangered1','orangered2','orangered3','orangered4','red','red1','red2','red3','red4']
        enemy_Spawns = [(0, 0), (screen.get_width(), 0), (0, screen.get_height()),
                        (screen.get_width(), screen.get_height()), (0, screen.get_height() / 2), 
                        (screen.get_width(), screen.get_height() / 2), (screen.get_width() / 2, 0), 
                        (screen.get_width() / 2, screen.get_height())]

        self.vertices = enemy_Shapes[random.randint(0,len(enemy_Shapes)-1)]
        self.position = pygame.Vector2(enemy_Spawns[random.randint(0,len(enemy_Spawns)-1)])
        self.color = enemy_Colors[random.randint(0,len(enemy_Colors)-1)]
        self.temp_color = self.color
        self.count = count
        self.speed = 200 + count
        self.jitter = 100 + (count * 10)
        self.radius = 20
        self.can_move = True
        self.is_dead = False
        self.dead_color = 255
        self.is_frozen = False
        self.frozen_start = 0
        self.frozen_end = 0
        self.boss_exists = False

    def move(self, player_pos, dt):
        enemy_speed = self.speed

        if not self.can_move or self.is_dead or self.is_frozen:
            return
        
        if self.jitter < 400:
            self.jitter += (1/40)

        random_Offset = random.randint(0,int(self.jitter))
        if random_Offset % 2 == 0:
            enemy_speed += random_Offset
        else:
            enemy_speed -= random_Offset

        if not self.boss_exists:
            if player_pos.x > self.position.x:
                self.position.x += enemy_speed * dt
            if player_pos.x < self.position.x:
                self.position.x -= enemy_speed * dt
            if player_pos.y > self.position.y:
                self.position.y += enemy_speed * dt
            if player_pos.y < self.position.y:
                self.position.y -= enemy_speed * dt
        else:
            if screen.get_width() / 2 > self.position.x:
                self.position.x -= enemy_speed * dt * 1.25
            if screen.get_width() / 2 < self.position.x:
                self.position.x += enemy_speed * dt * 1.25
            if screen.get_height() + 50 > self.position.y:
                self.position.y += enemy_speed * dt * 1.25

    def draw(self, surface):
        if self.is_frozen:
            self.color = 'blue'
            self.frozen_end = time.time()
            time_frozen = self.frozen_end - self.frozen_start

            if time_frozen > 10:
                self.is_frozen = False
        else:
            self.color = self.temp_color

        if self.is_dead:
            self.dead_color -= 1
            if self.dead_color < 0:
                return False
            
            self.color = (self.dead_color,self.dead_color,self.dead_color)

        translated_vertices = [tuple(vec + self.position) for vec in self.vertices]
        pygame.draw.polygon(surface, self.color, translated_vertices)
        return True
    
    def collides_with(self, player):
        if self.is_dead or self.is_frozen:
            return

        distance = pygame.Vector2.distance_to(player.position, self.position)
        return distance <= player.radius
        return False #god mode
    
    def die(self):
        enemy_die_Sound.play()
        
        self.is_dead = True

class Projectile:
    def __init__(self, position, velocity, type='Player'):
        self.position = position
        self.velocity = velocity
        self.color = 'white'
        self.size = 5
        self.can_move = True
        self.type = type
        self.last_color_change = 0
        self.radius = 5
        if self.type == 'Player':
            self.color_cooldown = 100
        else:
            self.color_cooldown = 212
        self.color_bool = True

    def update(self, dt):
        if not self.can_move:
            return
        
        self.position += self.velocity * dt

    def draw(self, surface):
        current_time = pygame.time.get_ticks()
        dif = current_time - self.last_color_change

        if dif > self.color_cooldown:
            if self.color_bool and self.type == 'Player':
                self.color = 'deepskyblue'
                self.size = 10
                self.color_bool = False
            elif self.color_bool and self.type == 'Boss':
                self.color = 'crimson'
                self.size = 10
                self.color_bool = False
            else:
                self.color = 'white'
                self.size = 5
                self.color_bool = True
            self.last_color_change = current_time

        pygame.draw.circle(surface, self.color, (int(self.position.x), int(self.position.y)), self.size)

    def collides_with(self, enemy):
        if self.type == 'Player':
            if not enemy.is_dead:
                if enemy.color == 'brown2': #is a boss
                    if enemy.intro_complete:
                        distance = pygame.Vector2.distance_to(enemy.position, self.position)
                        return distance <= enemy.radius + 5
                else:
                    distance = pygame.Vector2.distance_to(enemy.position, self.position)
                    return distance <= enemy.radius + 5
        elif self.type == 'Boss':
            distance = pygame.Vector2.distance_to(enemy.position, self.position)
            return distance <= enemy.radius

class Powerup:
    def __init__(self, screen, type):
        rand_x = random.randint(10, screen.get_width() - 10)
        rand_y = random.randint(10, screen.get_height() - 10)
        self.position = pygame.Vector2(rand_x, rand_y)
        self.is_active = True
        self.start_Time = time.time()
        self.type = type
        self.color = (0,0,0)

    def collides_with(self, player):
        if not self.is_active:
            return
        
        distance = pygame.Vector2.distance_to(player.position, self.position)

        return distance <= player.radius + 10
    
    def draw(self, screen):
        #powerup color and timing logic
        end_Time = time.time()
        time_Active = end_Time - self.start_Time

        #timeout after 6 seconds
        if time_Active > 6:
                self.is_active = False

        if not self.is_active:
            return
        
        #powerup types
        match self.type:
            case 'Frozen':
                self.color = 'dodgerblue'

                if round(time_Active,0) % 2 == 0:
                    self.color = 'white'
                else:
                    self.color = 'dodgerblue'

            case 'Shooting':
                if self.color[1] < 255:
                    self.color = (0,self.color[1]+1,0)
                elif self.color[2] < 255:
                    self.color = (0,self.color[1],self.color[2]+1)
                elif self.color[0] < 255:
                    self.color = (self.color[0]+1,self.color[1],self.color[2])

            case 'Speed':
                if round(time_Active,0) % 2 == 0:
                    self.color = 'aquamarine1'
                else:
                    self.color = 'gold'

        #draw
        pygame.draw.circle(screen, self.color, (self.position.x, self.position.y), 10)

class Boss:
    def __init__(self, health):
        self.position = pygame.Vector2(screen.get_width() / 2,-screen.get_width() * 1.125 - 75)
        self.color = 'brown2' #this is not brown lol
        self.speed = 10
        self.health = health
        self.max_health = self.health
        self.radius = screen.get_width() * 1.125
        self.shake_dir = 'left'
        self.intro_complete = False
        self.timer = 0
        self.projectile_cooldown = 1000
        self.projectile_speed = 200
        self.last_projectile_time = 0
        self.speed = 40
        self.direction = 2
        self.dir_inout = True
        self.alternate = True
        self.is_dead = False
        self.can_move = True
        self.health_color = (0,0,0)
        self.dead_color = 255
          
    def draw(self, surface, dt):
        if not self.can_move:
            self.intro_complete = True

        if not self.intro_complete:
            if self.position.y < (-screen.get_width()):
                self.position.y += self.speed * dt

                #shake logic
                random_delay = 12
                random_dist = random.randint(10,15)

                if self.timer % random_delay == 0:
                    if self.shake_dir == 'left':
                        self.shake_dir = 'right'
                        self.position.x = (screen.get_width() / 2) + random_dist
                    else:
                        self.shake_dir = 'left'
                        self.position.x = (screen.get_width() / 2) - random_dist
                
                if self.health_color[1] < 255:
                    self.health_color = (0,self.health_color[1] + 0.25,0)

                self.timer += 1
            else:
                self.intro_complete = True
        else:
            if self.can_move:
                self.shoot()

        if self.health <= 0:
            self.is_dead = True

        if self.is_dead:
            self.dead_color -= 0.5
            if self.dead_color < 0:
                return False
            
            self.color = (self.dead_color,self.dead_color,self.dead_color)

        pygame.draw.circle(surface, self.color, self.position, self.radius)

        #health bar
        rect_width, rect_height = 1000, 20
        rect_x = (screen.get_width() - rect_width) // 2
        rect_y = 20
        ratio = self.health / self.max_health
        total_rect_dimensions = (rect_x, rect_y, rect_width, rect_height)
        remaining_rect_dimensions = (rect_x, rect_y, rect_width * ratio, rect_height)
        pygame.draw.rect(surface, 'black', total_rect_dimensions)
        pygame.draw.rect(surface, self.health_color, remaining_rect_dimensions)

        return True

    def shoot(self):
        if self.can_shoot():
            projectile_Sound.play()
            self.last_projectile_time = pygame.time.get_ticks()
            projectile_velocity = self.projectile_speed
            projectile_right = pygame.Vector2(projectile_velocity/self.direction, projectile_velocity)
            projectile_left = pygame.Vector2(-projectile_velocity/self.direction, projectile_velocity)
            projectile_down = pygame.Vector2(0, projectile_velocity)

            #this is a mess
            projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 - 0, 0), projectile_down, 'Boss'))

            if self.alternate:
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 - 350, 0), projectile_right, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 - 750, 0), projectile_right, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 + 50, 0), projectile_right, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 + 450, 0), projectile_right, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 + 850, 0), projectile_right, 'Boss'))

                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 + 350, 0), projectile_left, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 + 750, 0), projectile_left, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 - 50, 0), projectile_left, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 - 450, 0), projectile_left, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 - 850, 0), projectile_left, 'Boss'))

                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 - 500, 0), projectile_down, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 - 1000, 0), projectile_down, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 + 500, 0), projectile_down, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 + 1000, 0), projectile_down, 'Boss'))
                self.alternate = False
            else:
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 - 150, 0), projectile_right, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 - 550, 0), projectile_right, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 - 950, 0), projectile_right, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 + 250, 0), projectile_right, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 + 650, 0), projectile_right, 'Boss'))

                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 + 150, 0), projectile_left, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 + 550, 0), projectile_left, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 + 950, 0), projectile_left, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 - 250, 0), projectile_left, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 - 650, 0), projectile_left, 'Boss'))

                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 - 250, 0), projectile_down, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 - 750, 0), projectile_down, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 + 250, 0), projectile_down, 'Boss'))
                projectiles.append(Projectile(pygame.Vector2(screen.get_width() / 2 + 750, 0), projectile_down, 'Boss'))
                self.alternate = True

            if self.dir_inout:
                self.direction += 1
                if self.direction > 8:
                    self.dir_inout = False
            else:
                self.direction -= 1
                if self.direction <= 1:
                    self.dir_inout = True
    
    def can_shoot(self):
        if self.is_dead:
            return False
        
        current_time = pygame.time.get_ticks()
        return current_time - self.last_projectile_time > self.projectile_cooldown

    def collides_with(self, player):
        if self.is_dead:
            return

        distance = pygame.Vector2.distance_to(player.position, self.position)
        return distance <= self.radius + 20

#game functions
def reset_game(boss_Count):
    #resets game after player death
    player.score = 0
    enemies.clear()
    projectiles.clear()
    powerUps.clear()
    the_boss.clear()
    background_sound.set_volume(0.75) #0.75
    player.position = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    player.can_move = True
    player.projectile_cooldown = 500
    player.speed = 500
    player.projectile_speed = 750
    if boss_Count > 0:
        boss_sound.stop()
        background_sound.play(-1)

    for i in range(4):
        enemies.append(Enemy(len(enemies)))

def powerup_spawn(type):
    #every 5 points there is a 25% chance for a Powerup Shooting
    if player.score % 5 == 0:
        powerup_roll = random.randint(1,100)
        if powerup_roll < 25: #25
            match type:
                case 'Shooting':
                    if player.projectile_cooldown > 100:
                        powerUps.append(Powerup(screen, type))
                case 'Speed':
                    if player.speed < 700:
                        powerUps.append(Powerup(screen, type))
                case _:
                    powerUps.append(Powerup(screen, type))

def powerup_logic(powerUps):
    for powerup in powerUps:
        powerup.draw(screen)
        if powerup.collides_with(player):
            powerUps.remove(powerup)

            #removes 25 from shooting cooldown, down to 100
            if powerup.type == 'Shooting':
                powerup_sound_shooting.play()
                if player.projectile_cooldown > 100:
                    player.projectile_cooldown -= 25
                    if player.projectile_cooldown < 100:
                        player.projectile_cooldown = 100
            
            #freezes enemies
            if powerup.type == 'Frozen':
                powerup_sound_frozen.play()
                for enemy in enemies:
                    enemy.is_frozen = True
                    enemy.frozen_start = time.time()
            
            #speed up player, up to...
            if powerup.type == 'Speed':
                powerup_sound_speed.play()
                player.speed += 10
                player.projectile_speed += 10

def projectile_logic(projectiles, enemy_count, game_over, player_died):
    for projectile in projectiles:
        if is_out_of_bounds(projectile, screen.get_width(), screen.get_height()):
                projectiles.remove(projectile)

        if game_over:
            projectile.can_move = False

        projectile.update(dt)
        projectile.draw(screen)

        if len(the_boss) > 0:
            if projectile.type == 'Player' and projectile.collides_with(the_boss[0]):
                enemy_die_Sound.play()
                projectiles.remove(projectile)
                the_boss[0].health -= 1

        if projectile.type == 'Boss' and projectile.collides_with(player):
            if not player_died:
                player_die_sound.play()
                player_died = True
            message_text = message_font.render('GAME OVER - Press E to Start Over', True, 'white')
            background_sound.set_volume(0.25)
            text_width = message_text.get_width()
            text_height = message_text.get_height()
            screen.blit(message_text, ((screen.get_width() - text_width) // 2, (screen.get_height() - text_height) // 2))
            game_over = True
            player.can_move = False
            return True

        for enemy in enemies:
            if projectile.collides_with(enemy):
                enemy.die()
                projectiles.remove(projectile)
                if projectile.type == 'Player':
                    player.score += 1

                #every 5 points there is a chance for a Powerups
                powerup_spawn('Shooting')
                powerup_spawn('Frozen')
                powerup_spawn('Speed')

                #every 10 points enemy count goes up by 1 until there are 30 enemies / projectile cooldown drops by 10 until its at 100
                if player.score % 10 == 0:
                    if enemy_count < 30:
                        enemy_count += 1
                    if player.projectile_cooldown > 100:
                        player.projectile_cooldown -= 10

                if not enemy.boss_exists:
                    for i in range(enemy_count - len(enemies) + 1):
                        enemies.append(Enemy(enemy_count))

                return enemy_count
    return enemy_count

def enemy_logic(enemies, enemy_count, game_over, the_boss, player_died):
    for enemy in enemies:
        if len(the_boss) > 0:
            enemy.boss_exists = True
        else:
            enemy.boss_exists = False
        
        if enemy.boss_exists:
            if is_out_of_bounds(enemy, screen.get_width(), screen.get_height()):
                enemies.remove(enemy)

        enemy.move(player.position, dt)
        status = enemy.draw(screen)
        if enemy.speed < 300:
            enemy.speed += 1/100

        if not status:
            enemies.remove(enemy)
            break

        if game_over:
            enemy.can_move = False

        if enemy.collides_with(player):
            if not player_died:
                player_die_sound.play()
                player_died = True
            message_text = message_font.render('GAME OVER - Press E to Start Over', True, 'white')
            background_sound.set_volume(0.25)
            text_width = message_text.get_width()
            text_height = message_text.get_height()
            screen.blit(message_text, ((screen.get_width() - text_width) // 2, (screen.get_height() - text_height) // 2))
            game_over = True
            player.can_move = False
            return True

        if len(the_boss) == 0:
            for i in range(enemy_count - len(enemies)):
                        enemies.append(Enemy(enemy_count))
    if player_died:
        return True
    return False

def is_out_of_bounds(enemy, screen_width, screen_height):
    return (
        enemy.position.x < -enemy.radius or
        enemy.position.x > screen_width + enemy.radius or
        enemy.position.y < -enemy.radius or
        enemy.position.y > screen_height + enemy.radius
    )

#audio variables
pygame.init()
pygame.mixer.init()
projectile_Sound = pygame.mixer.Sound('Audio//projectile_1.wav')
enemy_die_Sound = pygame.mixer.Sound('Audio//enemy_die.wav')
player_die_sound = pygame.mixer.Sound('Audio//player_die.wav')
powerup_sound_shooting = pygame.mixer.Sound('Audio//powerup_shooting.wav')
powerup_sound_frozen = pygame.mixer.Sound('Audio//powerup_frozen.wav')
powerup_sound_speed = pygame.mixer.Sound('Audio//powerup_speed.mp3')
background_sound = pygame.mixer.Sound('Audio//background.mp3')
boss_sound = pygame.mixer.Sound('Audio//Boss_Music.mp3')
background_sound.set_volume(0.25) #0.25
background_sound.play(-1)

#game variables
screen = pygame.display.set_mode((1920, 1080))
running = True
game_over = False
score_font = pygame.font.Font(None, 36)
message_font = pygame.font.Font(None, 100)
debug_font = pygame.font.Font(None, 36)
game_start = False
start_message_font = pygame.font.Font(None, 100)
start_message_text = start_message_font.render('Press E to Start', True, 'white')

#player variables
player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
player = Player(player_pos, 'seagreen2')
player_died = False
projectiles = []

#initialize enemies
boss_health = 50
enemy_count = 4
enemies = []
powerUps = []

print('test for github')

#pre-game menu
while not game_start and running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
            exit()
        elif event.type == pygame.KEYDOWN:
                if not game_start and event.key == pygame.K_e:
                    game_start = True  #Player pressed 'E', start the game
                    background_sound.set_volume(0.75) #0.75
        
    
    if not game_start and running:
        #Display the starting message and wait for the player to press 'E'
        screen.fill('black')
        screen.blit(start_message_text, ((screen.get_width() - start_message_text.get_width()) // 2, (screen.get_height() - start_message_text.get_height()) // 2))
        pygame.display.update()
        continue  #Skip the rest of the loop until 'E' is pressed

#initiate enemies
for i in range(enemy_count):
    enemies.append(Enemy(len(enemies)))

the_boss = []

#main loop
clock = pygame.time.Clock()
dt = 0 #delta time
while running:
    #exit/reset check
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and game_over:
            if event.key == pygame.K_e:
                reset_game(len(the_boss))
                enemy_count = 4
                game_over = False
                player_died = False
        
    #background and check keys
    screen.fill('black')
    keys = pygame.key.get_pressed()

    #player moves
    player.move(keys, dt, screen.get_width(), screen.get_height())
    player.draw(screen)

    #powerup collision/use logic
    powerup_logic(powerUps)

    #projectile logic
    if keys[pygame.K_SPACE]:
        if not game_over:
            player.shoot()

    temp_ = projectile_logic(projectiles, enemy_count, game_over, player_died)
    if isinstance(temp_,bool):
        player_died = temp_
        game_over = player_died
    else:
        enemy_count = temp_
        projectiles = [projectile for projectile in projectiles if projectile.position.y >= 0]

    #enemy logic
    player_died = enemy_logic(enemies, enemy_count, game_over, the_boss, player_died)
    game_over = player_died

    #boss logic
    if player.score % 100 == 0 and len(the_boss) == 0 and player.score > 0:
        background_sound.fadeout(2000)
        boss_sound.set_volume(1)
        boss_sound.play(-1)
        the_boss.append(Boss(boss_health))

    if len(the_boss) > 0:
        if player_died:
            the_boss[0].can_move = False

        if the_boss[0].collides_with(player):
            if not player_died:
                player_die_sound.play()
                player_died = True
            message_text = message_font.render('GAME OVER - Press E to Start Over', True, 'white')
            background_sound.set_volume(0.25)
            text_width = message_text.get_width()
            text_height = message_text.get_height()
            screen.blit(message_text, ((screen.get_width() - text_width) // 2, (screen.get_height() - text_height) // 2))
            game_over = True
            player.can_move = False

        status = the_boss[0].draw(screen, dt)

        if the_boss[0].health <= 0:
            boss_sound.set_volume(0.5)
            if not status:
                player.score += int(boss_health/2)
                boss_sound.fadeout(2000)
                background_sound.play(-1)
                the_boss.remove(the_boss[0])

                for i in range(enemy_count - len(enemies)):
                            enemies.append(Enemy(enemy_count))

    #scoreboard
    score_text = score_font.render('Score: ' + str(player.score), True, 'white')
    screen.blit(score_text, (10, 10))

    #debug
    if len(enemies) > 0:
        debug_text = debug_font.render('Cooldown: ' + str(player.projectile_cooldown) + ' Enemies: ' + str(len(enemies)) + 
                                    ' dt: ' + str(dt) +' e_speed: ' + str(round(enemies[0].speed,0)) +
                                    ' e_jitter: ' + str(round(enemies[0].jitter,0)) +' player speed: ' + str(round(player.speed,0)) + 
                                    ' projectiles : ' + str(len(projectiles)), True, 'white')
    else:
        debug_text = debug_font.render('Cooldown: ' + str(player.projectile_cooldown) + ' Enemies: ' + str(len(enemies)) + 
                                    ' dt: ' + str(dt) +' e_speed: 0' + ' e_jitter: 0' ' player speed: ' + str(round(player.speed,0)) +
                                    ' projectiles : ' + str(len(projectiles)), True, 'white')
    #screen.blit(debug_text, (10, screen.get_height() - 50))

    pygame.display.update()
    dt = clock.tick(144) / 1000

pygame.quit()