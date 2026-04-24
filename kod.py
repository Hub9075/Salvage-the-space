import pygame

class Punkty_Podczas_kopania:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.suma_punktow = 0
        
        self.wartosci_rud = {
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
        
        self.rudy = list(self.wartosci_rud.keys())
        self.font = pygame.font.SysFont('Arial', 20)

    def dodawanie_punktow(self, nazwa_rudy):
        if nazwa_rudy in self.wartosci_rud:
            zdobyte = self.wartosci_rud[nazwa_rudy]
            self.suma_punktow += zdobyte
            print(f"Wykopano: {nazwa_rudy}! Dodano {zdobyte} pkt. Suma: {self.suma_punktow}")

    def wyswietl_punkty(self, okno):
        tekst = self.font.render(f"Punkty: {self.suma_punktow}", True, (255, 255, 255))
        okno.blit(tekst, (self.x, self.y))
