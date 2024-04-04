import pygame, sys
 
clock = pygame.time.Clock()
 
from pygame.locals import *
pygame.init() # initiates pygame
 
pygame.display.set_caption('Platformeri')

WINDOW_SIZE = (800,500)

screen = pygame.display.set_mode(WINDOW_SIZE,0,32) # initiate the window 

display = pygame.Surface((800,500))
#'run'
player_png = pygame.image.load('Pelaaja.png')
dirt_image = pygame.image.load('Multa.png')
grass_image = pygame.image.load('Ruoho.png')


pygame.mixer.music.load('music.wav')
pygame.mixer.music.play(-1)

def load_map(path):

    f = open(path + '.txt', 'r')
    data = f.read()
    f.close()
    data = data.split('\n')
    game_map = []
    for row in data:
        game_map.append(list(row))
    return game_map

global animation_frames 
animation_frames = {}

def load_animation(path, frame_durations):
    global animation_frames
    animation_name = path.split('/')[-1]
    animation_frame_data = []
    n = 0 
    for frame in frame_durations:
        animation_frame_id = animation_name + '_' + str(n)
        img_loc = path + '/' + animation_frame_id + '.png'
        aniamtion_image = pygame.image.load(img_loc).convert()
        aniamtion_image.set_colorkey((255,255,255))
        animation_frames[animation_frame_id] = aniamtion_image.copy()
        for i in range (frame):
            animation_frame_data.append(animation_frame_id)
        n += 1
    return animation_frame_data

def change_action(action_var, frame, new_value):
    if action_var != new_value:
        action_var = new_value
        frame = 0 
    return action_var, frame

animation_database = {}

animation_database['walk'] = load_animation('animations/walk',[7,7])
animation_database['idle'] = load_animation('animations/idle',[15,15])

player_action = 'idle'
player_frame = 0
player_flip = False

game_map = load_map('map1')



moving_left = False
moving_right = False

def collision_test(rect, tiles):
    hit_list = []
    for tile in tiles:
        if rect.colliderect(tile): 
            hit_list.append(tile)
    return hit_list

def move(rect, movement, tiles):
    collision_types = {'top': False, 'bottom': False, 'right': False, 'left': False}
    rect.x += movement[0] 
    hit_list = collision_test(rect, tiles)  
    for tile in hit_list:
        if movement[0] > 0:
            rect.right = tile.left
            collision_types['right'] = True
        elif movement[0] < 0:
            rect.left = tile.right
            collision_types['left'] = True
    rect.y += movement[1]
    hit_list = collision_test(rect, tiles)
    for tile in hit_list:
        if movement[1] > 0:
            rect.bottom = tile.top
            collision_types['bottom'] = True
        elif movement[1] < 0:
            rect.top = tile.bottom
            collision_types['top'] = True
    return rect, collision_types



player_rect = pygame.Rect(50, 50, player_png.get_width(), player_png.get_height())

backround_objet = [[0.25,[120, 10, 70, 400]],[0.25,[280, 30, 40, 400]],[0.5, [30, 40, 40, 400]], [0.5,[130, 90, 100, 400]], [0.5,[300, 80, 20, 400]]]

test_rect = pygame.Rect(100,100,100,50)

player_y_momentum = 0

air_timer = 0

scroll = [0,0] 

TILE_SIZE = grass_image.get_width()

while True: # game loop

    scroll[0] += (player_rect.x-scroll[0]-152)/20
    scroll[1] += (player_rect.y-scroll[1]-200)/20

    display.fill((0, 100, 200))

    pygame.draw.rect(display,(7, 80, 75),pygame.Rect(30, 182, 600, 500))

    tile_rects = []

    y = 0 
    for row in game_map:
        x = 0
        for tile in row:
            if tile == '1':
                display.blit(dirt_image, (x * TILE_SIZE-scroll[0], y * TILE_SIZE-scroll[1]))
            if tile == '2':
                display.blit(grass_image, (x * TILE_SIZE-scroll[0], y * TILE_SIZE-scroll[1]))
            if tile != '0':
                tile_rects.append(pygame.Rect(x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))
            x += 1
        y += 1

    player_movement = [0, 0]
    if moving_right:
        player_movement[0] += 2
    if moving_left:
        player_movement[0] -= 2
    player_movement[1] += player_y_momentum
    player_y_momentum += 0.2
    if player_y_momentum > 3:
        player_y_momentum = 3

    if player_movement[0] > 0:
        player_action,player_frame = change_action(player_action, player_frame, 'walk')
        player_flip = False
    if player_movement[0] == 0:
        player_action,player_frame = change_action(player_action, player_frame, 'idle')        
    if player_movement[0] < 0:
        player_action,player_frame = change_action(player_action, player_frame, 'walk')
        player_flip = True

    
     
    player_rect, collisions = move(player_rect, player_movement, tile_rects)



    if collisions['bottom']: 
        player_y_momentum = 0
        air_timer = 0
        jump_counter = 0
    else:
        air_timer += 1

    player_frame += 1
    if player_frame >= len(animation_database[player_action]):
        player_frame = 0
    player_img_id = animation_database[player_action][player_frame]
    player_image = animation_frames[player_img_id]
    display.blit(pygame.transform.flip(player_image,player_flip,False), (player_rect.x-scroll[0], player_rect.y-scroll[1]))

    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_RIGHT:
                moving_right = True
            if event.key == K_LEFT:
                moving_left = True
            if event.key == K_SPACE:
                if jump_counter < 2:
                    player_y_momentum = -5
                    jump_counter += 1
        if event.type == KEYUP:
            if event.key == K_RIGHT:
                moving_right = False
            if event.key == K_LEFT:
                moving_left = False

    surf = pygame.transform.scale(display, WINDOW_SIZE)
    screen.blit(surf, (0, 0))
    pygame.display.update()
    clock.tick(60) # Maintain 60 fps 