import pygame
from hra import main as spust_hru
from hra import vykresli_text as vykresli_text
from hra import vykresli_tlacitko as vykresli_tlacitko
from fyzika import nastav_kolo

pygame.init()

obrazovka_sirka = 1920
obrazovka_vyska = 1080
screen = pygame.display.set_mode((obrazovka_sirka, obrazovka_vyska))
pygame.display.set_caption("Tour de Bike - Menu")

main_menu_imgs = []
for i in range(3):
    for j in range(3):
        main_menu_imgs.append(pygame.image.load(f"img/main_menu/{i}{j}.png").convert_alpha())

silnicka_img = pygame.image.load("img/silnicka.png").convert_alpha()
celopero_img = pygame.image.load("img/celopero.png").convert_alpha()
hardtail_img = pygame.image.load("img/hardtail.png").convert_alpha()
bike_imgs = [("Road bike", silnicka_img), ("Hardtail", hardtail_img), ("Full suspension", celopero_img)]

# Načti pozadí pro nastavení
obloha_img = pygame.image.load("img/obloha.png").convert_alpha()
obloha_img = pygame.transform.smoothscale(obloha_img, (obrazovka_sirka, obrazovka_vyska))

vybrane_kolo = 0 # 0=silnicka, 1=hardtail, 2=celopero
vybrane_jidlo = 0 # 0=banan, 1=tycinka, 2=kure

# TODO
# zmensit kolo v menu
# zmensit aktualni vybranou energii
# pridat kure
# upgrady, ruzny kola - horsky, silnicka, hardtail

def menu():
    global vybrane_kolo, vybrane_jidlo
    while True:
        screen.blit(main_menu_imgs[vybrane_kolo * 3 + vybrane_jidlo], (0,0))

        tlacitko_start = pygame.Rect(50,335,250,150)
        tlacitko_vylepseni = pygame.Rect(50,525,500,150)
        tlacitko_nastaveni = pygame.Rect(50,700,450,150)
        tlacitko_konec = pygame.Rect(50,880,250,150)
        
        
        # hitboxy
        # pygame.draw.rect(screen, "red",tlacitko_start,1)
        # pygame.draw.rect(screen, "red",tlacitko_vylepseni,1)
        # pygame.draw.rect(screen, "red", tlacitko_nastaveni, 1)
        # pygame.draw.rect(screen, "red",tlacitko_konec,1)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if tlacitko_start.collidepoint(event.pos):
                    if vybrane_kolo == 0:
                        akt_kolo = "silnicka"
                    elif vybrane_kolo == 1:
                        akt_kolo = "hardtail"
                    elif vybrane_kolo == 2:
                        akt_kolo = "celopero"

                    nastav_kolo(akt_kolo)
                    
                    spust_hru(akt_kolo, vybrane_jidlo)
                elif tlacitko_vylepseni.collidepoint(event.pos):
                    menu_vylepseni()
                elif tlacitko_nastaveni.collidepoint(event.pos):
                    menu_nastaveni()
                elif tlacitko_konec.collidepoint(event.pos):
                    pygame.quit()
                    quit()

def menu_vylepseni():
    global vybrane_kolo, vybrane_jidlo
    bezi = True
    while bezi:
        screen.blit(obloha_img, (0, 0))
        vykresli_text(screen, "Upgrades", (0,0,0), (100,100))

        leva_sipka = pygame.Rect(200, 350, 80, 120)
        prava_sipka = pygame.Rect(680, 350, 80, 120)
        _, obrazek = bike_imgs[vybrane_kolo]
        sirka_obrazek = obrazek.get_width()
        k = 300 / sirka_obrazek
        vyska_obrazek = obrazek.get_height() * k
        sirka_obrazek *= k
        

        pygame.draw.polygon(screen, (100, 100, 100), [(leva_sipka.right, leva_sipka.top), (leva_sipka.left, leva_sipka.centery), (leva_sipka.right, leva_sipka.bottom)])
        pygame.draw.polygon(screen, (100, 100, 100), [(prava_sipka.left, prava_sipka.top), (prava_sipka.right, prava_sipka.centery), (prava_sipka.left, prava_sipka.bottom)])


        kolo_nazev, kolo_img = bike_imgs[vybrane_kolo]
        kolo_img_scaled = pygame.transform.smoothscale(kolo_img, (sirka_obrazek, vyska_obrazek))
        x = leva_sipka.right + 50
        y = leva_sipka.top - 100
        screen.blit(kolo_img_scaled, (x,y))
        vykresli_text(screen, kolo_nazev, (0, 0, 0), (sirka_obrazek/2 + x, vyska_obrazek + y + 30), "center")

        upgrade1 = pygame.Rect(100, 600, 600, 100)
        upgrade2 = pygame.Rect(100, 750, 600, 100)
        vykresli_tlacitko(screen, "+ SPEED (nefugnuje)", upgrade1, barva_pozadi=(180, 180, 255), barva_textu=(0,0,0))
        vykresli_tlacitko(screen, "+ ENDURANCE (nefugnuje)", upgrade2, barva_pozadi=(180, 255, 180), barva_textu=(0,0,0))

        jidlo_rects = [
            pygame.Rect(800, 550, 200, 100),  # banan
            pygame.Rect(800, 700, 200, 100),  # tycinka
            pygame.Rect(800, 850, 200, 100),  # kure
        ]
        jidla = ["Banana", "Protein bar", "Chicken"]
        barvy = [(255, 255, 180), (220, 255, 220), (255, 220, 220)]

        for i in range(3):
            vykresli_tlacitko(
                screen,
                jidla[i],
                jidlo_rects[i],
                barva_pozadi=barvy[i],
                barva_textu=(0,0,0),
                barva_okraje=(0,0,255) if vybrane_jidlo == i else (0,0,0),
                tloustka_okraje=5 if vybrane_jidlo == i else 2
            )

        tlacitko_zpet = pygame.Rect(50, 900, 200, 100)
        vykresli_tlacitko(screen, "Back", tlacitko_zpet, barva_pozadi=(255, 100, 100), barva_textu=(0,0,0))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if leva_sipka.collidepoint(event.pos):
                    vybrane_kolo = (vybrane_kolo - 1) % len(bike_imgs)
                elif prava_sipka.collidepoint(event.pos):
                    vybrane_kolo = (vybrane_kolo + 1) % len(bike_imgs)
                elif tlacitko_zpet.collidepoint(event.pos):
                    bezi = False
                elif jidlo_rects[0].collidepoint(event.pos):
                    vybrane_jidlo = 0
                elif jidlo_rects[1].collidepoint(event.pos):
                    vybrane_jidlo = 1
                elif jidlo_rects[2].collidepoint(event.pos):
                    vybrane_jidlo = 2
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    bezi = False

def menu_nastaveni():
    bezi = True
    while bezi:
        screen.blit(obloha_img, (0, 0))
        vykresli_text(screen, "Settings", (0, 0, 0), (100, 100))

        vykresli_text(screen, "Volume: ", (0, 0, 0), (120, 250))
        vykresli_text(screen, "Potato PC (disables stones and clouds):", (0, 0, 0), (120, 325))
        vykresli_text(screen, "Credits:", (0, 0, 0), (120, 650))
        vykresli_text(screen, "Ondra - physics, antialiasing", (0, 0, 0), (120, 725))
        vykresli_text(screen, "Rosta - bug fix stones", (0, 0, 0), (120, 800))
        

        tlacitko_zpet = pygame.Rect(50, 900, 200, 100)
        vykresli_tlacitko(screen, "Back", tlacitko_zpet, barva_pozadi=(255, 100, 100), barva_textu=(0,0,0))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if tlacitko_zpet.collidepoint(event.pos):
                    bezi = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    bezi = False

menu()

# if __name__ == "__main__":
#     import cProfile
#     import pstats

#     profiler = cProfile.Profile()
#     profiler.enable()
#     menu()
#     profiler.disable()
#     stats = pstats.Stats(profiler).sort_stats('cumtime')
#     stats.print_stats(30)
#     pygame.quit()
