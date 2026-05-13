import pygame
import sys
import math
import random

pygame.init()

WIDTH, HEIGHT = 520, 320
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SS14 - Infinite Stars & World")

clock = pygame.time.Clock()

# --- ŁADOWANIE ZASOBÓW ---
planet_img = pygame.image.load("image.png").convert_alpha()

TILE_SIZE = 64
tile_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
tile_img.fill((40, 40, 45)) 
pygame.draw.rect(tile_img, (60, 60, 70), (0, 0, TILE_SIZE, TILE_SIZE), 1)

player_img_right = pygame.image.load("image_prawo.png").convert_alpha()
player_img_right = pygame.transform.scale(player_img_right, (64, 64))
player_img_left = pygame.transform.flip(player_img_right, True, False)

# --- GENEROWANIE GWIAZD ---
stars = []
for i in range(100):
    # Każda gwiazda to: [x, y, rozmiar, prędkość_paralaksy]
    stars.append([
        random.randint(0, WIDTH), 
        random.randint(0, HEIGHT - 100), 
        random.randint(1, 3), 
        random.uniform(0.02, 0.1) # Im mniejsza liczba, tym dalej jest gwiazda
    ])

# --- ZMIENNE ---
player_x = 0
speed = 5
player_y = HEIGHT - TILE_SIZE - 64 
current_img = player_img_right

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    dx = 0
    if keys[pygame.K_LEFT]:
        dx = -speed
        current_img = player_img_left
    if keys[pygame.K_RIGHT]:
        dx = speed
        current_img = player_img_right
    
    player_x += dx
    cam_x = player_x - (WIDTH // 2)

    # --- RYSOWANIE ---
    screen.fill((5, 5, 15)) # Bardzo ciemny granat

    # 1. WARSTWA: NIESKOŃCZONE GWIAZDY
    for star in stars:
        # Obliczamy pozycję gwiazdy na ekranie na podstawie ruchu gracza
        # Star[3] to indywidualna prędkość paralaksy dla tej gwiazdy
        star_x = (star[0] - cam_x * star[3]) % WIDTH
        
        # Rysujemy gwiazdę jako małe kółko lub prostokąt
        color = (200, 200, 255) if star[2] > 1 else (100, 100, 150)
        pygame.draw.circle(screen, color, (int(star_x), star[1]), star[2])

    # 2. WARSTWA: PLANETA
    planet_x_display = math.floor(-cam_x * 0.2)
    screen.blit(planet_img, (planet_x_display, 40))

    # 3. WARSTWA: NIESKOŃCZONA PODŁOGA
    start_tile = int(cam_x // TILE_SIZE)
    for i in range(start_tile, start_tile + (WIDTH // TILE_SIZE) + 2):
        draw_x = i * TILE_SIZE - cam_x
        screen.blit(tile_img, (draw_x, HEIGHT - TILE_SIZE))

    # 4. WARSTWA: GRACZ
    screen.blit(current_img, (WIDTH // 2, player_y))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()