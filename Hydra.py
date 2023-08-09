import pygame, random, time, csv, string
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
    player.homing_powerup = False
    player.multi_powerup = False
    player.fire_powerup = False
    player.projectile_speed = 750
    player.boss_exists = False
    player.god_mode = False
    
    if boss_Count > 0:
        boss_sound.stop()
        background_sound.play(-1)

    for i in range(4):
        enemies.append(Enemy(len(enemies), screen, enemy_die_Sound))

def powerup_spawn():
    types = ['Shooting','Speed','Frozen','Invincible','Homing','Multi', 'Fire']

    if player.score % 5 == 0:
        for type in types:
            powerup_roll = random.randint(1,100)
            if powerup_roll < 200:
                #test
                match type:
                    case 'Fire':
                        powerUps.append(Powerup(screen, type))
                
            if powerup_roll < 5:
                #rare
                match type:
                    case 'Invincible':
                        powerUps.append(Powerup(screen, type))
                    case 'Homing':
                        powerUps.append(Powerup(screen, type))
                    case 'Fire':
                        powerUps.append(Powerup(screen, type))

            if powerup_roll < 20:
                #common
                match type:
                    case 'Shooting':
                        if player.projectile_cooldown > 100:
                            powerUps.append(Powerup(screen, type))
                    case 'Speed':
                        if player.speed < 700:
                            powerUps.append(Powerup(screen, type))
                    case 'Frozen':
                        powerUps.append(Powerup(screen, type))
                    case 'Multi':
                        powerUps.append(Powerup(screen, type))
                    
def powerup_logic(powerUps):
    for powerup in powerUps:
        active = powerup.draw(screen, dt)

        if not active:
            powerUps.remove(powerup)

        if powerup.collides_with(player) and not powerup.type == 'Message':
            powerUps.remove(powerup)

            #removes 25 from shooting cooldown, down to 100
            if powerup.type == 'Shooting':
                powerup_sound_shooting.play()
                message = 'Shooting Cooldown -20'
                if player.projectile_cooldown > 100:
                    player.projectile_cooldown -= 20
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

            #Invincible for 10 seconds
            if powerup.type == 'Invincible':
                powerup_sound_invincible.play()
                message = 'Invincible! 10 seconds'
                player.god_mode = True
                player.god_powerup = True
                player.gp_time = time.time()
            
            #homing bullet, chases closest target
            if powerup.type == 'Homing':
                powerup_sound_homing.play()
                message = 'Homing Bullets! 10 seconds'
                player.homing_powerup = True
                player.h_time = time.time()
            
            #homing bullet, chases closest target
            if powerup.type == 'Multi':
                powerup_sound_multi.play()
                message = 'Multi Bullets! 10 seconds'
                player.multi_powerup = True
                player.m_time = time.time()
            
            #leaves a fire trail
            if powerup.type == 'Fire':
                powerup_sound_fire.play()
                message = 'Fire Trail! 10 seconds'
                player.fire_powerup = True
                player.f_time = time.time()
            
            #message catch
            if powerup.type == 'Message':
                #there is a rare error where a 'message' type powerup gets through collision
                #it will just repeat whatever message it is holding
                message = powerup.message

            #Display powerup message
            try:
                powerUps.append(Powerup(screen, 'Message', message))
            except:
                continue

def projectile_logic(projectiles, enemy_count, game_over, player_died):
    #returns enemy_count unless Boss projectile hits player, then returns True
    for projectile in projectiles:
        if is_out_of_bounds(projectile, screen.get_width(), screen.get_height()):
            projectiles.remove(projectile)

        if game_over:
            projectile.can_move = False

        status = projectile.update(dt, enemies)

        if isinstance(status, bool):
            if not status:
                projectiles.remove(projectile)

        projectile.draw(screen)

        if len(the_boss) > 0:
            #player hitting boss logic
            if projectile.type == 'Player' and projectile.collides_with(the_boss[0]):
                enemy_die_Sound.play()
                try:
                    projectiles.remove(projectile)
                except:
                    continue
                the_boss[0].health -= 1

        if projectile.type == 'Boss' and projectile.collides_with(player):
            #player has been hit by Boss projectile, return True
            if not player_died:
                player_die_sound.play()
                player_died = True
            game_over_message()
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
                    continue

                if projectile.type == 'Player':
                    player.score += 1

                #every 5 points there is a chance for a Powerups
                powerup_spawn()

                #every 10 points enemy count goes up by 1 until there are 30 enemies / projectile cooldown drops by 5 until its at 100
                if player.score % 10 == 0:
                    if enemy_count < 30:
                        enemy_count += 1
                    if player.projectile_cooldown > 100:
                        player.projectile_cooldown -= 5

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

        enemy.move(player, dt)
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
            game_over_message()
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

def game_over_message():
    message_text = message_font.render('GAME OVER - Press E to Start Over', True, 'white')
    background_sound.set_volume(0.2)
    text_width = message_text.get_width()
    text_height = message_text.get_height()
    screen.blit(message_text, ((screen.get_width() - text_width) // 2, (screen.get_height() - text_height) // 2))

def load_high_scores():
    try:
        with open('highscores.csv', 'r', newline='') as file:
            reader = csv.reader(file)
            high_scores = [(row[0], int(row[1])) for row in reader]
            high_scores.sort(key=lambda x: x[1], reverse=True)
            return high_scores
    except FileNotFoundError:
        return []

def save_high_scores(high_scores):
    with open('highscores.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        for name, score in high_scores:
            writer.writerow([name, score])

def update_high_scores(new_score):
    #this is a lot more code than I thought it would be...
    #and it's gonna get longer!!!

    #Load existing high scores
    high_scores = load_high_scores()

    #Check if the new score is a high score
    if len(high_scores) < 10 or new_score > high_scores[-1][1]:
        background_sound.stop()
        boss_sound.stop()
        highscore_music.play(-1)

        if len(high_scores) == 10:
            high_scores.pop()  #Remove the lowest high score

        #Get the player's name (limited to 3 characters)
        inputting = True
        player_name = 'AAA'
        name_text = message_font.render(player_name, True, 'white')
        name_width = name_text.get_width() + 50

        alphabet = list(string.ascii_uppercase)
        current_letter_index = 0
        name_index = 0
        ani = 0
        ani_switch = True

        while inputting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        current_letter_index = (current_letter_index + 1) % len(alphabet)
                    elif event.key == pygame.K_DOWN:
                        current_letter_index = (current_letter_index - 1) % len(alphabet)
                    elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
                        current_letter_index = 0
                        name_index += 1
                        if name_index >= 3:
                            inputting = False

            current_letter = alphabet[current_letter_index]
            player_name = replace_char(player_name, name_index, current_letter)
            screen.fill('black')

            #animate background
            for i in range(50):
                ani2 = ani+i*20
                pygame.draw.line(screen, 'red', (0,0), (screen.get_width() - ani2, screen.get_height()))
                pygame.draw.line(screen, 'green', (screen.get_width(),0), (0 + ani2, screen.get_height()))
                pygame.draw.line(screen, 'red', (screen.get_width(), screen.get_height()), (0 + ani2 , 0))
                pygame.draw.line(screen, 'green', (0,screen.get_height()), (screen.get_width() - ani2,0))

            if ani_switch:
                ani+=1
                if (screen.get_width() - (ani+i*20)) < 0:
                    ani_switch = False
            else:
                ani-=1
                if ani < 0:
                    ani_switch = True

            message_text = message_font.render('GAME OVER - High Score!', True, 'white')
            message_font2 = pygame.font.Font(None, 50)
            message_2 = message_font2.render('Use Up, Down, and Enter', True, 'white')
            name_font = pygame.font.Font(None, 150)
            for i, letter in enumerate(player_name):
                if i == name_index:
                    render_letter = name_font.render(letter, True, 'blue')
                else:
                    render_letter = name_font.render(letter, True, 'white')
                
                text_height = render_letter.get_height()
                screen.blit(render_letter, ((screen.get_width() + (name_width*i) - 250) // 2, (screen.get_height() - text_height) // 2))

            background_sound.set_volume(0.2)
            text_width = message_text.get_width()
            text_height = message_text.get_height()
            screen.blit(message_text, ((screen.get_width() - text_width) // 2, (screen.get_height() - text_height) // 4))
            screen.blit(message_2, ((screen.get_width() - text_width) // 2, (screen.get_height() - text_height) // 3))
            pygame.display.update()

        high_scores.append((player_name, new_score))
        high_scores.sort(key=lambda x: x[1], reverse=True)

        #Save updated high scores
        save_high_scores(high_scores)
        highscore_music.stop()
        background_sound.play(0)
        background_sound.set_volume(0.2)

def replace_char(string, index, new_char):
    if index < 0 or index >= len(string):
        return string  # Return the original string if index is out of bounds
    return string[:index] + new_char + string[index + 1:]

def reset_high_scores():
    message_font = pygame.font.Font(None, 25)
    message_text = message_font.render('Press F3 again to reset all high scores. Any other key to cancel.', True, 'white')
    text_width = message_text.get_width()
    text_height = message_text.get_height()
    screen.blit(message_text, ((screen.get_width() - text_width) // 4, (screen.get_height() - text_height) // 3))
    pygame.display.update()

    prompt = True
    while prompt:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    prompt = False
                else:
                    return

    default_scores = 'highscores_default.csv'
    current_scores = 'highscores.csv'

    data = []
    with open(default_scores, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            data.append(row)

    with open(current_scores, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        for row in data:
            writer.writerow(row)


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
powerup_sound_multi = pygame.mixer.Sound('Audio//powerup_multi.wav')
powerup_sound_multi_end = pygame.mixer.Sound('Audio//powerup_multi_end.wav')
powerup_sound_homing = pygame.mixer.Sound('Audio//powerup_homing.wav')
powerup_sound_homing_end = pygame.mixer.Sound('Audio//powerup_homing_end.wav')
powerup_sound_fire = pygame.mixer.Sound('Audio//powerup_fire.wav')
powerup_sound_fire_end = pygame.mixer.Sound('Audio//powerup_fire_end.wav')
powerup_sounds = [powerup_sound_shooting, powerup_sound_frozen, powerup_sound_speed, powerup_sound_invincible, powerup_sound_invincible_end,
                  powerup_sound_multi, powerup_sound_multi_end, powerup_sound_homing, powerup_sound_homing_end, powerup_sound_fire, powerup_sound_fire_end]
for sound in powerup_sounds:
    sound.set_volume(0.6)

background_sound = pygame.mixer.Sound('Audio//background_60.mp3')
boss_sound = pygame.mixer.Sound('Audio//Boss_Music.mp3')
highscore_music = pygame.mixer.Sound('Audio/high_score.mp3')
highscore_music.set_volume(0.6)
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
player = Player(player_pos, projectile_Sound, powerup_sound_invincible_end, powerup_sound_multi_end, powerup_sound_homing_end, powerup_sound_fire_end)
projectiles = []
player_died = False
high_scores = load_high_scores()
high_score_complete = False
cheat_mode = False

#initialize enemies
boss_health = 25
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
            elif event.key == pygame.K_F3:
                reset_high_scores()
        
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
                cheat_mode = False
                enemy_count = 4
                game_over = False
                player_died = False
                high_score_complete = False
                boss_health = 25
                high_scores = load_high_scores()
            elif event.key == pygame.K_F1:
                if show_debug:
                    show_debug = False
                else:
                    show_debug = True
            elif event.key == pygame.K_e:
                game_pause = True
            elif event.key == pygame.K_F2:
                cheat_mode = True

                if player.god_mode:
                    player.god_mode = False
                else:
                    player.god_mode = True
            elif game_over and event.key == pygame.K_F3:
                reset_high_scores()

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
                    cheat_mode = False
                    enemy_count = 4
                    game_over = False
                    player_died = False
                    high_score_complete = False
                    boss_health = 25
                    high_scores = load_high_scores()
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
                elif event.key == pygame.K_F3:
                    reset_high_scores()

    #powerup pause correction
    if len(powerUps) > 0:
        for powerup in powerUps:
            powerup.draw(screen, dt, True, paused_time)
  
    #background and check keys
    screen.fill('black')
    keys = pygame.key.get_pressed()

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

    #player moves
    player.move(keys, dt, screen.get_width(), screen.get_height())
    player.draw(screen, projectiles)

    #powerup collision/use logic
    powerup_logic(powerUps)

    #enemy logic
    player_died = enemy_logic(enemies, enemy_count, game_over, the_boss, player_died)
    game_over = player_died

    #boss logic
    if player.score == (boss_health*3) and len(the_boss) == 0 and player.score > 0:
        background_sound.fadeout(2000)
        boss_sound.set_volume(0.7)
        boss_sound.play(-1)
        player.boss_exists = True
        player.homing_powerup = False
        player.fire_powerup = False
        the_boss.append(Boss(boss_health, screen, projectile_Sound))

    if len(the_boss) > 0:
        player.homing_powerup = False

        if player_died:
            the_boss[0].can_move = False

        if the_boss[0].collides_with(player):
            if not player_died:
                player_die_sound.play()
                player_died = True
            game_over_message()
            game_over = True
            player.can_move = False

        status = the_boss[0].draw(screen, dt, projectiles)

        if the_boss[0].health <= 0:
            boss_sound.set_volume(0.5)
            player.boss_exists = False
            if not status:
                player.score += int(boss_health/4)
                boss_health *= 2
                if boss_health > 200:
                    boss_health = 200 #max boss health
                boss_sound.fadeout(2000)
                background_sound.play(-1)
                the_boss.remove(the_boss[0])

                for i in range(enemy_count - len(enemies)):
                    enemies.append(Enemy(enemy_count, screen, enemy_die_Sound))

    #score
    score_text = score_font.render('Score: ' + str(player.score), True, 'white')
    screen.blit(score_text, (10, 10))

    #debug
    if len(enemies) > 0:
        debug_text = debug_font.render('Cooldown: ' + str(player.projectile_cooldown) + ' Enemies: ' + str(len(enemies)) + 
                                    ' dt: ' + str(dt) +' e_speed: ' + str(round(enemies[0].speed,0)) +' player speed: ' + str(round(player.speed,0)) + 
                                    ' projectiles : ' + str(len(projectiles)) + ' god mode: ' + str(player.god_mode) +
                                    'b_health: ' + str(boss_health), True, 'white')
    else:
        debug_text = debug_font.render('Cooldown: ' + str(player.projectile_cooldown) + ' Enemies: ' + str(len(enemies)) + 
                                    ' dt: ' + str(dt) +' e_speed: 0' + ' player speed: ' + str(round(player.speed,0)) +
                                    ' projectiles : ' + str(len(projectiles)) + ' god mode: ' + str(player.god_mode) +
                                    'b_health: ' + str(boss_health), True, 'white')
    if show_debug:
        screen.blit(debug_text, (10, screen.get_height() - 50))

    #high score logic
    if game_over:
        game_over_message()

        if not cheat_mode:
            if player.score > high_scores[-1][1] and not high_score_complete:
                update_high_scores(player.score)
                high_score_complete = True
        
        #Display High Scores
        high_scores = load_high_scores()
        scoreboard_font = pygame.font.Font(None, 30)
        scoreboard_title = scoreboard_font.render('Top 10 High Scores', True, 'white')
        screen.blit(scoreboard_title, (10, 50))

        for i, score in enumerate(high_scores, start=1):
            score_text = scoreboard_font.render(f'{score[0]} : {score[1]}', True, 'white')
            screen.blit(score_text, (10, 50 + i * 30))

    pygame.display.update()
    dt = clock.tick(1000) / 1000

pygame.quit()