import pygame
import sys
import math
import random

pygame.init()
pygame.font.init()

WIDTH, HEIGHT = 900, 850  
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("GALAXY Mine & Shop")

clock = pygame.time.Clock()

BG_DEEP = (3, 3, 12)
PANEL_DARK = (15, 15, 30)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
GOLD = (255, 215, 0)
WHITE = (230, 230, 250)
SUCCESS = (0, 255, 150)
DANGER = (255, 50, 80)

def get_font(size, bold=False):
    return pygame.font.SysFont("DejaVu Sans, Liberation Sans, Arial", size, bold=bold)

font_huge = get_font(52, True)
font_title = get_font(30, True)
font_main = get_font(18, True)
font_small = get_font(14)

wallet = 0
inventory = [] 

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

shop_items = {
    "ENCHANTY": [
        {"name": "Efficiency I", "price": 100, "desc": "Szybkość kopania I (+1 dmg)", "power": 1},
        {"name": "Efficiency II", "price": 500, "desc": "Szybkość kopania II (+2 dmg)", "power": 2},
        {"name": "Efficiency III", "price": 2500, "desc": "Szybkość kopania III (+3 dmg)", "power": 3},
        {"name": "Efficiency IV", "price": 10000, "desc": "Szybkość kopania IV (+4 dmg)", "power": 4},
        {"name": "Efficiency V", "price": 50000, "desc": "Szybkość kopania V (+5 dmg)", "power": 5},
    ],
    "W BUDOWIE": []
}

current_state = "GAME"
current_tab = "ENCHANTY"

class Button:
    def __init__(self, text, x, y, w, h, color, accent, border=2):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.accent = accent
        self.border = border

    def draw(self, surface):
        mouse = pygame.mouse.get_pos()
        hover = self.rect.collidepoint(mouse)
        
        if hover:
            pygame.draw.rect(surface, self.accent, self.rect.inflate(6, 6), 1, border_radius=10)
        
        pygame.draw.rect(surface, self.color if not hover else [min(255, c+20) for c in self.color], self.rect, border_radius=8)
        pygame.draw.rect(surface, self.accent, self.rect, self.border, border_radius=8)
        
        txt = font_main.render(self.text, True, WHITE)
        surface.blit(txt, (self.rect.centerx - txt.get_width()//2, self.rect.centery - txt.get_height()//2))

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

btn_open_shop = Button("SKLEP (E)", 15, 15, 120, 35, PANEL_DARK, CYAN)
btn_open_sell = Button("SPRZEDAŻ", 145, 15, 120, 35, PANEL_DARK, SUCCESS)
btn_close_ui = Button("POWRÓT DO GRY", WIDTH - 190, 15, 175, 35, (40, 40, 50), CYAN)
btn_sell_all = Button("SPRZEDAJ WSZYSTKO", WIDTH - 430, 15, 220, 35, DANGER, WHITE)

TILE_SIZE = 64
PLAYER_WIDTH, PLAYER_HEIGHT = 54, 54

def create_dummy_surface(w, h, color):
    s = pygame.Surface((w, h), pygame.SRCALPHA)
    s.fill(color)
    return s

try:
    planet_img = pygame.image.load("image.png").convert_alpha()
except:
    planet_img = create_dummy_surface(200, 200, (100, 50, 150))

try:
    player_img_right = pygame.image.load("image_prawo.png").convert_alpha()
    player_img_right = pygame.transform.scale(player_img_right, (TILE_SIZE, TILE_SIZE))
except:
    player_img_right = create_dummy_surface(TILE_SIZE, TILE_SIZE, (0, 200, 255))

player_img_left = pygame.transform.flip(player_img_right, True, False)

try:
    ore_overlay_img = pygame.image.load("pixil-frame-0_13.png").convert_alpha()
    ore_overlay_img = pygame.transform.scale(ore_overlay_img, (TILE_SIZE, TILE_SIZE))
except:
    ore_overlay_img = create_dummy_surface(TILE_SIZE, TILE_SIZE, (255, 255, 0))

pickaxe_img = create_dummy_surface(32, 32, GOLD)
pygame.draw.rect(pickaxe_img, (150, 75, 0), (0, 20, 32, 8)) 
jetpack_fire_img = create_dummy_surface(16, 24, (255, 100, 0))

TILES = {}
stone_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
stone_img.fill((40, 40, 45))
pygame.draw.rect(stone_img, (60, 60, 70), (0, 0, TILE_SIZE, TILE_SIZE), 1)
TILES['stone'] = stone_img

for ore in ores.keys():
    ore_tile = stone_img.copy()
    ore_tile.blit(ore_overlay_img, (0, 0))
    TILES[ore] = ore_tile

def create_asteroid_texture(size, seed_val):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    rand = random.Random(seed_val)
    color_base = rand.randint(70, 95)
    pygame.draw.circle(surf, (color_base, color_base, color_base), (size//2, size//2), size//2)
    return surf

bg_asteroids = []
for i in range(40):
    size = random.randint(24, 64)
    bg_asteroids.append({
        'texture': create_asteroid_texture(size, f"ast_{i}"),
        'wx': random.randint(-1500, 2500),
        'wy': random.randint(-6000, -400), 
        'factor': random.uniform(0.08, 0.18)
    })

stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3), random.uniform(0.02, 0.1)] for _ in range(150)]


player_x, player_y = 100, 200 - PLAYER_HEIGHT
speed = 5
FLOOR_Y = 260 
current_img = player_img_right
facing_right = True

world_map = {}       
block_durability = {} 
mining_animation_timer = 0
MINING_DURATION = 8 

vel_y = 0
GRAVITY = 0.5
TERMINAL_VELOCITY = 10
JETPACK_THRUST = -0.9 
is_using_jetpack = False


def get_mining_power():
    """Zwraca siłę kopania gracza na podstawie zakupionych enchantów."""
    power = 1
    for item in shop_items["ENCHANTY"]:
        if item["name"] in inventory:
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
    card_height, card_spacing = 90, 20
    cols = 2
    card_width = (WIDTH - padding_x * 2 - 20) // cols
    btn_w = 140
    for idx, (name, data) in enumerate(ores.items()):
        row, col = idx // cols, idx % cols
        x = padding_x + col * (card_width + 20)
        y = padding_y + row * (card_height + card_spacing)
        card = pygame.Rect(x, y, card_width, card_height)
        button = pygame.Rect(card.right - btn_w - 20, y + 20, btn_w, 50)
        cards.append((name, data, card, button))
    return cards


def draw_stars():
    screen.fill(BG_DEEP)
    for star in stars:
        pygame.draw.circle(screen, (200, 200, 255), (star[0], star[1]), star[2])

def draw_header():
    pygame.draw.rect(screen, (10, 10, 25), (0, 0, WIDTH, 90))
    pygame.draw.line(screen, CYAN, (0, 90), (WIDTH, 90), 2)
    w_txt = font_title.render(f"CREDITS: {wallet}$", True, GOLD)
    screen.blit(w_txt, (30, 25))
    btn_close_ui.draw(screen)

def draw_shop():
    draw_stars()
    draw_header()
    
    tabs = ["ENCHANTY", "W BUDOWIE"] 
    for i, t in enumerate(tabs):
        t_rect = pygame.Rect(30 + i*180, 110, 160, 40)
        active = current_tab == t
        pygame.draw.rect(screen, CYAN if active else PANEL_DARK, t_rect, border_radius=5)
        txt = font_main.render(t, True, BG_DEEP if active else WHITE)
        screen.blit(txt, (t_rect.centerx - txt.get_width()//2, t_rect.centery - txt.get_height()//2))

    if current_tab == "W BUDOWIE":
        info_rect = pygame.Rect(150, 250, WIDTH - 300, 300)
        pygame.draw.rect(screen, PANEL_DARK, info_rect, border_radius=20)
        text_title = font_title.render("SEKTOR W BUDOWIE", True, MAGENTA)
        screen.blit(text_title, (info_rect.centerx - text_title.get_width()//2, info_rect.y + 50))
    else:
        for i, item in enumerate(shop_items[current_tab]):
            y_pos = 170 + (i * 120)
            card = pygame.Rect(30, y_pos, 840, 100)
            pygame.draw.rect(screen, PANEL_DARK, card, border_radius=12)
            pygame.draw.rect(screen, CYAN, card, 1, border_radius=12)
            
            screen.blit(font_main.render(item["name"], True, WHITE), (50, y_pos + 20))
            screen.blit(font_small.render(item["desc"], True, (160, 160, 180)), (50, y_pos + 55))
            
            price_txt = font_main.render(f"{item['price']}$", True, GOLD)
            screen.blit(price_txt, (600, y_pos + 35))
            
            owned = item["name"] in inventory
            buy_rect = pygame.Rect(720, y_pos + 25, 120, 50)
            pygame.draw.rect(screen, SUCCESS if wallet >= item["price"] and not owned else (60,60,60), buy_rect, border_radius=8)
            b_label = "POSIADASZ" if owned else "KUPUJ"
            bt = font_main.render(b_label, True, WHITE)
            screen.blit(bt, (buy_rect.centerx - bt.get_width()//2, buy_rect.centery - bt.get_height()//2))

def draw_sell():
    draw_stars()
    draw_header()
    btn_sell_all.draw(screen)
    
    for name, data, card, s_btn in get_sell_cards():
        pygame.draw.rect(screen, PANEL_DARK, card, border_radius=15)
        screen.blit(font_main.render(f"{data['label']}", True, WHITE), (card.x + 30, card.y + 20))
        screen.blit(font_small.render(f"ILOSC: {data['qty']} (Cena: {data['price']}$)", True, CYAN), (card.x + 30, card.y + 50))
        pygame.draw.rect(screen, SUCCESS if data['qty'] > 0 else (60,60,60), s_btn, border_radius=8)
        label = font_main.render("SPRZEDAJ 1", True, WHITE)
        screen.blit(label, (s_btn.centerx - label.get_width()//2, s_btn.centery - label.get_height()//2))


running = True
while running:
    events = pygame.event.get()
    
    

    if current_state in ["SHOP", "SELL"]:
        for event in events:
            if event.type == pygame.QUIT: running = False
            
            if btn_close_ui.clicked(event) or (event.type == pygame.KEYDOWN and event.key == pygame.K_e):
                current_state = "GAME"

                
            if current_state == "SHOP":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    tabs = ["ENCHANTY", "W BUDOWIE"]
                    for i, t in enumerate(tabs):
                        if pygame.Rect(30 + i*180, 110, 160, 40).collidepoint(event.pos):
                            current_tab = t
                            
                    if current_tab in shop_items:
                        for i, item in enumerate(shop_items[current_tab]):
                            buy_rect = pygame.Rect(720, 170 + (i * 120) + 25, 120, 50)
                            if buy_rect.collidepoint(event.pos):
                                if wallet >= item["price"] and item["name"] not in inventory:
                                    wallet -= item["price"]
                                    inventory.append(item["name"])
                                    
            elif current_state == "SELL":
                if btn_sell_all.clicked(event):
                    for name in ores:
                        wallet += ores[name]["qty"] * ores[name]["price"]
                        ores[name]["qty"] = 0
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for name, data, card, s_btn in get_sell_cards():
                        if s_btn.collidepoint(event.pos) and data["qty"] > 0:
                            wallet += data["price"]
                            data["qty"] -= 1


        if current_state == "SHOP": draw_shop()
        elif current_state == "SELL": draw_sell()


    else:
        cam_x = player_x - (WIDTH // 2) + (PLAYER_WIDTH // 2)
        cam_y = player_y - (HEIGHT // 2) + (PLAYER_HEIGHT // 2) - 50

        for event in events:
            if event.type == pygame.QUIT: running = False
            
            if btn_open_shop.clicked(event) or (event.type == pygame.KEYDOWN and event.key == pygame.K_e):
                current_state = "SHOP"
            if btn_open_sell.clicked(event):
                current_state = "SELL"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                world_mouse_x = event.pos[0] + cam_x
                world_mouse_y = event.pos[1] + cam_y
                
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
                                if tile_content in ores:
                                    ores[tile_content]["qty"] += 1  
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

        if keys[pygame.K_SPACE] or keys[pygame.K_w]:
            is_using_jetpack = True
            vel_y += JETPACK_THRUST
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

       
        screen.fill((5, 5, 15)) 

    
        for star in stars:
            star_x = (star[0] - cam_x * star[3]) % WIDTH
            star_y = (star[1] - cam_y * star[3] * 0.5) % HEIGHT
            pygame.draw.circle(screen, (200, 200, 255) if star[2] > 1 else (100, 100, 150), (int(star_x), int(star_y)), star[2])

        screen.blit(planet_img, (math.floor(-cam_x * 0.2) + (WIDTH // 2 - 100), math.floor(-cam_y * 0.1) + 80))
        
       
        for ast in bg_asteroids:
            ast_screen_x = ast['wx'] - cam_x * ast['factor']
            ast_screen_y = ast['wy'] - cam_y * ast['factor']
            if -64 < ast_screen_x < WIDTH + 64 and -64 < ast_screen_y < HEIGHT + 64:
                screen.blit(ast['texture'], (int(ast_screen_x), int(ast_screen_y)))

        
        start_tile_x = int(cam_x // TILE_SIZE)
        end_tile_x = start_tile_x + (WIDTH // TILE_SIZE) + 2
        start_tile_y = max(0, int((cam_y - FLOOR_Y) // TILE_SIZE))
        end_tile_y = start_tile_y + (HEIGHT // TILE_SIZE) + 2
        
        for ty in range(start_tile_y, end_tile_y):
            for tx in range(start_tile_x, end_tile_x):
                tile_type = get_tile_at(tx, ty)
                if tile_type != 'air':
                    draw_x = tx * TILE_SIZE - cam_x
                    draw_y = FLOOR_Y + (ty * TILE_SIZE) - cam_y
                    screen.blit(TILES[tile_type], (draw_x, draw_y))
                    
                    if (tx, ty) in block_durability:
                        max_hp = get_block_max_hp(ty)
                        current_hp = block_durability[(tx, ty)]
                        if current_hp < max_hp:
                            pygame.draw.line(screen, (255, 0, 0), (draw_x + 10, draw_y + 10), (draw_x + TILE_SIZE - 10, draw_y + TILE_SIZE - 10), 2)

     
        player_screen_x = player_x - cam_x
        player_screen_y = player_y - cam_y
        screen.blit(current_img, (player_screen_x - 5, player_screen_y - 5))

        if is_using_jetpack:
            fire_offset_y = random.randint(22, 26)
            screen.blit(jetpack_fire_img, (player_screen_x - 8 if facing_right else player_screen_x + PLAYER_WIDTH - 4, player_screen_y + fire_offset_y))

      
        if mining_animation_timer > 0:
            angle = (mining_animation_timer / MINING_DURATION) * 70
            mining_animation_timer -= 1
        else: angle = 0

        if facing_right:
            rotated_pickaxe = pygame.transform.rotate(pickaxe_img, -angle)
            screen.blit(rotated_pickaxe, (player_screen_x + 32, player_screen_y + 15))
        else:
            flipped_pick = pygame.transform.flip(pickaxe_img, True, False)
            rotated_pickaxe = pygame.transform.rotate(flipped_pick, angle)
            screen.blit(rotated_pickaxe, (player_screen_x - 15, player_screen_y + 15))

      
        pygame.draw.rect(screen, PANEL_DARK, (0, 0, WIDTH, 65))
        pygame.draw.line(screen, CYAN, (0, 65), (WIDTH, 65), 2)
        
        btn_open_shop.draw(screen)
        btn_open_sell.draw(screen)
        
        wallet_text = font_main.render(f"KREDYTY: {wallet}$", True, GOLD)
        screen.blit(wallet_text, (290, 22))
        
       
        power_text = font_small.render(f"Moc kilofa: Wzmocnienie +{get_mining_power()-1}", True, CYAN)
        screen.blit(power_text, (480, 25))

      
        active_items = [f"{data['label']}: {data['qty']}" for data in ores.values() if data['qty'] > 0]
        ui_height = 35 + (len(active_items) * 20) if active_items else 40
        
        pygame.draw.rect(screen, (20, 20, 30), (15, 80, 200, ui_height), border_radius=8)
        pygame.draw.rect(screen, (100, 100, 150), (15, 80, 200, ui_height), 2, border_radius=8)
        
        screen.blit(get_font(18, True).render("EKWIPUNEK:", True, WHITE), (25, 87))
        if not active_items:
            screen.blit(font_small.render("Pusto...", True, (150, 150, 150)), (25, 110))
        else:
            for index, item_string in enumerate(active_items):
                screen.blit(font_small.render(item_string, True, SUCCESS), (25, 113 + (index * 20)))

       
        altitude = max(0, int(-player_y // 10))
        if altitude > 0:
            screen.blit(font_main.render(f"Wysokość: {altitude}m", True, (240, 180, 50)), (15, HEIGHT - 30))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()