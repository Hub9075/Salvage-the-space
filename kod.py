import pygame
import sys
import math
import random

pygame.init()
pygame.font.init()  # Inicjalizacja czcionek do UI

WIDTH, HEIGHT = 520, 480  # Zwiększyłem wysokość okna, żeby widzieć więcej podziemia
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("SS14 - Infinite Stars, Mining & World")

clock = pygame.time.Clock()
FONT = pygame.font.SysFont("Arial", 18, bold=True)

# --- SYSTEM RUD I WARTOŚCI ---
ORE_VALUES = {
    'coal': 10,
    'iron': 25,
    'quartz': 40,
    'lapiz': 60,
    'gold': 100,
    'emerald': 150,
    'rubin': 200,
    'sapphire': 250,
    'diament': 500,
    'uran': 1000,
    'alien_ore': 5000
}

# Kolory zastępcze (na wypadek gdybyś jeszcze nie miał grafik)
ORE_COLORS = {
    'stone': (40, 40, 45), 'coal': (20, 20, 20), 'iron': (210, 140, 80),
    'quartz': (220, 220, 220), 'lapiz': (20, 50, 200), 'gold': (255, 215, 0),
    'emerald': (0, 200, 50), 'rubin': (220, 20, 60), 'sapphire': (15, 80, 210),
    'diament': (0, 255, 255), 'uran': (100, 255, 0), 'alien_ore': (150, 0, 255)
}

# --- ŁADOWANIE ZASOBÓW ---
planet_img = pygame.image.load("image.png").convert_alpha()

TILE_SIZE = 64
player_img_right = pygame.image.load("image_prawo.png").convert_alpha()
player_img_right = pygame.transform.scale(player_img_right, (64, 64))
player_img_left = pygame.transform.flip(player_img_right, True, False)

# Słownik na tekstury kafelków (zwykły kamień + rudy)
TILES = {}
# 1. Zwykły kamień
stone_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
stone_img.fill(ORE_COLORS['stone'])
pygame.draw.rect(stone_img, (60, 60, 70), (0, 0, TILE_SIZE, TILE_SIZE), 1)
TILES['stone'] = stone_img

# 2. Ładowanie Twoich grafik rud (lub tworzenie zastępczych)
for ore in ORE_VALUES.keys():
    try:
        # Tutaj gra spróbuje załadować plik np. "coal.png", "iron.png" itd.
        img = pygame.image.load(f"{ore}.png").convert_alpha()
        TILES[ore] = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    except pygame.error:
        # Jeśli pliku nie ma, tworzy klocek z kolorem z tabeli ORE_COLORS
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE))
        surf.fill(ORE_COLORS[ore])
        pygame.draw.rect(surf, (0, 0, 0), (0, 0, TILE_SIZE, TILE_SIZE), 1)
        # Dodajemy mały tekst z pierwszą literą rudy, żeby było wiadomo co to
        txt = FONT.render(ore[0].upper(), True, (255, 255, 255))
        surf.blit(txt, (5, 5))
        TILES[ore] = surf

# --- GENEROWANIE GWIAZD ---
stars = []
for i in range(100):
    stars.append([
        random.randint(0, WIDTH), 
        random.randint(0, HEIGHT - 250), 
        random.randint(1, 3), 
        random.uniform(0.02, 0.1)
    ])

# --- ZMIENNE GRY ---
player_x = 0
speed = 5
# Podłoga zaczyna się na wysokości 200 pikseli
FLOOR_Y = 200
player_y = FLOOR_Y - 64 
current_img = player_img_right

money = 0  # Twój portfel

# --- DYNAMICZNY ŚWIAT (CHUNKI / PAMIĘĆ ZNISZCZONYCH BLOKÓW) ---
# Przechowujemy tu bloki, które gracz wykopał lub wygenerował: (tile_x, tile_y) -> 'nazwa_rudy' lub 'air'
world_map = {}

def get_tile_at(tx, ty):
    """Funkcja deterministycznie zwraca co jest na danych współrzędnych kafelka"""
    if ty < 0:
        return 'air' # Nad ziemią jest puste powietrze
        
    # Jeśli blok został już zmodyfikowany (wykopany), zwracamy jego stan z pamięci
    if (tx, ty) in world_map:
        return world_map[(tx, ty)]
    
    # Proceduralne generowanie rud na podstawie głębokości (ty)
    # Im głębiej (większe ty), tym rzadsze i droższe surowce
    seed = random.Random((tx, ty)) # Stały seed dla danej pozycji
    rand_val = seed.random()
    
    if ty == 0:
        return 'stone' # Pierwsza warstwa to zawsze czysty kamień
        
    # Szanse na rudy w zależności od głębokości
    if ty >= 8 and rand_val < 0.02: return 'alien_ore'
    if ty >= 6 and rand_val < 0.04: return 'uran'
    if ty >= 5 and rand_val < 0.06: return 'diament'
    if ty >= 4 and rand_val < 0.08: return 'sapphire'
    if ty >= 3 and rand_val < 0.10: return 'rubin'
    if ty >= 2 and rand_val < 0.12: return