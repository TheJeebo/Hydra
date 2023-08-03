import pygame, random, time


class Player:
    def __init__(self, position, projectile_Sound, gp_end):
        self.position = position
        self.color = 'seagreen2'
        self.projectile_Sound = projectile_Sound
        self.speed = 500
        self.projectile_cooldown = 500
        self.last_projectile_time = 0
        self.score = 0
        self.radius = 20
        self.last_Direction = 'w'
        self.can_move = True
        self.key_pressed = False
        self.boss_exists = False
        self.god_mode = False

        self.god_powerup = False
        self.gp_time = 0
        self.gp_total = 0
        self.gp_end = gp_end

        self.homing_powerup = False 
        self.h_time = 0
        self.h_total = 0
        self.h_end = gp_end

        if self.homing_powerup:
            self.projectile_speed = 500
        else:
            self.projectile_speed = 750
        
    def move(self, keys, dt, screen_width, screen_height):
        if not self.can_move:
            return
        
        #up/down circle back doesn't work when boss is active
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.last_Direction = 'w'
            self.position.y -= self.speed * dt
            if self.boss_exists:
                if self.position.y - self.radius < 0:
                    self.position.y = 0 + self.radius
            else:
                if self.position.y < 0:
                    self.position.y = screen_height

        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.last_Direction = 's'
            self.position.y += self.speed * dt

            if self.boss_exists:
                if self.position.y + self.radius > screen_height:
                    self.position.y = screen_height - self.radius
            else:
                if self.position.y > screen_height:
                    self.position.y = 0

        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.last_Direction = 'a'
            self.position.x -= self.speed * dt
            if self.position.x < 0:
                    self.position.x = screen_width
                    
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.last_Direction = 'd'
            self.position.x += self.speed * dt
            if self.position.x > screen_width:
                    self.position.x = 0

        if keys[pygame.K_w] and keys[pygame.K_a]:
            self.last_Direction = 'wa'
        if keys[pygame.K_w] and keys[pygame.K_d]:
            self.last_Direction = 'wd'
        if keys[pygame.K_s] and keys[pygame.K_a]:
            self.last_Direction = 'sa'
        if keys[pygame.K_s] and keys[pygame.K_d]:
            self.last_Direction = 'sd'

        if keys[pygame.K_UP] and keys[pygame.K_LEFT]:
            self.last_Direction = 'wa'
        if keys[pygame.K_UP] and keys[pygame.K_RIGHT]:
            self.last_Direction = 'wd'
        if keys[pygame.K_DOWN] and keys[pygame.K_LEFT]:
            self.last_Direction = 'sa'
        if keys[pygame.K_DOWN] and keys[pygame.K_RIGHT]:
            self.last_Direction = 'sd'
       
    def draw(self, surface):
        if self.god_mode:
            self.color = 'deeppink'
            if self.god_powerup:
                #once powerup is close to ending, flash white
                gp_current = time.time()
                self.gp_total = gp_current - self.gp_time

                if self.gp_total > 7:
                    if int(self.gp_total*10) % 2 == 0:
                        self.color = 'white'
                    else:
                        self.color = 'deeppink'
                
                pygame.draw.circle(surface, self.color, self.position, self.radius+20)
                pygame.draw.circle(surface, 'black', self.position, self.radius+17)

                if self.gp_total > 10:
                    self.gp_end.play()
                    self.god_powerup = False
                    self.god_mode = False
        elif self.homing_powerup:
            h_current = time.time()
            self.h_total = h_current - self.h_time

            self.color = 'darkgoldenrod1'

            if self.h_total > 10:
                self.homing_powerup = False
        else:
            self.god_powerup = False
            self.color = 'seagreen2'

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

    def shoot(self, projectiles):
        if self.can_shoot():
            self.projectile_Sound.play()
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

            if self.homing_powerup:
                new_projectile = Projectile(self.position.copy(), self.projectile_speed, homing=self.homing_powerup)
            else:
                new_projectile = Projectile(self.position.copy(), projectile_Direction)
            projectiles.append(new_projectile)


class Enemy:
    def __init__(self, count, screen, sound):
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
        enemy_Personalities = ['normal','normal','normal','dodgy','glitchy']

        self.personality = enemy_Personalities[random.randint(0,len(enemy_Personalities)-1)]
        self.vertices = enemy_Shapes[random.randint(0,len(enemy_Shapes)-1)]
        self.position = pygame.Vector2(enemy_Spawns[random.randint(0,len(enemy_Spawns)-1)])
        self.color = enemy_Colors[random.randint(0,len(enemy_Colors)-1)]
        self.temp_color = self.color
        self.count = count
        self.speed = 200 + count
        self.radius = 20
        self.can_move = True
        self.is_dead = False
        self.dead_color = 255
        self.is_frozen = False
        self.frozen_start = 0
        self.frozen_end = 0
        self.boss_exists = False
        self.screen = screen
        self.sound = sound
        self.offset = random.randint(0,50)
        self.cooldown = 10
        self.last_time = 0

    def move(self, player, dt):
        player_pos = player.position.copy()
        enemy_speed = self.speed

        if self.personality == 'dodgy':
            offset = self.offset
            distance = pygame.Vector2.distance_to(player.position, self.position)
            if distance <= player.radius + random.randint(100,300):
                offset = 0
            match player.last_Direction:
                case 'w':
                    player_pos.y -= offset
                    player_pos.x -= offset
                case 's':
                    player_pos.y += offset
                    player_pos.x += offset
                case 'a':
                    player_pos.x -= offset
                    player_pos.y -= offset
                case 'd':
                    player_pos.x += offset
                    player_pos.y += offset
        
        if not self.can_move or self.is_dead or self.is_frozen:
            return

        if self.personality == 'glitchy':
            current_time = pygame.time.get_ticks()
            can_twitch = current_time - self.last_time > self.cooldown

            if can_twitch:
                self.last_time = pygame.time.get_ticks()
                offset = random.randint(0,100)

                match offset:
                    case 0:
                        self.boss_exists = True
                    case 1:
                        enemy_speed += 50
                    case 2:
                        enemy_speed -= 50
                    case 4:
                        self.position.x += 30
                    case 5:
                        self.position.x -= 30
                    case 6:
                        self.position.y += 30
                    case 7:
                        self.position.y -= 30
                    case _:
                        self.boss_exists = False

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
            if self.screen.get_width() / 2 > self.position.x:
                self.position.x -= enemy_speed * dt * 1.25
            if self.screen.get_width() / 2 < self.position.x:
                self.position.x += enemy_speed * dt * 1.25
            if self.screen.get_height() + 50 > self.position.y:
                self.position.y += enemy_speed * dt * 1.25

    def draw(self, surface, dt):
        if self.is_frozen:
            self.color = 'blue'
            self.frozen_end = time.time()
            time_frozen = self.frozen_end - self.frozen_start

            if time_frozen > 10:
                self.is_frozen = False
        else:
            self.color = self.temp_color

        if self.is_dead:
            self.dead_color -= (1 * (dt*1000))
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
        if player.god_mode:
            return False #god mode
        else:
            return distance <= player.radius
        
    def die(self):
        self.sound.play()
        
        self.is_dead = True


class Projectile:
    def __init__(self, position, velocity, type='Player', homing=False):
        self.position = position
        self.velocity = velocity
        self.color = 'white'
        self.size = 5
        self.can_move = True
        self.homing = homing
        self.type = type
        self.last_color_change = 0
        self.radius = 5
        if self.type == 'Player':
            self.color_cooldown = 100
        else:
            self.color_cooldown = 212
        self.color_bool = True

    def update(self, dt, enemies):
        if not self.can_move:
            return
        
        if len(enemies) <= 0:
            self.homing = False

        if self.homing:
            target = 10000
            for enemy in enemies:
                distance = pygame.Vector2.distance_to(enemy.position, self.position)
                if distance < target:
                    target = distance
                    enemy_pos = enemy.position.copy()
            
            if enemy_pos.x > self.position.x:
                self.position.x += self.velocity * dt
            if enemy_pos.x < self.position.x:
                self.position.x -= self.velocity * dt
            if enemy_pos.y > self.position.y:
                self.position.y += self.velocity * dt
            if enemy_pos.y < self.position.y:
                self.position.y -= self.velocity * dt
            
        else:
            try:
                self.position += self.velocity * dt
            except:
                print('Projectile Error')

    def draw(self, surface):
        current_time = pygame.time.get_ticks()
        dif = current_time - self.last_color_change

        if dif > self.color_cooldown:
            if self.color_bool and self.type == 'Player'and not self.homing:
                self.color = 'deepskyblue'
                self.size = 10
                self.color_bool = False
            elif self.color_bool and self.type == 'Boss':
                self.color = 'crimson'
                self.size = 10
                self.color_bool = False
            elif self.color_bool and self.type == 'Player' and self.homing:
                self.color = 'indianred1'
                self.size = 10
                self.color_bool = False
            elif not self.color_bool and self.type == 'Player' and self.homing:
                self.color = 'orangered4'
                self.size = 5
                self.color_bool = False
                self.color_bool = True
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
            try:
                if enemy.god_mode:
                    return False
                else:
                    distance = pygame.Vector2.distance_to(enemy.position, self.position)
                    return distance <= enemy.radius
            except:
                distance = pygame.Vector2.distance_to(enemy.position, self.position)
                return distance <= enemy.radius


class Powerup:
    def __init__(self, screen, type, message = ''):
        rand_x = random.randint(10, screen.get_width() - 10)
        rand_y = random.randint(10, screen.get_height() - 10)
        self.rand = random.randint(-200,200)
        self.position = pygame.Vector2(rand_x, rand_y)
        self.is_active = True
        self.start_Time = time.time()
        self.type = type
        self.message = message
        self.message_font = pygame.font.Font(None, 75)
        if self.type == 'Message':
            self.display_time = 2
            self.color_value = 255
        else:
            self.display_time = 6
            self.color_value = 0
        self.color = (self.color_value,self.color_value,self.color_value)
        self.time_Active = 0
        self.paused_Time = 0

    def collides_with(self, player):
        if not self.is_active:
            return
        
        distance = pygame.Vector2.distance_to(player.position, self.position)

        return distance <= player.radius + 10
    
    def draw(self, screen, dt, paused=False, pause=0):
        #powerup color and timing logic
        if paused:
            self.paused_Time += pause
        end_Time = time.time() - self.paused_Time
        self.time_Active = end_Time - self.start_Time

        dt = dt * 100

        #timeout after display_time seconds
        if self.time_Active > self.display_time:
                self.is_active = False

        if not self.is_active:
            return False
        
        #powerup types
        match self.type:
            case 'Frozen':
                self.color = 'dodgerblue'

                if round(self.time_Active,0) % 2 == 0:
                    self.color = 'white'
                else:
                    self.color = 'dodgerblue'

            case 'Shooting':
                if self.color[1]+1*dt < 255:
                    self.color = (0,self.color[1]+1*dt,0)
                elif self.color[2]+1*dt < 255:
                    self.color = (0,self.color[1],self.color[2]+1*dt)
                elif self.color[0]+1*dt < 255:
                    self.color = (self.color[0]+1*dt,self.color[1],self.color[2])

            case 'Speed':
                if round(self.time_Active,0) % 2 == 0:
                    self.color = 'aquamarine1'
                else:
                    self.color = 'gold'
            
            case 'Invincible':
                if round(self.time_Active*10,0) % 2 == 0:
                    self.color = 'deeppink'
                else:
                    self.color = 'purple4'
            
            case 'Homing':
                if round(self.time_Active*10,0) % 2 == 0:
                    self.color = 'indianred1'
                else:
                    self.color = 'orangered4'

            case 'Message':
                message_text = self.message_font.render(self.message, True, self.color)
                text_width = message_text.get_width()
                text_height = message_text.get_height()
                if self.color_value - 1.5*dt > 0:
                    self.color_value -= 1.5*dt
                else:
                    return False
                self.color = (self.color_value,self.color_value,self.color_value)
                
        #draw
        if self.type == 'Message':
            screen.blit(message_text, ((screen.get_width() - text_width) // 2, (screen.get_height() - text_height) // 3 + self.rand))
        else:
            pygame.draw.circle(screen, self.color, (self.position.x, self.position.y), 10)
        
        return True


class Boss:
    def __init__(self, health, screen, sound):
        self.position = pygame.Vector2(screen.get_width() / 2,-screen.get_width() * 1.125 - 75)
        self.color = 'brown2' #this is not brown lol
        self.health = health
        self.max_health = self.health
        self.radius = screen.get_width() * 1.125
        self.intro_complete = False
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
        self.screen = screen
        self.sound = sound
          
    def draw(self, surface, dt, projectiles):
        if not self.can_move:
            self.intro_complete = True

        if not self.intro_complete:
            if self.position.y < (-self.screen.get_width()):
                self.position.y += self.speed * dt

                if self.health_color[1] + 0.1*(dt*1000) < 255:
                    self.health_color = (0,self.health_color[1] + 0.1*(dt*1000),0)
            else:
                self.intro_complete = True
        else:
            if self.can_move:
                self.shoot(projectiles)

        if self.health <= 0:
            self.is_dead = True

        if self.is_dead:
            self.dead_color -= 0.1 * (dt*1000)
            if self.dead_color < 0:
                return False
            
            self.color = (self.dead_color,self.dead_color,self.dead_color)

        pygame.draw.circle(surface, self.color, self.position, self.radius)

        #health bar
        rect_width, rect_height = 1000, 20
        rect_x = (self.screen.get_width() - rect_width) // 2
        rect_y = 20
        ratio = self.health / self.max_health
        total_rect_dimensions = (rect_x, rect_y, rect_width, rect_height)
        remaining_rect_dimensions = (rect_x, rect_y, rect_width * ratio, rect_height)
        pygame.draw.rect(surface, 'black', total_rect_dimensions)
        pygame.draw.rect(surface, self.health_color, remaining_rect_dimensions)

        return True

    def shoot(self, projectiles):
        screen = self.screen

        if self.can_shoot():
            self.sound.play()
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

        if player.god_mode:
            return False
        else:
            distance = pygame.Vector2.distance_to(player.position, self.position)
            return distance <= self.radius + 20