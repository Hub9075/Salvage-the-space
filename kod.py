import pygame
import sys
import math
import random
import os
import json

pygame.init()
pygame.font.init()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_FILE = os.path.join(BASE_DIR, "savegame.json")

VIRTUAL_WIDTH, VIRTUAL_HEIGHT = 900, 850  
window_width, window_height = VIRTUAL_WIDTH, VIRTUAL_HEIGHT

screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)
pygame.display.set_caption("GALAXY Mine, Shop & Survival")

virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
transition_overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
pause_overlay = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)  # Warstwa pod menu pauzy

clock = pygame.time.Clock()

BG_DEEP = (3, 3, 12)
PANEL_DARK = (15, 15, 30)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GOLD = (255, 215, 0)
WHITE = (230, 230, 250)
SUCCESS = (0, 255, 150)
DANGER = (255, 50, 80)
ORANGE = (255, 140, 0)
GRAY = (100, 100, 110)

def get_font(size, bold=False):
    return pygame.font.SysFont("DejaVu Sans, Liberation Sans, Arial", size, bold=bold)

font_huge = get_font(52, True)
font_title = get_font(30, True)
font_main = get_font(18, True)
font_small = get_font(14)

ores = {
    "coal": {"qty": 0, "price": 10, "label": "Węgiel"},
    "iron": {"qty": 0, "price": 25, "label": "Żelazo"},
    "quartz": {"qty": 0, "price": 40, "label": "Kwarc"},
    "lapiz": {"qty": 0, "price": 60, "label": "Lapis"},
    "gold": {"qty": 0, "price": 100, "label": "Złoto"},
    "emerald": {"qty": 0, "price": 150, "label": "Szmaragd"},
    "rubin": {"qty": 0, "price": 200, "label": "Rubin"},
    "sapphire": {"qty": 0, "price": 250, "label": "Szafir"},
    "diament": {"qty": 0, "price": 500, "label": "Diament"},
    "uran": {"qty": 0, "price": 1000, "label": "Uran"},
    "alien_ore": {"qty": 0, "price": 5000, "label": "Kosmiczna Ruda"},
}

world_map = {}       
block_durability = {} 

def save_game():
    try:
        serialized_world = {f"{k[0]},{k[1]}": v for k, v in world_map.items()}
        save_data = {
            "wallet": wallet,
            "upgrades_inventory": upgrades_inventory,
            "hunger": hunger,
            "thirst": thirst,
            "fuel": fuel,
            "player_x": player_x,
            "player_y": player_y,
            "player_inventory": player_inventory,
            "ores_qty": {k: v["qty"] for k, v in ores.items()},
            "world_map": serialized_world
        }
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=4, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Błąd zapisu: {e}")
        return False

def load_game():
    global wallet, upgrades_inventory, hunger, thirst, fuel, player_inventory, ores, world_map, block_durability, player_x, player_y, vel_y, current_state, is_dead
    if not os.path.exists(SAVE_FILE):
        return False
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            save_data = json.load(f)
            
        wallet = save_data.get("wallet", 1000)
        upgrades_inventory = save_data.get("upgrades_inventory", [])
        hunger = save_data.get("hunger", 100.0)
        thirst = save_data.get("thirst", 100.0)
        fuel = save_data.get("fuel", 100.0)
        player_x = save_data.get("player_x", 100)
        player_y = save_data.get("player_y", 200)
        player_inventory = save_data.get("player_inventory", {"chleb": 2, "kurczak": 1, "woda": 2, "paliwo_kanister": 1})
        
        saved_ores = save_data.get("ores_qty", {})
        for k in ores:
            if k in saved_ores:
                ores[k]["qty"] = saved_ores[k]
                
        world_map.clear()
        block_durability.clear()
        saved_world = save_data.get("world_map", {})
        for k, v in saved_world.items():
            try:
                tx, ty = map(int, k.split(","))
                world_map[(tx, ty)] = v
            except:
                pass
                
        vel_y = 0
        is_dead = False
        return True
    except Exception as e:
        print(f"Błąd odczytu: {e}")
        return False

def reset_game():
    global wallet, upgrades_inventory, hunger, thirst, fuel, player_inventory, ores, world_map, block_durability, player_x, player_y, vel_y, current_state, is_dead, death_timer
    wallet = 1000  
    upgrades_inventory = [] 
    hunger = 100.0
    thirst = 100.0
    fuel = 100.0
    player_x, player_y = 100, 200 - PLAYER_HEIGHT
    vel_y = 0
    current_state = "GAME"
    is_dead = False
    death_timer = 0
    
    world_map.clear()
    block_durability.clear()

    player_inventory = {"chleb": 2, "kurczak": 1, "woda": 2, "paliwo_kanister": 1}
    for ore in ores:
        ores[ore]["qty"] = 0

HUNGER_DECAY = 0.015    
THIRST_DECAY = 0.02     
FUEL_CONSUMPTION = 0.4  

items_data = {
    "chleb": {"label": "Chleb", "restore_type": "hunger", "amount": 20, "price": 15, "desc": "Przywraca 20 pkt głodu"},
    "kurczak": {"label": "Pieczony Kurczak", "restore_type": "hunger", "amount": 60, "price": 40, "desc": "Przywraca 60 pkt głodu"},
    "woda": {"label": "Woda Kosmiczna", "restore_type": "thirst", "amount": 40, "price": 10, "desc": "Przywraca 40 pkt pragnienia"},
    "paliwo_kanister": {"label": "Kanister Paliwa", "restore_type": "fuel", "amount": 50, "price": 30, "desc": "Tankuje 50 pkt paliwa jetpacka"}
}

shop_items = {
    "ENCHANTY": [
        {"name": "Efficiency I", "price": 10000, "desc": "Szybkość kopania I (+1 dmg)", "power": 1},
        {"name": "Efficiency II", "price": 50000, "desc": "Szybkość kopania II (+2 dmg)", "power": 2},
        {"name": "Efficiency III", "price": 250000, "desc": "Szybkość kopania III (+3 dmg)", "power": 3},
        {"name": "Efficiency IV", "price": 1000000, "desc": "Szybkość kopania IV (+4 dmg)", "power": 4},
        {"name": "Efficiency V", "price": 50000000, "desc": "Szybkość kopania V (+5 dmg)", "power": 5},
    ],
    "ŻYWNOŚĆ I PALIWO": [
        {"id": "chleb", "price": 15},
        {"id": "kurczak", "price": 40},
        {"id": "woda", "price": 10},
        {"id": "paliwo_kanister", "price": 30}
    ]
}

current_state = "MENU" 
current_tab = "ENCHANTY"
sell_page = 0  
is_dead = False
death_timer = 0

transition_active = False
transition_alpha = 0
transition_target_state = None

meteors = []
for _ in range(5):
    meteors.append({
        "x": random.randint(0, VIRTUAL_WIDTH),
        "y": random.randint(-200, 0),
        "speed": random.uniform(4, 9),
        "length": random.randint(30, 70),
        "width": random.randint(1, 3)
    })

def start_transition(target):
    global transition_active, transition_alpha, transition_target_state
    if not transition_active:
        transition_active = True
        transition_alpha = 0
        transition_target_state = target

def update_meteors():
    for m in meteors:
        m["x"] -= m["speed"] * 0.7
        m["y"] += m["speed"]
        if m["y"] > VIRTUAL_HEIGHT or m["x"] < -100:
            m["x"] = random.randint(200, VIRTUAL_WIDTH + 200)
            m["y"] = random.randint(-150, -50)
            m["speed"] = random.uniform(4, 9)
            m["length"] = random.randint(30, 70)

def draw_meteors(surf):
    for m in meteors:
        start_pos = (m["x"], m["y"])
        end_pos = (m["x"] + m["length"] * 0.7, m["y"] - m["length"])
        pygame.draw.line(surf, (200, 220, 255), start_pos, end_pos, m["width"])

casino_bet = 100
casino_bet_input_text = "100"  
casino_input_active = False    
casino_chosen_color = "RED"  
roulette_spinning = False
roulette_timer = 0
roulette_display_value = ""
roulette_result_color = None
casino_message = ""
casino_message_color = WHITE

ROULETTE_NUMBERS = [
    (0, "GREEN"), (32, "RED"), (15, "BLACK"), (19, "RED"), (4, "BLACK"),
    (21, "RED"), (2, "BLACK"), (25, "RED"), (17, "BLACK"), (34, "RED"),
    (6, "BLACK"), (27, "RED"), (13, "BLACK"), (36, "RED"), (11, "BLACK"),
    (30, "RED"), (8, "BLACK"), (23, "RED"), (10, "BLACK"), (5, "RED"),
    (24, "BLACK"), (16, "RED"), (33, "BLACK"), (1, "RED"), (20, "BLACK"),
    (14, "RED"), (31, "BLACK"), (9, "RED"), (22, "BLACK"), (18, "RED"),
    (29, "BLACK"), (7, "RED"), (28, "BLACK"), (12, "RED"), (35, "BLACK"),
    (3, "RED"), (26, "BLACK")
]

class Button:
    def __init__(self, text, x, y, w, h, color, accent, border=2):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.accent = accent
        self.border = border

    def draw(self, surface, mouse_pos, disabled=False):
        hover = self.rect.collidepoint(mouse_pos) and not disabled
        if hover:
            pygame.draw.rect(surface, self.accent, self.rect.inflate(6, 6), 1, border_radius=10)
        c = GRAY if disabled else (self.color if not hover else [min(255, col+20) for col in self.color])
        a = GRAY if disabled else self.accent
        pygame.draw.rect(surface, c, self.rect, border_radius=8)
        pygame.draw.rect(surface, a, self.rect, self.border, border_radius=8)
        txt = font_main.render(self.text, True, (170, 170, 170) if disabled else WHITE)
        surface.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.centery - txt.get_height()//2))

    def clicked(self, event, mouse_pos, disabled=False):
        if disabled: return False
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(mouse_pos)

btn_menu_start = Button("START NOWA GRA", VIRTUAL_WIDTH // 2 - 150, 320, 300, 55, PANEL_DARK, CYAN, 3)
btn_menu_load = Button("WCZYTAJ ZAPIS", VIRTUAL_WIDTH // 2 - 150, 410, 300, 55, PANEL_DARK, GOLD, 2)
btn_menu_exit = Button("WYJDŹ Z GRY", VIRTUAL_WIDTH // 2 - 150, 500, 300, 55, PANEL_DARK, DANGER, 2)

btn_open_shop = Button("SKLEP (E)", 15, 15, 110, 35, PANEL_DARK, CYAN)
btn_open_sell = Button("SPRZEDAŻ", 135, 15, 110, 35, PANEL_DARK, SUCCESS)
btn_open_casino = Button("KASYNO", 255, 15, 110, 35, PANEL_DARK, MAGENTA)
btn_open_inv = Button("EQ (I)", 375, 15, 80, 35, PANEL_DARK, ORANGE)

btn_save_game = Button("ZAPISZ GRĘ", 465, 15, 120, 35, PANEL_DARK, GOLD)
btn_go_lobby = Button("LOBBY (MENU)", 595, 15, 130, 35, PANEL_DARK, DANGER)

btn_close_ui = Button("POWRÓT DO GRY", VIRTUAL_WIDTH - 190, 15, 175, 35, (40, 40, 50), CYAN)
btn_sell_all = Button("SPRZEDAJ WSZYSTKO", VIRTUAL_WIDTH - 430, 15, 220, 35, DANGER, WHITE)

btn_prev_page = Button("<", 30, VIRTUAL_HEIGHT - 70, 60, 40, PANEL_DARK, CYAN)
btn_next_page = Button(">", VIRTUAL_WIDTH - 90, VIRTUAL_HEIGHT - 70, 60, 40, PANEL_DARK, CYAN)

btn_bet_red = Button("CZERWONY (x2)", 150, 450, 180, 50, (180, 20, 20), WHITE)
btn_bet_black = Button("CZARNY (x2)", 360, 450, 180, 50, (20, 20, 20), WHITE)
btn_bet_green = Button("ZIELONY (x14)", 570, 450, 180, 50, (20, 150, 50), WHITE)

btn_bet_minus = Button("-100$", 160, 530, 100, 40, PANEL_DARK, DANGER)
btn_bet_plus = Button("+100$", 640, 530, 100, 40, PANEL_DARK, SUCCESS)
btn_bet_all_in = Button("ALL IN", 400, 590, 100, 40, PANEL_DARK, GOLD)

btn_spin = Button("LOSUJ! 🎰", VIRTUAL_WIDTH // 2 - 100, 660, 200, 60, (100, 30, 150), MAGENTA)


btn_pause_resume = Button("WRÓĆ DO GRY", VIRTUAL_WIDTH // 2 - 150, 330, 300, 50, (40, 45, 60), CYAN)
btn_pause_save_exit = Button("ZAPISZ I WYJDŹ", VIRTUAL_WIDTH // 2 - 150, 410, 300, 50, (20, 50, 30), SUCCESS)
btn_pause_exit = Button("WYJDŹ BEZ ZAPISU", VIRTUAL_WIDTH // 2 - 150, 490, 300, 50, PANEL_DARK, DANGER)

casino_input_rect = pygame.Rect(VIRTUAL_WIDTH // 2 - 100, 530, 200, 40)

TILE_SIZE = 64
PLAYER_WIDTH, PLAYER_HEIGHT = 54, 54

def create_dummy_surface(w, h, color):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill(color)
    return s

try:
    planet_path = os.path.join(BASE_DIR, "enlarged.png")
    planet_img = pygame.image.load(planet_path).convert_alpha()
    planet_img = pygame.transform.scale(planet_img, (140, 80))
except:
    planet_img = create_dummy_surface(140, 80, (100, 50, 150))

try:
    player_path = os.path.join(BASE_DIR, "image_prawo.png")
    player_img_right = pygame.image.load(player_path).convert_alpha()
    player_img_right = pygame.transform.scale(player_img_right, (TILE_SIZE, TILE_SIZE))
except:
    player_img_right = create_dummy_surface(TILE_SIZE, TILE_SIZE, (0, 200, 255))

player_img_left = pygame.transform.flip(player_img_right, True, False)

try:
    ore_path = os.path.join(BASE_DIR, "pixil-frame-0_13.png")
    ore_overlay_img = pygame.image.load(ore_path).convert_alpha()
    ore_overlay_img = pygame.transform.scale(ore_overlay_img, (TILE_SIZE, TILE_SIZE))
except:
    ore_overlay_img = create_dummy_surface(TILE_SIZE, TILE_SIZE, (255, 255, 0))

try:
    pickaxe_path = os.path.join(BASE_DIR, "pixil-frame-0_4.png")
    pickaxe_img = pygame.image.load(pickaxe_path).convert_alpha()
    pickaxe_img = pygame.transform.scale(pickaxe_img, (32, 32)) 
except:
    pickaxe_img = create_dummy_surface(32, 32, GOLD)

jetpack_fire_img = create_dummy_surface(16, 24, (255, 100, 0))

TILES = {}
stone_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
stone_img.fill((40, 40, 45))
pygame.draw.rect(stone_img, (60, 60, 70), (0, 0, TILE_SIZE, TILE_SIZE), 1)
TILES['stone'] = stone_img

reset_game()
current_state = "MENU"

for ore in ores.keys():
    ore_tile = stone_img.copy()
    ore_tile.blit(ore_overlay_img, (0, 0))
    TILES[ore] = ore_tile

bg_asteroids = []
for i in range(40):
    size = random.randint(24, 64)
    bg_asteroids.append({
        'texture': create_dummy_surface(size, size, (80, 80, 85)),
        'wx': random.randint(-1500, 2500),
        'wy': random.randint(-6000, -400), 
        'factor': random.uniform(0.08, 0.18)
    })

stars = [[random.randint(0, VIRTUAL_WIDTH), random.randint(0, VIRTUAL_HEIGHT), random.randint(1, 3), random.uniform(0.02, 0.1)] for _ in range(150)]

speed = 5
FLOOR_Y = 260 
current_img = player_img_right
facing_right = True

mining_animation_timer = 0
MINING_DURATION = 8 
GRAVITY = 0.5
TERMINAL_VELOCITY = 10
JETPACK_THRUST = -0.9 
is_using_jetpack = False

surface_alert_timer = 0  
save_alert_timer = 0  

def is_on_surface():
    return player_y <= (FLOOR_Y - PLAYER_HEIGHT + 10)

def get_mining_power():
    power = 1
    for item in shop_items["ENCHANTY"]:
        if item["name"] in upgrades_inventory:
            power = max(power, 1 + item["power"])
    return power

def get_block_max_hp(ty):
    if ty <= 2: return 1   
    if ty <= 5: return 2   
    if ty <= 8: return 3   
    return 4               

def get_tile_at(tx, ty):
    if ty < 0: return 'air'
    if (tx, ty) in world_map: return world_map[(tx, ty)]
    seed = random.Random(f"{tx}_{ty}")
    if ty > 0 and seed.random() < 0.25: return 'air'
    rand_val = seed.random()
    if ty == 0: return 'stone'
    if ty >= 8 and rand_val < 0.02: return 'alien_ore'
    if ty >= 6 and rand_val < 0.04: return 'uran'
    if ty >= 5 and rand_val < 0.06: return 'diament'
    if ty >= 4 and rand_val < 0.08: return 'sapphire'
    if ty >= 3 and rand_val < 0.10: return 'rubin'
    if ty >= 2 and rand_val < 0.12: return 'emerald'
    if ty >= 2 and rand_val < 0.15: return 'gold'
    if ty >= 1 and rand_val < 0.18: return 'lapiz'
    if ty >= 1 and rand_val < 0.22: return 'quartz'
    if rand_val < 0.28: return 'iron'
    if rand_val < 0.35: return 'coal'
    return 'stone'

def get_collidable_rects(p_x, p_y):
    start_tx = int((p_x - TILE_SIZE) // TILE_SIZE)
    end_tx = int((p_x + PLAYER_WIDTH + TILE_SIZE) // TILE_SIZE)
    start_ty = int((p_y - FLOOR_Y - TILE_SIZE) // TILE_SIZE)
    end_ty = int((p_y - FLOOR_Y + PLAYER_HEIGHT + TILE_SIZE) // TILE_SIZE)
    rects = []
    for ty in range(max(0, start_ty), end_ty + 1):
        for tx in range(start_tx, end_tx + 1):
            if get_tile_at(tx, ty) != 'air':
                rects.append(pygame.Rect(tx * TILE_SIZE, FLOOR_Y + (ty * TILE_SIZE), TILE_SIZE, TILE_SIZE))
    return rects

def get_sell_cards():
    cards = []
    padding_x, padding_y = 50, 120
    card_height, card_spacing = 130, 25  
    cols = 2
    card_width = (VIRTUAL_WIDTH - padding_x * 2 - 30) // cols
    btn_w = 140
    ore_items = list(ores.items())
    start_idx = sell_page * 6
    end_idx = start_idx + 6
    page_items = ore_items[start_idx:end_idx]
    for idx, (name, data) in enumerate(page_items):
        row, col = idx // cols, idx % cols
        x = padding_x + col * (card_width + 30)
        y = padding_y + row * (card_height + card_spacing)
        card = pygame.Rect(x, y, card_width, card_height)
        button = pygame.Rect(card.right - btn_w - 20, y + (card_height // 2) - 25, btn_w, 50)
        cards.append((name, data, card, button))
    return cards

def draw_stars(surf):
    surf.fill(BG_DEEP)
    for star in stars:
        pygame.draw.circle(surf, (200, 200, 255), (star[0], star[1]), star[2])

def draw_menu(surf, mouse_pos):
    draw_stars(surf)
    update_meteors()
    draw_meteors(surf)
    
    title_main = font_huge.render("GALAXY MINE", True, CYAN)
    title_sub = font_title.render("Shop & Survival Simulator", True, MAGENTA)
    
    surf.blit(title_main, (VIRTUAL_WIDTH // 2 - title_main.get_width() // 2, 120))
    surf.blit(title_sub, (VIRTUAL_WIDTH // 2 - title_sub.get_width() // 2, 200))
    
    btn_menu_start.draw(surf, mouse_pos)
    has_save = os.path.exists(SAVE_FILE)
    btn_menu_load.draw(surf, mouse_pos, disabled=not has_save)
    btn_menu_exit.draw(surf, mouse_pos)

def draw_header(surf, mouse_pos):
    pygame.draw.rect(surf, (10, 10, 25), (0, 0, VIRTUAL_WIDTH, 90))
    pygame.draw.line(surf, CYAN, (0, 90), (VIRTUAL_WIDTH, 90), 2)
    w_txt = font_title.render(f"CREDITS: {wallet}$", True, GOLD)
    surf.blit(w_txt, (30, 25))
    btn_close_ui.draw(surf, mouse_pos)

def draw_status_bars(surf, x, y):
    bars = [
        {"val": hunger, "color": (200, 50, 50), "label": f"Głód: {int(hunger)}%"},
        {"val": thirst, "color": (50, 150, 255), "label": f"Pragnienie: {int(thirst)}%"},
        {"val": fuel, "color": (255, 165, 0), "label": f"Paliwo: {int(fuel)}%"}
    ]
    for i, bar in enumerate(bars):
        bx, by = x, y + (i * 22)
        pygame.draw.rect(surf, (40, 40, 50), (bx, by, 140, 16), border_radius=4)
        w = int((max(0, bar["val"]) / 100) * 140)
        if w > 0:
            pygame.draw.rect(surf, bar["color"], (bx, by, w, 16), border_radius=4)
        txt = font_small.render(bar["label"], True, WHITE)
        surf.blit(txt, (bx + 5, by + 1))

def draw_shop(surf, mouse_pos):
    draw_stars(surf)
    draw_header(surf, mouse_pos)
    
    tabs = ["ENCHANTY", "ŻYWNOŚĆ I PALIWO", "SEKTOR W BUDOWIE"] 
    for i, t in enumerate(tabs):
        t_rect = pygame.Rect(30 + i*230, 110, 210, 40)
        active = current_tab == t
        pygame.draw.rect(surf, CYAN if active else PANEL_DARK, t_rect, border_radius=5)
        txt = font_main.render(t, True, BG_DEEP if active else WHITE)
        surf.blit(txt, (t_rect.centerx - txt.get_width()//2, t_rect.centery - txt.get_height()//2))

    if current_tab == "SEKTOR W BUDOWIE":
        under_construction_box = pygame.Rect(30, 180, 840, 400)
        pygame.draw.rect(surf, PANEL_DARK, under_construction_box, border_radius=15)
        pygame.draw.rect(surf, DANGER, under_construction_box, 2, border_radius=15)
        warn_txt1 = font_title.render("⚠️ STREFA ZABLOKOWANA ⚠️", True, DANGER)
        warn_txt2 = font_main.render("Trwają prace inżynieryjne nad nowym sektorem handlowym.", True, WHITE)
        warn_txt3 = font_small.render("Nowe technologie i statki kosmiczne zostaną udostępnione wkrótce.", True, (160, 160, 180))
        surf.blit(warn_txt1, (under_construction_box.centerx - warn_txt1.get_width()//2, under_construction_box.y + 120))
        surf.blit(warn_txt2, (under_construction_box.centerx - warn_txt2.get_width()//2, under_construction_box.y + 190))
        surf.blit(warn_txt3, (under_construction_box.centerx - warn_txt3.get_width()//2, under_construction_box.y + 240))

    elif current_tab == "ŻYWNOŚĆ I PALIWO":
        for i, item in enumerate(shop_items["ŻYWNOŚĆ I PALIWO"]):
            y_pos = 170 + (i * 120)
            card = pygame.Rect(30, y_pos, 840, 100)
            pygame.draw.rect(surf, PANEL_DARK, card, border_radius=12)
            pygame.draw.rect(surf, ORANGE, card, 1, border_radius=12)
            
            item_info = items_data[item["id"]]
            surf.blit(font_main.render(item_info["label"], True, WHITE), (50, y_pos + 20))
            surf.blit(font_small.render(item_info["desc"], True, (160, 160, 180)), (50, y_pos + 55))
            
            price_txt = font_main.render(f"{item['price']}$", True, GOLD)
            surf.blit(price_txt, (600, y_pos + 35))
            
            buy_rect = pygame.Rect(720, y_pos + 25, 120, 50)
            pygame.draw.rect(surf, SUCCESS if wallet >= item["price"] else (60,60,60), buy_rect, border_radius=8)
            bt = font_main.render("KUPUJ", True, WHITE)
            surf.blit(bt, (buy_rect.centerx - bt.get_width()//2, buy_rect.centery - bt.get_height()//2))
    else:
        for i, item in enumerate(shop_items["ENCHANTY"]):
            y_pos = 170 + (i * 120)
            card = pygame.Rect(30, y_pos, 840, 100)
            pygame.draw.rect(surf, PANEL_DARK, card, border_radius=12)
            pygame.draw.rect(surf, CYAN, card, 1, border_radius=12)
            
            surf.blit(font_main.render(item["name"], True, WHITE), (50, y_pos + 20))
            surf.blit(font_small.render(item["desc"], True, (160, 160, 180)), (50, y_pos + 55))
            
            price_txt = font_main.render(f"{item['price']}$", True, GOLD)
            surf.blit(price_txt, (600, y_pos + 35))
            
            owned = item["name"] in upgrades_inventory
            buy_rect = pygame.Rect(720, y_pos + 25, 120, 50)
            pygame.draw.rect(surf, SUCCESS if wallet >= item["price"] and not owned else (60,60,60), buy_rect, border_radius=8)
            b_label = "POSIADASZ" if owned else "KUPUJ"
            bt = font_main.render(b_label, True, WHITE)
            surf.blit(bt, (buy_rect.centerx - bt.get_width()//2, buy_rect.centery - bt.get_height()//2))

def draw_sell(surf, mouse_pos):
    draw_stars(surf)
    draw_header(surf, mouse_pos)
    btn_sell_all.draw(surf, mouse_pos)
    
    total_pages = math.ceil(len(ores) / 6)
    for name, data, card, s_btn in get_sell_cards():
        pygame.draw.rect(surf, PANEL_DARK, card, border_radius=15)
        pygame.draw.rect(surf, CYAN, card, 1, border_radius=15) 
        surf.blit(font_main.render(f"{data['label']}", True, WHITE), (card.x + 25, card.y + 30))
        surf.blit(font_small.render(f"ILOSC: {data['qty']}", True, CYAN), (card.x + 25, card.y + 65))
        surf.blit(font_small.render(f"Cena: {data['price']}$", True, GOLD), (card.x + 25, card.y + 85))
        
        pygame.draw.rect(surf, SUCCESS if data['qty'] > 0 else (60,60,60), s_btn, border_radius=8)
        label = font_main.render("SPRZEDAJ 1", True, WHITE)
        surf.blit(label, (s_btn.centerx - label.get_width()//2, s_btn.centery - label.get_height()//2))
        
    if sell_page > 0: btn_prev_page.draw(surf, mouse_pos)
    if sell_page < total_pages - 1: btn_next_page.draw(surf, mouse_pos)
    page_txt = font_main.render(f"Strona {sell_page + 1} / {total_pages}", True, WHITE)
    surf.blit(page_txt, (VIRTUAL_WIDTH // 2 - page_txt.get_width() // 2, VIRTUAL_HEIGHT - 60))

def draw_casino(surf, mouse_pos):
    global roulette_spinning, roulette_timer, roulette_display_value, roulette_result_color, casino_message, casino_message_color, wallet, casino_bet
    draw_stars(surf)
    draw_header(surf, mouse_pos)

    main_rect = pygame.Rect(50, 110, VIRTUAL_WIDTH - 100, 220)
    pygame.draw.rect(surf, PANEL_DARK, main_rect, border_radius=20)
    pygame.draw.rect(surf, MAGENTA, main_rect, 2, border_radius=20)

    title = font_title.render("GALAXY CASINO - RULETKA", True, MAGENTA)
    surf.blit(title, (main_rect.centerx - title.get_width()//2, main_rect.y + 15))

    if roulette_spinning:
        roulette_timer -= 1
        temp_num, temp_color = random.choice(ROULETTE_NUMBERS)
        roulette_display_value = str(temp_num)
        if temp_color == "RED": roulette_result_color = (200, 30, 30)
        elif temp_color == "BLACK": roulette_result_color = (30, 30, 30)
        else: roulette_result_color = (30, 180, 5)

        if roulette_timer <= 0:
            roulette_spinning = False
            final_num, final_color = random.choice(ROULETTE_NUMBERS)
            roulette_display_value = str(final_num)
            
            if final_color == "RED": roulette_result_color = (200, 30, 30)
            elif final_color == "BLACK": roulette_result_color = (30, 30, 30)
            else: roulette_result_color = (30, 180, 5)

            if final_color == casino_chosen_color:
                multiplier = 14 if final_color == "GREEN" else 2
                win_amount = casino_bet * multiplier
                wallet += win_amount
                casino_message = f"WYGRANA! +{win_amount}$ (Wylosowano: {final_num} {final_color})"
                casino_message_color = SUCCESS
            else:
                casino_message = f"PRZEGRANA! (Wylosowano: {final_num} {final_color})"
                casino_message_color = DANGER

    spin_box = pygame.Rect(VIRTUAL_WIDTH // 2 - 80, main_rect.y + 70, 160, 90)
    box_color = roulette_result_color if roulette_result_color else (40, 40, 50)
    pygame.draw.rect(surf, box_color, spin_box, border_radius=10)
    pygame.draw.rect(surf, GOLD, spin_box, 3, border_radius=10)

    if roulette_display_value:
        num_txt = font_huge.render(roulette_display_value, True, WHITE)
        surf.blit(num_txt, (spin_box.centerx - num_txt.get_width()//2, spin_box.centery - num_txt.get_height()//2))
    else:
        num_txt = font_main.render("ZAKRĘĆ", True, WHITE)
        surf.blit(num_txt, (spin_box.centerx - num_txt.get_width()//2, spin_box.centery - num_txt.get_height()//2))

    if casino_message:
        msg_txt = font_main.render(casino_message, True, casino_message_color)
        surf.blit(msg_txt, (VIRTUAL_WIDTH // 2 - msg_txt.get_width()//2, main_rect.bottom + 20))

    bet_info = font_title.render(f"Twój wybór: {casino_chosen_color}", True, CYAN)
    surf.blit(bet_info, (VIRTUAL_WIDTH // 2 - bet_info.get_width()//2, 390))

    btn_bet_red.draw(surf, mouse_pos)
    btn_bet_black.draw(surf, mouse_pos)
    btn_bet_green.draw(surf, mouse_pos)

    if casino_chosen_color == "RED": pygame.draw.rect(surf, GOLD, btn_bet_red.rect.inflate(10,10), 3, border_radius=12)
    elif casino_chosen_color == "BLACK": pygame.draw.rect(surf, GOLD, btn_bet_black.rect.inflate(10,10), 3, border_radius=12)
    elif casino_chosen_color == "GREEN": pygame.draw.rect(surf, GOLD, btn_bet_green.rect.inflate(10,10), 3, border_radius=12)

    pygame.draw.rect(surf, (25, 25, 50) if not casino_input_active else (40, 40, 80), casino_input_rect, border_radius=8)
    pygame.draw.rect(surf, GOLD if casino_input_active else CYAN, casino_input_rect, 2, border_radius=8)
    
    input_text_surf = font_main.render(casino_bet_input_text + ("|" if casino_input_active and pygame.time.get_ticks() // 500 % 2 == 0 else ""), True, WHITE)
    surf.blit(input_text_surf, (casino_input_rect.centerx - input_text_surf.get_width()//2, casino_input_rect.centery - input_text_surf.get_height()//2))

    btn_bet_minus.draw(surf, mouse_pos)
    btn_bet_plus.draw(surf, mouse_pos)
    btn_bet_all_in.draw(surf, mouse_pos)

    if not roulette_spinning: btn_spin.draw(surf, mouse_pos)

def draw_inventory(surf, mouse_pos):
    draw_stars(surf)
    draw_header(surf, mouse_pos)
    
    title = font_title.render("EKWIPUNEK PRZETRWANIA", True, ORANGE)
    surf.blit(title, (50, 110))
    draw_status_bars(surf, 680, 110)
    
    for i, (item_id, qty) in enumerate(player_inventory.items()):
        info = items_data[item_id]
        y_pos = 180 + (i * 105)
        
        card_rect = pygame.Rect(50, y_pos, 800, 90)
        pygame.draw.rect(surf, PANEL_DARK, card_rect, border_radius=10)
        pygame.draw.rect(surf, ORANGE, card_rect, 1, border_radius=10)
        
        surf.blit(font_main.render(f"{info['label']} (Ilość: {qty})", True, WHITE), (70, y_pos + 20))
        surf.blit(font_small.render(info["desc"], True, (170, 170, 180)), (70, y_pos + 50))
        
        use_btn = pygame.Rect(680, y_pos + 20, 140, 50)
        pygame.draw.rect(surf, (40, 120, 40) if qty > 0 else (50, 50, 50), use_btn, border_radius=8)
        
        btn_label = "UŻYJ / ZJEDZ" if info["restore_type"] != "fuel" else "ZATANKUJ"
        u_txt = font_small.render(btn_label, True, WHITE)
        surf.blit(u_txt, (use_btn.centerx - u_txt.get_width()//2, use_btn.centery - u_txt.get_height()//2))

def draw_pause_menu(surf, mouse_pos):
    pause_overlay.fill((10, 10, 20, 180))
    surf.blit(pause_overlay, (0, 0))

    menu_box = pygame.Rect(VIRTUAL_WIDTH // 2 - 200, 200, 400, 380)
    pygame.draw.rect(surf, PANEL_DARK, menu_box, border_radius=15)
    pygame.draw.rect(surf, CYAN, menu_box, 2, border_radius=15)
    
    p_txt = font_title.render("GRA ZATRZYMANA", True, CYAN)
    surf.blit(p_txt, (menu_box.centerx - p_txt.get_width() // 2, menu_box.y + 40))
    
    btn_pause_resume.draw(surf, mouse_pos)
    btn_pause_save_exit.draw(surf, mouse_pos)
    btn_pause_exit.draw(surf, mouse_pos)

running = True
while running:
    real_mouse_pos = pygame.mouse.get_pos()
    virtual_mouse_pos = (
        int(real_mouse_pos[0] * (VIRTUAL_WIDTH / window_width)),
        int(real_mouse_pos[1] * (VIRTUAL_HEIGHT / window_height))
    )

    events = pygame.event.get()
    
    if not is_dead and current_state not in ["MENU", "PAUSE"] and (hunger <= 0 or thirst <= 0):
        is_dead = True
        death_timer = pygame.time.get_ticks()
        current_state = "DEATH"

    if is_dead:
        virtual_screen.fill((20, 5, 5))
        msg_game_over = font_huge.render("GAME OVER", True, DANGER)
        msg_sub = font_title.render("Zmarłeś z głodu lub pragnienia!", True, WHITE)
        msg_restart = font_main.render("Powrót do menu...", True, GOLD)
        
        virtual_screen.blit(msg_game_over, (VIRTUAL_WIDTH//2 - msg_game_over.get_width()//2, VIRTUAL_HEIGHT//2 - 100))
        virtual_screen.blit(msg_sub, (VIRTUAL_WIDTH//2 - msg_sub.get_width()//2, VIRTUAL_HEIGHT//2))
        virtual_screen.blit(msg_restart, (VIRTUAL_WIDTH//2 - msg_restart.get_width()//2, VIRTUAL_HEIGHT//2 + 70))
        
        if pygame.time.get_ticks() - death_timer > 3000:
            current_state = "MENU"
            is_dead = False
            
        scaled_surface = pygame.transform.scale(virtual_screen, (window_width, window_height))
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)
        continue

    for event in events:
        if event.type == pygame.QUIT: 
            running = False
            
        if event.type == pygame.VIDEORESIZE:
            window_width, window_height = event.w, event.h
            screen = pygame.display.set_mode((window_width, window_height), pygame.RESIZABLE)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if current_state == "GAME":
                current_state = "PAUSE"
            elif current_state == "PAUSE":
                current_state = "GAME"
            elif current_state in ["SHOP", "SELL", "CASINO", "INVENTORY"]:
                current_state = "GAME"

        if current_state not in ["MENU", "PAUSE"] and event.type == pygame.KEYDOWN and event.key == pygame.K_i:
            if current_state == "INVENTORY": current_state = "GAME"
            else: current_state = "INVENTORY"

        if current_state not in ["MENU", "PAUSE"] and event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            if current_state == "SHOP": 
                current_state = "GAME"
            elif current_state == "GAME":
                if is_on_surface(): current_state = "SHOP"
                else: surface_alert_timer = 120

        if current_state == "CASINO" and casino_input_active and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                casino_bet_input_text = casino_bet_input_text[:-1]
            elif event.unicode.isdigit(): 
                if len(casino_bet_input_text) < 9:
                    casino_bet_input_text += event.unicode
            try: casino_bet = int(casino_bet_input_text) if casino_bet_input_text != "" else 0
            except ValueError: casino_bet = 0

    if current_state == "GAME":
        hunger = max(0.0, hunger - HUNGER_DECAY)
        thirst = max(0.0, thirst - THIRST_DECAY)

    if current_state == "MENU":
        for event in events:
            if not transition_active:
                if btn_menu_start.clicked(event, virtual_mouse_pos):
                    reset_game()
                    start_transition("GAME")
                elif btn_menu_load.clicked(event, virtual_mouse_pos, disabled=not os.path.exists(SAVE_FILE)):
                    if load_game(): start_transition("GAME")
                elif btn_menu_exit.clicked(event, virtual_mouse_pos):
                    start_transition("EXIT")
                    
        draw_menu(virtual_screen, virtual_mouse_pos)

    elif current_state == "PAUSE":
        for event in events:
            if btn_pause_resume.clicked(event, virtual_mouse_pos):
                current_state = "GAME"
            elif btn_pause_save_exit.clicked(event, virtual_mouse_pos):
                save_game()
                start_transition("MENU")
            elif btn_pause_exit.clicked(event, virtual_mouse_pos):
                start_transition("MENU")

        draw_pause_menu(virtual_screen, virtual_mouse_pos)

    elif current_state in ["SHOP", "SELL", "CASINO", "INVENTORY"]:
        for event in events:
            if btn_close_ui.clicked(event, virtual_mouse_pos):
                current_state = "GAME"
                casino_input_active = False

            if current_state == "SHOP":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if pygame.Rect(30, 110, 210, 40).collidepoint(virtual_mouse_pos): current_tab = "ENCHANTY"
                    if pygame.Rect(260, 110, 210, 40).collidepoint(virtual_mouse_pos): current_tab = "ŻYWNOŚĆ I PALIWO"
                    if pygame.Rect(490, 110, 210, 40).collidepoint(virtual_mouse_pos): current_tab = "SEKTOR W BUDOWIE"
                        
                    if current_tab == "ENCHANTY":
                        for i, item in enumerate(shop_items["ENCHANTY"]):
                            buy_rect = pygame.Rect(720, 170 + (i * 120) + 25, 120, 50)
                            if buy_rect.collidepoint(virtual_mouse_pos):
                                if wallet >= item["price"] and item["name"] not in upgrades_inventory:
                                    wallet -= item["price"]
                                    upgrades_inventory.append(item["name"])
                    
                    elif current_tab == "ŻYWNOŚĆ I PALIWO":
                        for i, item in enumerate(shop_items["ŻYWNOŚĆ I PALIWO"]):
                            buy_rect = pygame.Rect(720, 170 + (i * 120) + 25, 120, 50)
                            if buy_rect.collidepoint(virtual_mouse_pos):
                                if wallet >= item["price"]:
                                    wallet -= item["price"]
                                    player_inventory[item["id"]] += 1

            elif current_state == "SELL":
                total_pages = math.ceil(len(ores) / 6)
                if btn_sell_all.clicked(event, virtual_mouse_pos):
                    for name in ores:
                        wallet += ores[name]["qty"] * ores[name]["price"]
                        ores[name]["qty"] = 0
                if sell_page > 0 and btn_prev_page.clicked(event, virtual_mouse_pos): sell_page -= 1
                if sell_page < total_pages - 1 and btn_next_page.clicked(event, virtual_mouse_pos): sell_page += 1

                if event.type == pygame.MOUSEBUTTONDOWN:
                    for name, data, card, s_btn in get_sell_cards():
                        if s_btn.collidepoint(virtual_mouse_pos) and data["qty"] > 0:
                            wallet += data["price"]
                            data["qty"] -= 1

            elif current_state == "CASINO":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if casino_input_rect.collidepoint(virtual_mouse_pos): casino_input_active = True
                    else: casino_input_active = False

                if not roulette_spinning:
                    if btn_bet_red.clicked(event, virtual_mouse_pos): casino_chosen_color = "RED"
                    if btn_bet_black.clicked(event, virtual_mouse_pos): casino_chosen_color = "BLACK"
                    if btn_bet_green.clicked(event, virtual_mouse_pos): casino_chosen_color = "GREEN"

                    if btn_bet_minus.clicked(event, virtual_mouse_pos):
                        casino_bet = max(0, casino_bet - 100)
                        casino_bet_input_text = str(casino_bet)
                    if btn_bet_plus.clicked(event, virtual_mouse_pos):
                        casino_bet += 100
                        casino_bet_input_text = str(casino_bet)
                    if btn_bet_all_in.clicked(event, virtual_mouse_pos):
                        casino_bet = max(0, wallet)
                        casino_bet_input_text = str(casino_bet)

                    if btn_spin.clicked(event, virtual_mouse_pos):
                        try: casino_bet = int(casino_bet_input_text)
                        except: casino_bet = 0
                        if wallet >= casino_bet and casino_bet > 0:
                            wallet -= casino_bet
                            roulette_spinning = True
                            roulette_timer = 50  
                            casino_message = ""
                            casino_input_active = False
                        else:
                            casino_message = "NIEPRAWIDŁOWA STAWKA LUB BRAK KREDYTÓW!"
                            casino_message_color = DANGER
                            
            elif current_state == "INVENTORY":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for i, (item_id, qty) in enumerate(player_inventory.items()):
                        y_pos = 180 + (i * 105)
                        use_btn = pygame.Rect(680, y_pos + 20, 140, 50)
                        if use_btn.collidepoint(virtual_mouse_pos) and qty > 0:
                            player_inventory[item_id] -= 1
                            info = items_data[item_id]
                            if info["restore_type"] == "hunger":
                                hunger = min(100.0, hunger + info["amount"])
                            elif info["restore_type"] == "thirst":
                                thirst = min(100.0, thirst + info["amount"])
                            elif info["restore_type"] == "fuel":
                                fuel = min(100.0, fuel + info["amount"])

        if current_state == "SHOP": draw_shop(virtual_screen, virtual_mouse_pos)
        elif current_state == "SELL": draw_sell(virtual_screen, virtual_mouse_pos)
        elif current_state == "CASINO": draw_casino(virtual_screen, virtual_mouse_pos)
        elif current_state == "INVENTORY": draw_inventory(virtual_screen, virtual_mouse_pos)

    elif current_state == "GAME":
        cam_x = player_x - (VIRTUAL_WIDTH // 2) + (PLAYER_WIDTH // 2)
        cam_y = player_y - (VIRTUAL_HEIGHT // 2) + (PLAYER_HEIGHT // 2) - 50

        trading_disabled = not is_on_surface()

        for event in events:
            if btn_open_shop.clicked(event, virtual_mouse_pos, disabled=trading_disabled): current_state = "SHOP"
            if btn_open_sell.clicked(event, virtual_mouse_pos, disabled=trading_disabled): current_state = "SELL"
            if btn_open_casino.clicked(event, virtual_mouse_pos, disabled=trading_disabled): current_state = "CASINO"
            if btn_open_inv.clicked(event, virtual_mouse_pos): current_state = "INVENTORY"
            
            if btn_go_lobby.clicked(event, virtual_mouse_pos): start_transition("MENU")
            if btn_save_game.clicked(event, virtual_mouse_pos):
                if save_game(): save_alert_timer = 90  

            if trading_disabled and event.type == pygame.MOUSEBUTTONDOWN:
                if btn_open_shop.rect.collidepoint(virtual_mouse_pos) or btn_open_sell.rect.collidepoint(virtual_mouse_pos) or btn_open_casino.rect.collidepoint(virtual_mouse_pos):
                    surface_alert_timer = 120

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                world_mouse_x = virtual_mouse_pos[0] + cam_x
                world_mouse_y = virtual_mouse_pos[1] + cam_y
                tile_click_x = int(world_mouse_x // TILE_SIZE)
                tile_click_y = int((world_mouse_y - FLOOR_Y) // TILE_SIZE)
                
                p_tile_x = int((player_x + PLAYER_WIDTH // 2) // TILE_SIZE)
                p_tile_y = int((player_y + PLAYER_HEIGHT // 2 - FLOOR_Y) // TILE_SIZE)
                
                if abs(tile_click_x - p_tile_x) <= 2 and abs(tile_click_y - p_tile_y) <= 2:
                    if tile_click_y >= 0:
                        tile_content = get_tile_at(tile_click_x, tile_click_y)
                        if tile_content != 'air':
                            mining_animation_timer = MINING_DURATION
                            if (tile_click_x, tile_click_y) not in block_durability:
                                block_durability[(tile_click_x, tile_click_y)] = get_block_max_hp(tile_click_y)
                            
                            block_durability[(tile_click_x, tile_click_y)] -= get_mining_power()
                            if block_durability[(tile_click_x, tile_click_y)] <= 0:
                                if tile_content in ores: ores[tile_content]["qty"] += 1  
                                world_map[(tile_click_x, tile_click_y)] = 'air'

        keys = pygame.key.get_pressed()
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -speed
            current_img = player_img_left
            facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = speed
            current_img = player_img_right
            facing_right = True

        if (keys[pygame.K_SPACE] or keys[pygame.K_w]) and fuel > 0:
            is_using_jetpack = True
            vel_y += JETPACK_THRUST
            fuel = max(0.0, fuel - FUEL_CONSUMPTION)
        else:
            is_using_jetpack = False

        player_x += dx
        player_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
        for rect in get_collidable_rects(player_x, player_y):
            if player_rect.colliderect(rect):
                if dx > 0: player_x = rect.left - PLAYER_WIDTH
                if dx < 0: player_x = rect.right
                player_rect.x = player_x

        vel_y += GRAVITY
        if vel_y > TERMINAL_VELOCITY: vel_y = TERMINAL_VELOCITY
        player_y += vel_y
        player_rect = pygame.Rect(player_x, player_y, PLAYER_WIDTH, PLAYER_HEIGHT)
        for rect in get_collidable_rects(player_x, player_y):
            if player_rect.colliderect(rect):
                if vel_y > 0:
                    player_y = rect.top - PLAYER_HEIGHT
                    vel_y = 0
                elif vel_y < 0:
                    player_y = rect.bottom
                    vel_y = 0
                player_rect.y = player_y

        virtual_screen.fill((5, 5, 15)) 

        for star in stars:
            star_x = (star[0] - cam_x * star[3]) % VIRTUAL_WIDTH
            star_y = (star[1] - cam_y * star[3] * 0.5) % VIRTUAL_HEIGHT
            pygame.draw.circle(virtual_screen, (200, 200, 255) if star[2] > 1 else (100, 100, 150), (int(star_x), int(star_y)), star[2])

        virtual_screen.blit(planet_img, (math.floor(-cam_x * 0.2) + (VIRTUAL_WIDTH // 2 - 70), math.floor(-cam_y * 0.1) + 80))
        
        for ast in bg_asteroids:
            ast_screen_x = ast['wx'] - cam_x * ast['factor']
            ast_screen_y = ast['wy'] - cam_y * ast['factor']
            if -64 < ast_screen_x < VIRTUAL_WIDTH + 64 and -64 < ast_screen_y < VIRTUAL_HEIGHT + 64:
                virtual_screen.blit(ast['texture'], (int(ast_screen_x), int(ast_screen_y)))

        start_tile_x = int(cam_x // TILE_SIZE)
        end_tile_x = start_tile_x + (VIRTUAL_WIDTH // TILE_SIZE) + 2
        start_tile_y = max(0, int((cam_y - FLOOR_Y) // TILE_SIZE))
        end_tile_y = start_tile_y + (VIRTUAL_HEIGHT // TILE_SIZE) + 2
        
        for ty in range(start_tile_y, end_tile_y):
            for tx in range(start_tile_x, end_tile_x):
                tile_type = get_tile_at(tx, ty)
                if tile_type != 'air' and tile_type in TILES:
                    draw_x = tx * TILE_SIZE - cam_x
                    draw_y = FLOOR_Y + (ty * TILE_SIZE) - cam_y
                    virtual_screen.blit(TILES[tile_type], (draw_x, draw_y))
                    if (tx, ty) in block_durability:
                        max_hp = get_block_max_hp(ty)
                        current_hp = block_durability[(tx, ty)]
                        if current_hp < max_hp:
                            pygame.draw.line(virtual_screen, (255, 0, 0), (draw_x + 10, draw_y + 10), (draw_x + TILE_SIZE - 10, draw_y + TILE_SIZE - 10), 2)

        player_screen_x = player_x - cam_x
        player_screen_y = player_y - cam_y
        virtual_screen.blit(current_img, (player_screen_x - 5, player_screen_y - 5))

        if is_using_jetpack:
            fire_offset_y = random.randint(22, 26)
            virtual_screen.blit(jetpack_fire_img, (player_screen_x - 8 if facing_right else player_screen_x + PLAYER_WIDTH - 4, player_screen_y + fire_offset_y))

        if mining_animation_timer > 0:
            angle = (mining_animation_timer / MINING_DURATION) * 70
            mining_animation_timer -= 1
        else: angle = 0

        if facing_right:
            rotated_pickaxe = pygame.transform.rotate(pickaxe_img, -angle)
            virtual_screen.blit(rotated_pickaxe, (player_screen_x + 32, player_screen_y + 15))
        else:
            flipped_pick = pygame.transform.flip(pickaxe_img, True, False)
            rotated_pickaxe = pygame.transform.rotate(flipped_pick, angle)
            virtual_screen.blit(rotated_pickaxe, (player_screen_x - 15, player_screen_y + 15))

        pygame.draw.rect(virtual_screen, PANEL_DARK, (0, 0, VIRTUAL_WIDTH, 65))
        pygame.draw.line(virtual_screen, CYAN, (0, 65), (VIRTUAL_WIDTH, 65), 2)
        
        btn_open_shop.draw(virtual_screen, virtual_mouse_pos, disabled=trading_disabled)
        btn_open_sell.draw(virtual_screen, virtual_mouse_pos, disabled=trading_disabled)
        btn_open_casino.draw(virtual_screen, virtual_mouse_pos, disabled=trading_disabled)
        btn_open_inv.draw(virtual_screen, virtual_mouse_pos)
        btn_save_game.draw(virtual_screen, virtual_mouse_pos)
        btn_go_lobby.draw(virtual_screen, virtual_mouse_pos)
        
        draw_status_bars(virtual_screen, 745, 2)
        wallet_text = font_small.render(f"{wallet}$", True, GOLD)
        virtual_screen.blit(wallet_text, (465, 5))

        if save_alert_timer > 0:
            save_alert_timer -= 1
            s_txt = font_main.render("GRA ZOSTALA ZAPISANA SUKCESEM!", True, SUCCESS)
            pygame.draw.rect(virtual_screen, (10, 40, 20), (VIRTUAL_WIDTH//2 - s_txt.get_width()//2 - 10, 75, s_txt.get_width() + 20, 30), border_radius=5)
            virtual_screen.blit(s_txt, (VIRTUAL_WIDTH//2 - s_txt.get_width()//2, 80))

        if surface_alert_timer > 0:
            surface_alert_timer -= 1
            alert_txt = font_main.render("Menedżer handlu dostępny tylko na powierzchni!", True, DANGER)
            pygame.draw.rect(virtual_screen, (40, 10, 10), (VIRTUAL_WIDTH//2 - alert_txt.get_width()//2 - 10, 75, alert_txt.get_width() + 20, 30), border_radius=5)
            virtual_screen.blit(alert_txt, (VIRTUAL_WIDTH//2 - alert_txt.get_width()//2, 80))

        active_items = [f"{data['label']}: {data['qty']}" for data in ores.values() if data['qty'] > 0]
        ui_height = 35 + (len(active_items) * 20) if active_items else 40
        pygame.draw.rect(virtual_screen, (20, 20, 30), (15, 80, 180, ui_height), border_radius=8)
        pygame.draw.rect(virtual_screen, (100, 100, 150), (15, 80, 180, ui_height), 2, border_radius=8)
        virtual_screen.blit(font_small.render("MAGAZYN RUD:", True, WHITE), (25, 87))
        if not active_items:
            virtual_screen.blit(font_small.render("Pusto...", True, (150, 150, 150)), (25, 110))
        else:
            for index, item_string in enumerate(active_items):
                virtual_screen.blit(font_small.render(item_string, True, SUCCESS), (25, 113 + (index * 20)))

        altitude = max(0, int(-player_y // 10))
        if altitude > 0:
            virtual_screen.blit(font_main.render(f"Wysokość: {altitude}m", True, (240, 180, 50)), (15, VIRTUAL_HEIGHT - 30))
        else:
            virtual_screen.blit(font_main.render("Powierzchnia bazy", True, SUCCESS), (15, VIRTUAL_HEIGHT - 30))

    if transition_active:
        transition_alpha += 7
        if transition_alpha >= 255:
            transition_alpha = 255
            transition_active = False
            if transition_target_state == "EXIT": running = False
            else: current_state = transition_target_state
        
        transition_overlay.fill((0, 0, 0, transition_alpha))
        virtual_screen.blit(transition_overlay, (0, 0))

    scaled_surface = pygame.transform.scale(virtual_screen, (window_width, window_height))
    screen.blit(scaled_surface, (0, 0))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
