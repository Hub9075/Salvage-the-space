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
    return pygame.font.SysFont("Arial", size, bold=bold)

font_huge = get_font(52, True)
font_title = get_font(30, True)
font_main = get_font(18, True)
font_small = get_font(14)

wallet = 0
inventory = []

ores = {
    "coal": {"qty": 0, "price": 10, "label": "Węgiel"},
    "iron": {"qty": 0, "price": 25, "label": "Żelazo"},
    "gold": {"qty": 0, "price": 100, "label": "Złoto"},
}

shop_items = [
    {"name": "Efficiency I", "price": 100, "power": 1},
    {"name": "Efficiency II", "price": 500, "power": 2},
]

# 🎰 KASYNO
casino_bet = "100"
casino_result = ["?", "?", "?"]
casino_msg = "SPIN!"
casino_input_active = False

current_state = "GAME"

class Button:
    def __init__(self, text, x, y, w, h, color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color

    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)
        txt = font_main.render(self.text, True, WHITE)
        screen.blit(txt, (self.rect.centerx - txt.get_width()//2,
                          self.rect.centery - txt.get_height()//2))

    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos)

btn_shop = Button("SKLEP", 10, 10, 100, 40, CYAN)
btn_sell = Button("SELL", 120, 10, 100, 40, SUCCESS)
btn_casino = Button("KASYNO", 230, 10, 120, 40, MAGENTA)
btn_back = Button("BACK", 750, 10, 120, 40, CYAN)

def get_power():
    power = 1
    for item in shop_items:
        if item["name"] in inventory:
            power += item["power"]
    return power

def draw_game():
    screen.fill(BG_DEEP)
    btn_shop.draw()
    btn_sell.draw()
    btn_casino.draw()

    txt = font_main.render(f"KASA: {wallet}$", True, GOLD)
    screen.blit(txt, (350, 20))

def draw_shop():
    screen.fill((10, 10, 30))
    btn_back.draw()

    y = 150
    for item in shop_items:
        txt = font_main.render(item["name"], True, WHITE)
        screen.blit(txt, (100, y))

        price = font_small.render(f"{item['price']}$", True, GOLD)
        screen.blit(price, (300, y))

        buy_btn = pygame.Rect(450, y, 120, 40)
        pygame.draw.rect(screen, SUCCESS if wallet >= item["price"] else (60,60,60), buy_btn)

        t = font_small.render("BUY", True, WHITE)
        screen.blit(t, (buy_btn.x+30, buy_btn.y+10))

        item["btn"] = buy_btn
        y += 80

def draw_sell():
    screen.fill((20, 10, 10))
    btn_back.draw()

    y = 150
    for name, data in ores.items():
        txt = font_main.render(f"{data['label']} x{data['qty']}", True, WHITE)
        screen.blit(txt, (100, y))

        sell_btn = pygame.Rect(400, y, 120, 40)
        pygame.draw.rect(screen, SUCCESS, sell_btn)

        t = font_small.render("SELL 1", True, WHITE)
        screen.blit(t, (sell_btn.x+20, sell_btn.y+10))

        data["btn"] = sell_btn
        y += 80

def draw_casino():
    screen.fill((5, 0, 20))
    btn_back.draw()

    for i in range(3):
        txt = font_huge.render(casino_result[i], True, WHITE)
        screen.blit(txt, (300+i*100, 250))

    input_box = pygame.Rect(300, 350, 200, 40)
    pygame.draw.rect(screen, WHITE if casino_input_active else PANEL_DARK, input_box, 2)

    t = font_main.render(casino_bet, True, GOLD)
    screen.blit(t, (input_box.x+10, input_box.y+10))

    spin_btn = pygame.Rect(320, 420, 160, 50)
    pygame.draw.rect(screen, CYAN, spin_btn)
    txt = font_main.render("SPIN", True, BG_DEEP)
    screen.blit(txt, (spin_btn.centerx - txt.get_width()//2, spin_btn.centery - txt.get_height()//2))

    msg = font_main.render(casino_msg, True, WHITE)
    screen.blit(msg, (300, 500))

    return input_box, spin_btn

running = True
while running:
    events = pygame.event.get()

    for event in events:
        if event.type == pygame.QUIT:
            running = False

        if current_state == "GAME":
            if btn_shop.clicked(event):
                current_state = "SHOP"
            if btn_sell.clicked(event):
                current_state = "SELL"
            if btn_casino.clicked(event):
                current_state = "CASINO"

        elif current_state == "SHOP":
            if btn_back.clicked(event):
                current_state = "GAME"

            if event.type == pygame.MOUSEBUTTONDOWN:
                for item in shop_items:
                    if item["btn"].collidepoint(event.pos):
                        if wallet >= item["price"]:
                            wallet -= item["price"]
                            inventory.append(item["name"])

        elif current_state == "SELL":
            if btn_back.clicked(event):
                current_state = "GAME"

            if event.type == pygame.MOUSEBUTTONDOWN:
                for data in ores.values():
                    if data["btn"].collidepoint(event.pos):
                        if data["qty"] > 0:
                            data["qty"] -= 1
                            wallet += data["price"]

        elif current_state == "CASINO":
            input_box, spin_btn = draw_casino()

            if btn_back.clicked(event):
                current_state = "GAME"

            if event.type == pygame.MOUSEBUTTONDOWN:
                casino_input_active = input_box.collidepoint(event.pos)

                if spin_btn.collidepoint(event.pos):
                    if casino_bet.isdigit():
                        bet = int(casino_bet)
                        if bet > 0 and wallet >= bet:
                            wallet -= bet
                            symbols = ["7","★","♦","♣"]
                            casino_result = [random.choice(symbols) for _ in range(3)]

                            if casino_result[0] == casino_result[1] == casino_result[2]:
                                win = bet * 5
                                wallet += win
                                casino_msg = f"JACKPOT +{win}$"
                            elif casino_result[0] == casino_result[1] or casino_result[1] == casino_result[2]:
                                win = bet * 2
                                wallet += win
                                casino_msg = f"+{win}$"
                            else:
                                casino_msg = "PRZEGRANA"

            if event.type == pygame.KEYDOWN and casino_input_active:
                if event.key == pygame.K_BACKSPACE:
                    casino_bet = casino_bet[:-1]
                elif event.unicode.isdigit():
                    casino_bet += event.unicode

    if current_state == "GAME":
        draw_game()
    elif current_state == "SHOP":
        draw_shop()
    elif current_state == "SELL":
        draw_sell()
    elif current_state == "CASINO":
        draw_casino()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()