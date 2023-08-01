import pygame, random, time
from module import Player, Enemy, Boss, Powerup


#game functions
def reset_game(boss_Count):
    #resets game after player death
    player.score = 0
    enemies.clear()
    projectiles.clear()
    powerUps.clear()
    the_boss.clear()
    background_sound.set_volume(0.5)
    player.position = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
    player.can_move = True
    player.projectile_cooldown = 500
    player.speed = 500
    player.projectile_speed = 750
    player.boss_exists = False
    player.god_mode = False
    if boss_Count > 0:
        boss_sound.stop()
        background_sound.play(-1)

    for i in range(4):
        enemies.append(Enemy(len(enemies), screen, enemy_die_Sound))

def powerup_spawn(type):
    #every 5 points there is a 25% chance for a Powerup
    if player.score % 5 == 0:
        powerup_roll = random.randint(1,100)
        if powerup_roll < 250:
            match type:
                case 'Shooting':
                    if player.projectile_cooldown > 100:
                        powerUps.append(Powerup(screen, type))
                case 'Speed':
                    if player.speed < 700:
                        powerUps.append(Powerup(screen, type))
                case 'Frozen':
                    powerUps.append(Powerup(screen, type))
                case 'Invincible':
                    powerUps.append(Powerup(screen, type))

def powerup_logic(powerUps):
    for powerup in powerUps:
        active = powerup.draw(screen, dt)

        if not active:
            powerUps.remove(powerup)

        if powerup.collides_with(player):
            powerUps.remove(powerup)

            #removes 25 from shooting cooldown, down to 100
            if powerup.type == 'Shooting':
                powerup_sound_shooting.play()
                message = 'Shooting Cooldown -25'
                if player.projectile_cooldown > 100:
                    player.projectile_cooldown -= 25
                    if player.projectile_cooldown < 100:
                        player.projectile_cooldown = 100
            
            #freezes enemies
            if powerup.type == 'Frozen':
                powerup_sound_frozen.play()
                message = 'All Enemies Frozen'
                for enemy in enemies:
                    enemy.is_frozen = True
                    enemy.frozen_start = time.time()
            
            #speed up player, up to 700
            if powerup.type == 'Speed':
                powerup_sound_speed.play()
                message = 'Player Speed +10'
                player.speed += 10
                player.projectile_speed += 10

            #Invincible for x time TODO set up time
            if powerup.type == 'Invincible':
                powerup_sound_invincible.play()
                message = 'Invincible! 10 seconds'
                player.god_mode = True
                player.god_powerup = True
                player.gp_time = time.time()
            
            #Display powerup message
            try:
                powerUps.append(Powerup(screen, 'Message', message))
            except:
                print('PowerUp Message Error')

def projectile_logic(projectiles, enemy_count, game_over, player_died):
    #returns enemy_count unless Boss projectile hits player, then returns True
    for projectile in projectiles:
        if is_out_of_bounds(projectile, screen.get_width(), screen.get_height()):
                projectiles.remove(projectile)

        if game_over:
            projectile.can_move = False

        projectile.update(dt)
        projectile.draw(screen)

        if len(the_boss) > 0:
            #player hitting boss logic
            if projectile.type == 'Player' and projectile.collides_with(the_boss[0]):
                enemy_die_Sound.play()
                projectiles.remove(projectile)
                the_boss[0].health -= 1

        if projectile.type == 'Boss' and projectile.collides_with(player):
            #player has been hit by Boss projectile, return True
            if not player_died:
                player_die_sound.play()
                player_died = True
            message_text = message_font.render('GAME OVER - Press E to Start Over', True, 'white')
            background_sound.set_volume(0.2)
            text_width = message_text.get_width()
            text_height = message_text.get_height()
            screen.blit(message_text, ((screen.get_width() - text_width) // 2, (screen.get_height() - text_height) // 2))
            game_over = True
            player.can_move = False
            return True

        for enemy in enemies:
            #enemies hit by projectile logic
            if projectile.collides_with(enemy):
                enemy.die()
                try:
                    projectiles.remove(projectile)
                except:
                    print('Projectile Error')

                if projectile.type == 'Player':
                    player.score += 1

                #every 5 points there is a chance for a Powerups
                powerup_spawn('Shooting')
                powerup_spawn('Frozen')
                powerup_spawn('Speed')
                powerup_spawn('Invincible')

                #every 10 points enemy count goes up by 1 until there are 30 enemies / projectile cooldown drops by 10 until its at 100
                #TODO enemies that are in their dying animation prevent more enemies from being spawned, not the behavior I want
                if player.score % 10 == 0:
                    if enemy_count < 30:
                        enemy_count += 1
                    if player.projectile_cooldown > 100:
                        player.projectile_cooldown -= 10

                if not enemy.boss_exists:
                    for i in range(enemy_count - len(enemies) + 1):
                        enemies.append(Enemy(enemy_count, screen, enemy_die_Sound))

                return enemy_count
    return enemy_count

def enemy_logic(enemies, enemy_count, game_over, the_boss, player_died):
    #enemies chase player unless boss is present, then they run off screen
    for enemy in enemies:
        if len(the_boss) > 0:
            enemy.boss_exists = True
        else:
            enemy.boss_exists = False
        
        if enemy.boss_exists:
            if is_out_of_bounds(enemy, screen.get_width(), screen.get_height()):
                enemies.remove(enemy)

        enemy.move(player.position, dt)
        status = enemy.draw(screen, dt)
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
            background_sound.set_volume(0.2)
            text_width = message_text.get_width()
            text_height = message_text.get_height()
            screen.blit(message_text, ((screen.get_width() - text_width) // 2, (screen.get_height() - text_height) // 2))
            game_over = True
            player.can_move = False
            return True

        if len(the_boss) == 0:
            for i in range(enemy_count - len(enemies)):
                        enemies.append(Enemy(enemy_count, screen, enemy_die_Sound))
    if player_died:
        return True
    return False

def is_out_of_bounds(object, screen_width, screen_height):
    #used for projectiles and enemies to clear items that are off screen
    return (object.position.x < -object.radius or
        object.position.x > screen_width + object.radius or
        object.position.y < -object.radius or
        object.position.y > screen_height + object.radius)


#audio variables
pygame.init()
pygame.mixer.init()

projectile_Sound = pygame.mixer.Sound('Audio//projectile_1.wav')
enemy_die_Sound = pygame.mixer.Sound('Audio//enemy_die.wav')
player_die_sound = pygame.mixer.Sound('Audio//player_die.wav')
misc_sounds = [projectile_Sound, enemy_die_Sound, player_die_sound]
for sound in misc_sounds:
    sound.set_volume(0.6)

powerup_sound_shooting = pygame.mixer.Sound('Audio//powerup_shooting.wav')
powerup_sound_frozen = pygame.mixer.Sound('Audio//powerup_frozen.wav')
powerup_sound_speed = pygame.mixer.Sound('Audio//powerup_speed.mp3')
powerup_sound_invincible = pygame.mixer.Sound('Audio//powerup_invincible.wav')
powerup_sound_invincible_end = pygame.mixer.Sound('Audio//powerup_invincible_end.wav')
powerup_sounds = [powerup_sound_shooting, powerup_sound_frozen, powerup_sound_speed, powerup_sound_invincible, powerup_sound_invincible_end]
for sound in powerup_sounds:
    sound.set_volume(0.6)

background_sound = pygame.mixer.Sound('Audio//background.mp3')
boss_sound = pygame.mixer.Sound('Audio//Boss_Music.mp3')
background_sound.set_volume(0.2)
background_sound.play(-1)

#game variables
screen = pygame.display.set_mode((1920, 1080))
running = True
game_over = False
score_font = pygame.font.Font(None, 36)
message_font = pygame.font.Font(None, 100)
debug_font = pygame.font.Font(None, 50)
game_start = False
start_message_text = message_font.render('Press E to Start', True, 'white')
show_debug = False
game_pause = False

#player variables
player_pos = pygame.Vector2(screen.get_width() / 2, screen.get_height() / 2)
player = Player(player_pos, projectile_Sound, powerup_sound_invincible_end)
projectiles = []
player_died = False

#initialize enemies
boss_health = 50
enemy_count = 4
enemies = []
powerUps = []


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
                    background_sound.set_volume(0.5)
        
    
    if not game_start and running:
        #Display the starting message and wait for the player to press 'E'
        screen.fill('black')
        screen.blit(start_message_text, ((screen.get_width() - start_message_text.get_width()) // 2, (screen.get_height() - start_message_text.get_height()) // 2))
        pygame.display.update()
        continue  #Skip the rest of the loop until 'E' is pressed

#initiate enemies
for i in range(enemy_count):
    enemies.append(Enemy(len(enemies), screen, enemy_die_Sound))
the_boss = []


#main loop
clock = pygame.time.Clock()
dt = 0 #delta time
while running:
    #exit/reset check
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if game_over and event.key == pygame.K_e:
                reset_game(len(the_boss))
                enemy_count = 4
                game_over = False
                player_died = False
            elif event.key == pygame.K_F1:
                if show_debug:
                    show_debug = False
                else:
                    show_debug = True
            elif event.key == pygame.K_e:
                game_pause = True
            elif event.key == pygame.K_F2:
                if player.god_mode:
                    player.god_mode = False
                else:
                    player.god_mode = True

    #pause      
    paused_time = 0
    pause_start = time.time()
    while game_pause:
        background_sound.set_volume(0.2)
        boss_sound.set_volume(0.2)
        message_text = message_font.render('Game Paused - Press E to Resume', True, 'white')
        text_width = message_text.get_width()
        text_height = message_text.get_height()
        screen.blit(message_text, ((screen.get_width() - text_width) // 2, (screen.get_height() - text_height) // 2))
        pygame.display.update()

        pause_end = time.time()
        paused_time = pause_end - pause_start

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                game_pause = False
            elif event.type == pygame.KEYDOWN:
                if game_over and event.key == pygame.K_e:
                    reset_game(len(the_boss))
                    enemy_count = 4
                    game_over = False
                    player_died = False
                elif event.key == pygame.K_F1:
                    if show_debug:
                        show_debug = False
                    else:
                        show_debug = True
                elif event.key == pygame.K_e:
                    game_pause = False
                    background_sound.set_volume(0.5)
                    boss_sound.set_volume(0.7)
                    clock = pygame.time.Clock()

    #powerup pause correction
    if len(powerUps) > 0:
        for powerup in powerUps:
            powerup.draw(screen, dt, True, paused_time)

        
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
            player.shoot(projectiles)

    projectile_Return = projectile_logic(projectiles, enemy_count, game_over, player_died)
    if isinstance(projectile_Return,bool):
        player_died = projectile_Return
        game_over = player_died
    else:
        enemy_count = projectile_Return
        projectiles = [projectile for projectile in projectiles if projectile.position.y >= 0]

    #enemy logic
    player_died = enemy_logic(enemies, enemy_count, game_over, the_boss, player_died)
    game_over = player_died

    #boss logic
    if player.score % 100 == 0 and len(the_boss) == 0 and player.score > 0:
        background_sound.fadeout(2000)
        boss_sound.set_volume(0.7)
        boss_sound.play(-1)
        player.boss_exists = True
        the_boss.append(Boss(boss_health, screen, projectile_Sound))

    if len(the_boss) > 0:
        if player_died:
            the_boss[0].can_move = False

        if the_boss[0].collides_with(player):
            if not player_died:
                player_die_sound.play()
                player_died = True
            message_text = message_font.render('GAME OVER - Press E to Start Over', True, 'white')
            background_sound.set_volume(0.2)
            text_width = message_text.get_width()
            text_height = message_text.get_height()
            screen.blit(message_text, ((screen.get_width() - text_width) // 2, (screen.get_height() - text_height) // 2))
            game_over = True
            player.can_move = False

        status = the_boss[0].draw(screen, dt, projectiles)

        if the_boss[0].health <= 0:
            boss_sound.set_volume(0.5)
            player.boss_exists = False
            if not status:
                player.score += int(boss_health/2)
                boss_sound.fadeout(2000)
                background_sound.play(-1)
                the_boss.remove(the_boss[0])

                for i in range(enemy_count - len(enemies)):
                            enemies.append(Enemy(enemy_count, screen, enemy_die_Sound))

    #scoreboard
    score_text = score_font.render('Score: ' + str(player.score), True, 'white')
    screen.blit(score_text, (10, 10))

    #debug
    if len(enemies) > 0:
        debug_text = debug_font.render('Cooldown: ' + str(player.projectile_cooldown) + ' Enemies: ' + str(len(enemies)) + 
                                    ' dt: ' + str(dt) +' e_speed: ' + str(round(enemies[0].speed,0)) +' player speed: ' + str(round(player.speed,0)) + 
                                    ' projectiles : ' + str(len(projectiles)) + ' god mode: ' + str(player.god_mode), True, 'white')
    else:
        debug_text = debug_font.render('Cooldown: ' + str(player.projectile_cooldown) + ' Enemies: ' + str(len(enemies)) + 
                                    ' dt: ' + str(dt) +' e_speed: 0' + ' player speed: ' + str(round(player.speed,0)) +
                                    ' projectiles : ' + str(len(projectiles)) + ' god mode: ' + str(player.god_mode), True, 'white')
    if show_debug:
        screen.blit(debug_text, (10, screen.get_height() - 50))

    pygame.display.update()
    dt = clock.tick(1000) / 1000

pygame.quit()