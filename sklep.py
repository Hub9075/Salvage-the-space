import pygame
import random


pygame.init()

WIDTH, HEIGHT = 900, 850
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("GALAXY Shop")
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
    "Coal": {"qty": 0, "price": 10},
    "Iron": {"qty": 0, "price": 25},
    "Quartz": {"qty": 0, "price": 40},
    "lapiz": {"qty": 0, "price": 60},
    "Gold": {"qty": 0, "price": 100},
    "Emerald": {"qty": 0, "price": 150},
    "Rubin": {"qty": 0, "price": 200},
    "Sapphire": {"qty": 0, "price": 250},
    "Diament": {"qty": 0, "price": 500},
    "Uran": {"qty": 0, "price": 1000},
    "Alien_ore": {"qty": 0, "price": 5000},
}

shop_items = {
    "ENCHANTY": [
        {"name": "Efficency", "price": 50000, "desc": "Szybkość kopania I"},
        {"name": "Efficency II", "price": 250000, "desc": "Szybkość kopania II"},
        {"name": "Efficency III", "price": 750000, "desc": "Szybkość kopania III"},
        {"name": "Efficency IV", "price": 100000, "desc": "Szybkość kopania IV"},
        {"name": "Efficency V", "price": 7500000, "desc": "Szybkość kopania V"},
        {"name": "Fortuna ", "price": 50000, "desc": "Szczęscie I"},
        {"name": "Fortuna II", "price": 120000, "desc": "Szczęscie II"},
        {"name": "Fortuna III", "price": 2000000, "desc": "Szczęscie III"},
    ],
    "W BUDOWIE": []
}


current_state = "SPLASH"
current_tab = "ENCHANTY" 
loading_val = 0
active_input = False
casino_bet = "100"
casino_msg = "OBSTAW I URUCHOM"
casino_res = ["---", "---", "---"]
casino_mode = "SLOTS"
casino_choice = None

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

btn_to_shop = Button("SKLEP GALAKTYCZNY", 300, 320, 300, 60, PANEL_DARK, CYAN)
btn_to_sell = Button("SPRZEDAŻ SUROWCOW", 300, 400, 300, 60, PANEL_DARK, SUCCESS)
btn_to_casino = Button("KASYNO NEBULA", 300, 480, 300, 60, PANEL_DARK, MAGENTA)
btn_back = Button("POWRÓT", 700, 25, 170, 40, (40, 40, 50), CYAN)
btn_sell_all = Button("SPRZEDAJ WSZYSTKO", 450, 25, 220, 40, DANGER, WHITE)

def draw_stars():
    screen.fill(BG_DEEP)
    for _ in range(60):
        x, y = random.randint(0, WIDTH), random.randint(0, HEIGHT)
        pygame.draw.circle(screen, (200, 200, 255), (x, y), random.randint(1, 2))

def splash_screen():
    global loading_val, current_state
    draw_stars()
    title = font_huge.render("GALAXY Shop", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 300))
    
    pygame.draw.rect(screen, PANEL_DARK, (250, 450, 400, 20), border_radius=10)
    pygame.draw.rect(screen, CYAN, (250, 450, loading_val * 4, 20), border_radius=10)
    
    loading_val += 1.5
    if loading_val >= 100:
        current_state = "MENU"

def draw_header():
    pygame.draw.rect(screen, (10, 10, 25), (0, 0, WIDTH, 90))
    pygame.draw.line(screen, CYAN, (0, 90), (WIDTH, 90), 2)
    w_txt = font_title.render(f"CREDITS: {wallet}$", True, GOLD)
    screen.blit(w_txt, (30, 25))
    
    btn_back.rect = pygame.Rect(WIDTH - 200, 25, 170, 40)
    btn_back.draw(screen)

def draw_shop():
    draw_stars()
    draw_header()
    
    tabs = ["ENCHANTY", "W BUDOWIE"] 
    for i, t in enumerate(tabs):
        t_rect = pygame.Rect(30 + i*180, 110, 160, 40)
        active = current_tab == t
        pygame.draw.rect(screen, CYAN if active else PANEL_DARK, t_rect, border_radius=5)
        txt_color = BG_DEEP if active else WHITE
        txt = font_main.render(t, True, txt_color)
        screen.blit(txt, (t_rect.centerx - txt.get_width()//2, t_rect.centery - txt.get_height()//2))

    if current_tab == "W BUDOWIE":
        info_rect = pygame.Rect(150, 250, WIDTH - 300, 300)
        pygame.draw.rect(screen, PANEL_DARK, info_rect, border_radius=20)
        pygame.draw.rect(screen, MAGENTA, info_rect, 2, border_radius=20)
        
        text_title = font_title.render("SEKTOR W BUDOWIE", True, MAGENTA)
        text_desc1 = font_main.render("Więcej unikalnych kategorii oraz kosmicznych", True, WHITE)
        text_desc2 = font_main.render("przedmiotów pojawi się tutaj z czasem!", True, WHITE)
        text_hint = font_small.render("[System Aktualizacji GALAXY v1.4]", True, CYAN)
        
        screen.blit(text_title, (info_rect.centerx - text_title.get_width()//2, info_rect.y + 50))
        screen.blit(text_desc1, (info_rect.centerx - text_desc1.get_width()//2, info_rect.y + 130))
        screen.blit(text_desc2, (info_rect.centerx - text_desc2.get_width()//2, info_rect.y + 165))
        screen.blit(text_hint, (info_rect.centerx - text_hint.get_width()//2, info_rect.bottom - 40))
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

def get_sell_cards():
    cards = []
    padding_x = 50
    padding_y = 120
    card_height = 90
    card_spacing = 20
    cols = 1 if WIDTH < 1000 else 2
    available_width = WIDTH - padding_x * 2 - (cols - 1) * 20
    card_width = min(800, available_width / cols)
    btn_w = min(180, int(card_width * 0.28))
    for idx, (name, data) in enumerate(ores.items()):
        row = idx // cols
        col = idx % cols
        x = padding_x + col * (card_width + 20)
        y = padding_y + row * (card_height + card_spacing)
        card = pygame.Rect(x, y, card_width, card_height)
        button = pygame.Rect(card.right - btn_w - 20, y + 20, btn_w, 50)
        cards.append((name, data, card, button))
    return cards

def draw_sell():
    draw_stars()
    draw_header()
    btn_sell_all.rect = pygame.Rect(WIDTH - 440, 25, 220, 40)
    btn_sell_all.draw(screen)
    
    for name, data, card, s_btn in get_sell_cards():
        pygame.draw.rect(screen, PANEL_DARK, card, border_radius=15)
        screen.blit(font_main.render(f"SUROWIEC: {name}", True, WHITE), (card.x + 30, card.y + 20))
        screen.blit(font_small.render(f"ILOSC: {data['qty']}", True, CYAN), (card.x + 30, card.y + 50))
        pygame.draw.rect(screen, SUCCESS if data['qty'] > 0 else (60,60,60), s_btn, border_radius=8)
        label = font_main.render("SPRZEDAJ 1", True, WHITE)
        screen.blit(label, (s_btn.centerx - label.get_width()//2, s_btn.centery - label.get_height()//2))

def draw_casino():
    global active_input
    draw_stars()
    draw_header()
    
    m_w, m_h = WIDTH * 0.6, HEIGHT * 0.4
    m_x, m_y = (WIDTH - m_w) // 2, HEIGHT * 0.2
    
    pygame.draw.rect(screen, PANEL_DARK, (m_x, m_y, m_w, m_h), border_radius=20)
    pygame.draw.rect(screen, MAGENTA, (m_x, m_y, m_w, m_h), 3, border_radius=20)

    slot_w = m_w * 0.25
    slot_h = m_h * 0.5
    gap = (m_w - (3 * slot_w)) / 4

    for i in range(3):
        slot_x = m_x + gap + (i * (slot_w + gap))
        slot_y = m_y + (m_h * 0.2)
        slot_rect = pygame.Rect(slot_x, slot_y, slot_w, slot_h)
        
        pygame.draw.rect(screen, BG_DEEP, slot_rect, border_radius=15)
        pygame.draw.rect(screen, CYAN, slot_rect, 2, border_radius=15)
        
        res_font = get_font(int(slot_h * 0.3), True)
        t = res_font.render(casino_res[i], True, WHITE)
        screen.blit(t, (slot_rect.centerx - t.get_width()//2, slot_rect.centery - t.get_height()//2))

    inp_w, inp_h = m_w * 0.4, HEIGHT * 0.06
    inp_rect = pygame.Rect((WIDTH - inp_w)//2, m_y + m_h + 20, inp_w, inp_h)
    pygame.draw.rect(screen, WHITE if active_input else PANEL_DARK, inp_rect, 2, border_radius=10)
    
    b_txt = font_main.render(f"STAWKA: {casino_bet}$", True, GOLD)
    screen.blit(b_txt, (inp_rect.centerx - b_txt.get_width()//2, inp_rect.centery - b_txt.get_height()//2))
    
    m_txt = font_main.render(casino_msg, True, MAGENTA)
    screen.blit(m_txt, (WIDTH//2 - m_txt.get_width()//2, inp_rect.bottom + 10))
    
    spin_btn = Button("URUCHOM SILNIKI", WIDTH//2 - 125, int(inp_rect.bottom + 50), 250, 60, MAGENTA, WHITE)
    spin_btn.draw(screen)
    
    return spin_btn, inp_rect 

def handle_casino():
    global wallet, casino_res, casino_msg
    try: 
        bet = int(casino_bet)
    except: 
        return
    if bet > wallet or bet <= 0:
        casino_msg = "BRAK SRODKOW!"
        return
    
    wallet -= bet
    symbols = ["777", "VOID", "STAR", "GOLD", "ATOM"] + ["LOSS"] * 30 
    casino_res = [random.choice(symbols) for _ in range(3)]
    
    if casino_res[0] == casino_res[1] == casino_res[2] and casino_res[0] == "777":
        win = bet * 50
        wallet += win
        casino_msg = f"JACKPOT! +{win}$"
    elif casino_res[0] == casino_res[1] == casino_res[2] and casino_res[0] != "LOSS":
        win = bet * 15
        wallet += win
        casino_msg = f"TRIPLE! +{win}$"
    elif (casino_res[0] == casino_res[1] and casino_res[0] != "LOSS") or (casino_res[1] == casino_res[2] and casino_res[1] != "LOSS"):
        win = bet * 2
        wallet += win
        casino_msg = f"PARA! +{win}$"
    else:
        casino_msg = "PRZEGRANA. PROBUJ DALEJ."

running = True
while running:
    WIDTH, HEIGHT = screen.get_size() 
    
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT: running = False
        
        if current_state == "MENU":
            if btn_to_shop.clicked(event): current_state = "SHOP"
            elif btn_to_sell.clicked(event): current_state = "SELL"
            elif btn_to_casino.clicked(event): current_state = "CASINO"
        
        elif current_state == "SHOP":
            if btn_back.clicked(event): current_state = "MENU"
            if event.type == pygame.MOUSEBUTTONDOWN:
                tabs = ["ENCHANTY", "W BUDOWIE"]
                for i, t in enumerate(tabs):
                    t_rect = pygame.Rect(30 + i*180, 110, 160, 40)
                    if t_rect.collidepoint(event.pos):
                        current_tab = t
  
                if current_tab in shop_items and len(shop_items[current_tab]) > 0:
                    for i, item in enumerate(shop_items[current_tab]):
                        y_pos = 170 + (i * 120)
                        buy_rect = pygame.Rect(720, y_pos + 25, 120, 50)
                        if buy_rect.collidepoint(event.pos):
                            if wallet >= item["price"] and item["name"] not in inventory:
                                wallet -= item["price"]
                                inventory.append(item["name"])
        
        elif current_state == "SELL":
            if btn_back.clicked(event): current_state = "MENU"
            if btn_sell_all.clicked(event):
                for name in ores:
                    wallet += ores[name]["qty"] * ores[name]["price"]
                    ores[name]["qty"] = 0
            if event.type == pygame.MOUSEBUTTONDOWN:
                for name, data, card, s_btn in get_sell_cards():
                    if s_btn.collidepoint(event.pos) and data["qty"] > 0:
                        wallet += data["price"]
                        data["qty"] -= 1
        
        elif current_state == "CASINO":
            s_btn, input_box = draw_casino() 
            
            if s_btn.clicked(event): 
                handle_casino()
            if btn_back.clicked(event): 
                current_state = "MENU"
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                active_input = input_box.collidepoint(event.pos)
            
            if event.type == pygame.KEYDOWN and active_input:
                if event.key == pygame.K_BACKSPACE: 
                    casino_bet = casino_bet[:-1]
                elif event.unicode.isdigit(): 
                    casino_bet += event.unicode

    if current_state == "SPLASH": 
        splash_screen()
    elif current_state == "MENU":
        draw_stars()
        title = font_huge.render("GALAXY Shop", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, HEIGHT * 0.2))
        
        btn_to_shop.rect = pygame.Rect(WIDTH//2 - 150, HEIGHT * 0.4, 300, 60)
        btn_to_sell.rect = pygame.Rect(WIDTH//2 - 150, HEIGHT * 0.5, 300, 60)
        btn_to_casino.rect = pygame.Rect(WIDTH//2 - 150, HEIGHT * 0.6, 300, 60)
        
        btn_to_shop.draw(screen)
        btn_to_sell.draw(screen)
        btn_to_casino.draw(screen)
        
    elif current_state == "SHOP": draw_shop()
    elif current_state == "SELL": draw_sell()
    elif current_state == "CASINO":
        pass 

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
