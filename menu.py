import pygame
import config
from hra import main as spust_hru
from hra import vykresli_text
from hra import vykresli_tlacitko
from hra import get_font
from fyzika import nastav_kolo

pygame.init()


screen = pygame.display.set_mode((config.obrazovka_sirka, config.obrazovka_vyska))
pygame.display.set_caption("Tour de Bike - Menu")

main_menu_imgs = []
for i in range(3):
    for j in range(3):
        main_menu_imgs.append(pygame.image.load(f"img/main_menu/{i}{j}.png").convert())

silnicka_img = pygame.image.load("img/silnicka.png").convert_alpha()
celopero_img = pygame.image.load("img/celopero.png").convert_alpha()
hardtail_img = pygame.image.load("img/hardtail.png").convert_alpha()
bike_imgs = [("Road bike", silnicka_img), ("Hardtail", hardtail_img), ("Full suspension", celopero_img)]

obloha_img = pygame.image.load("img/obloha.png").convert()
obloha_img = pygame.transform.smoothscale(obloha_img, (config.obrazovka_sirka, config.obrazovka_vyska))

#vybrane_kolo = 0 # 0=silnicka, 1=hardtail, 2=celopero
#vybrane_jidlo = 0 # 0=banan, 1=tycinka, 2=kure


margin_x = 50

# TODO!!!
# procentualne na obrazovce vykreslovat - vybrat rozliseni a fullscren
# nastaveni - potato pc, zvuk a musika volume, zobrazeni FPS   
# ulozeni a nacteni hry
# vylepseni kola - rychlost, mensi ztrata energie, 
# kupovani kol a lepsich jidel
# ruzne mapy (mesic, dalnice, hory. noc)
# hezci ui
# hudba, zvuk
# optimalizace
# cedulky s rekordama
# easter eggy

def menu():
    while True:
        screen.blit(main_menu_imgs[config.vybrane_kolo * 3 + config.vybrane_jidlo], (0,0))

        tlacitko_start = pygame.Rect(50,335,250,150)
        tlacitko_vylepseni = pygame.Rect(50,525,500,150)
        tlacitko_nastaveni = pygame.Rect(50,700,450,150)
        tlacitko_konec = pygame.Rect(50,880,250,150)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if tlacitko_start.collidepoint(event.pos):
                    nastav_kolo(config.vybrane_kolo)
                    
                    spust_hru()
                elif tlacitko_vylepseni.collidepoint(event.pos):
                    menu_vylepseni()
                elif tlacitko_nastaveni.collidepoint(event.pos):
                    menu_nastaveni()
                elif tlacitko_konec.collidepoint(event.pos):
                    pygame.quit()
                    quit()

def menu_vylepseni():
    bezi = True
    while bezi:
        screen.blit(obloha_img, (0, 0))
        vykresli_text(screen, "Upgrades", (0,0,0), (100,100))

        leva_sipka = pygame.Rect(200, 350, 80, 120)
        prava_sipka = pygame.Rect(680, 350, 80, 120)
        _, obrazek = bike_imgs[config.vybrane_kolo]
        sirka_obrazek = obrazek.get_width()
        k = 300 / sirka_obrazek
        vyska_obrazek = obrazek.get_height() * k
        sirka_obrazek *= k
        

        pygame.draw.polygon(screen, (100, 100, 100), [(leva_sipka.right, leva_sipka.top), (leva_sipka.left, leva_sipka.centery), (leva_sipka.right, leva_sipka.bottom)])
        pygame.draw.polygon(screen, (100, 100, 100), [(prava_sipka.left, prava_sipka.top), (prava_sipka.right, prava_sipka.centery), (prava_sipka.left, prava_sipka.bottom)])


        kolo_nazev, kolo_img = bike_imgs[config.vybrane_kolo]
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
                barva_okraje=(0,0,255) if config.vybrane_jidlo == i else (0,0,0),
                tloustka_okraje=5 if config.vybrane_jidlo == i else 2
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
                    config.vybrane_kolo = (config.vybrane_kolo - 1) % len(bike_imgs)
                elif prava_sipka.collidepoint(event.pos):
                    config.vybrane_kolo = (config.vybrane_kolo + 1) % len(bike_imgs)
                elif tlacitko_zpet.collidepoint(event.pos):
                    bezi = False
                elif jidlo_rects[0].collidepoint(event.pos):
                    config.vybrane_jidlo = 0
                elif jidlo_rects[1].collidepoint(event.pos):
                    config.vybrane_jidlo = 1
                elif jidlo_rects[2].collidepoint(event.pos):
                    config.vybrane_jidlo = 2
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    bezi = False

def vykresli_slider(screen, y, posuvnik_delka, value, popisek, max_text="100", jednotka = "%", min_text="0"):
    slider_vyska = 8
    posuvnik_polomer = 18
    slider_color = (180, 180, 180)
    posuvnik_color = (255, 200, 100)
    font_color = (0, 0, 0)

    if popisek == "FPS limit":
        if value > 0.99:
            zobrazena_hodnota = 270
        else:
            zobrazena_hodnota = int(30 + value * 240)
        vykresli_text(screen, f"{popisek} {zobrazena_hodnota} {jednotka}", font_color, (margin_x, y))
    else:
        if value > 0.99:
            vykresli_text(screen, f"{popisek} 100 {jednotka}", font_color, (margin_x, y))
        else:
            vykresli_text(screen, f"{popisek} {round(value*100)} {jednotka}", font_color, (margin_x, y))

    text_sirka, text_vyska = get_font(50, "Arial").size(f"{popisek} {max_text} {jednotka}")
    x = 1.5 * margin_x + text_sirka
    y += text_vyska / 2 
    pygame.draw.rect(screen, slider_color, (x, y, posuvnik_delka, slider_vyska), border_radius=4)
    
    posuvnik_x = x + int(value * posuvnik_delka)
    posuvnik_y = y + slider_vyska // 2
    pygame.draw.circle(screen, posuvnik_color, (posuvnik_x, posuvnik_y), posuvnik_polomer)

    return pygame.Rect(x, y - posuvnik_polomer, posuvnik_delka, posuvnik_polomer * 2)

def vykresli_zakliknuti(screen, y, popisek, zaklikly):
    velikost = 36
    barva_okraj = (120, 120, 120)
    if zaklikly:
        barva_vypln = (220, 255, 220) 
    else:
        barva_vypln = (240, 240, 240)
    barva_fajfka = (0, 180, 0)
    font_color = (0, 0, 0)

    vykresli_text(screen, popisek, font_color, (margin_x, y))
    text_sirka, text_vyska = get_font(50, "Arial").size(f"{popisek}")
    x = 1.5 * margin_x + text_sirka
    y += (text_vyska - velikost) / 2
    pygame.draw.rect(screen, barva_vypln, (x, y, velikost, velikost), border_radius=6)
    pygame.draw.rect(screen, barva_okraj, (x, y, velikost, velikost), 2, border_radius=6)
    if zaklikly:
        margin_fajfky = velikost//5
        pygame.draw.line(screen, barva_fajfka, (x+margin_fajfky, y+velikost//2), (x+velikost//2, y+velikost-margin_fajfky), 5)
        pygame.draw.line(screen, barva_fajfka, (x+velikost//2, y+velikost-margin_fajfky), (x+velikost-margin_fajfky, y+margin_fajfky), 5)
    
    return pygame.Rect(x, y, velikost, velikost)

def menu_nastaveni():
    bezi = True
    secret_code = ""
    zadavani_kodu = False
    zprava = ""
    zprava_cas = 0

    while bezi:
        screen.blit(obloha_img, (0, 0))
        vykresli_text(screen, "Settings", (0, 0, 0), (config.obrazovka_sirka//2, 100), "center", velikost=125)

        slider_rect_sound = vykresli_slider(screen, 150, 300, config.volume_sound, "Sound volume:")
        slider_rect_music = vykresli_slider(screen, 225, 300, config.volume_music, "Music volume:")

        checkbox_rect_potato = vykresli_zakliknuti(screen, 300, "Potato PC (disables stones and clouds):", config.potato_pc)
        checkbox_rect_fps = vykresli_zakliknuti(screen, 375, "Show FPS counter:", config.fps)
        slider_rect_fps_limit = vykresli_slider(screen, 450, 300, config.fps_limit, "FPS limit", 300, "FPS:")
        checkbox_rect_fullscreen = vykresli_zakliknuti(screen, 525, "Fullscreen:", config.fullscreen)

        vykresli_text(screen, "misto 1 na neco", (0,0,0), (margin_x, 600))
        vykresli_text(screen, "misto 2 na neco", (0,0,0), (margin_x, 675))
        
        vykresli_text(screen, "Secret code:", (0, 0, 0), (margin_x, 750))
        code_sirka, code_vyska = get_font(50, "Arial").size("Secret code:")
        kod_rect = pygame.Rect(2 * margin_x + code_sirka, 750, 350, 60)
        pygame.draw.rect(screen, (240, 240, 255), kod_rect)
        pygame.draw.rect(screen, (0,0,0), kod_rect, 2)
        if zadavani_kodu:
            vykresli_text(screen, secret_code, (0,0,0), (kod_rect.x + margin_x, kod_rect.centery - code_vyska/2))
        else:
            vykresli_text(screen, "Click to type...", (0,0,0), (kod_rect.x + margin_x, kod_rect.centery - code_vyska/2))
        if zprava:
            if len(zprava) < 29:
                vykresli_text(screen, zprava, (200, 0, 0), (config.obrazovka_sirka-margin_x,200), zarovnat="right", velikost=100)
            else:
                vykresli_text(screen, zprava, (200, 0, 0), (config.obrazovka_sirka-margin_x,200), zarovnat="right")
            if (pygame.time.get_ticks() / 1000) - zprava_cas > 2:
                zprava = ""

        tlacitko_reset = pygame.Rect(config.obrazovka_sirka - margin_x - 300, config.obrazovka_vyska - 120, 300, 80)
        vykresli_tlacitko(screen, "Reset settings", tlacitko_reset, barva_pozadi=(255, 200, 100), barva_textu=(0,0,0))

        tlacitko_zpet = pygame.Rect(margin_x, config.obrazovka_vyska - 120, 200, 80)
        vykresli_tlacitko(screen, "Back", tlacitko_zpet, barva_pozadi=(255, 100, 100), barva_textu=(0,0,0))

        vykresli_text(screen, "Credits:", (0, 0, 0), (margin_x, 825))
        vykresli_text(screen, "Ondra - physics, antialiasing, playtester; Rosta - bug fix stones, playtester; Martin - playtester", (0, 0, 0), (margin_x, 900), velikost=30)
        vykresli_text(screen, "", (0, 0, 0), (margin_x, 900))

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if tlacitko_zpet.collidepoint(event.pos):
                    bezi = False
                elif slider_rect_sound.collidepoint(event.pos):
                    config.volume_sound = min(max((event.pos[0] - slider_rect_sound.x) / slider_rect_sound.width, 0), 1)
                elif slider_rect_music.collidepoint(event.pos):
                    config.volume_music = min(max((event.pos[0] - slider_rect_music.x) / slider_rect_music.width, 0), 1)
                elif checkbox_rect_potato.collidepoint(event.pos):
                    config.potato_pc = not config.potato_pc
                elif checkbox_rect_fps.collidepoint(event.pos):
                    config.fps = not config.fps
                elif slider_rect_fps_limit.collidepoint(event.pos):
                    config.fps_limit = min(max((event.pos[0] - slider_rect_fps_limit.x)/ slider_rect_fps_limit.width,0),1)
                elif checkbox_rect_fullscreen.collidepoint(event.pos):
                    config.fullscreen = not config.fullscreen
                    if config.fullscreen:
                        pygame.display.set_mode((config.obrazovka_sirka, config.obrazovka_vyska), pygame.FULLSCREEN)
                    else:
                        pygame.display.set_mode((config.obrazovka_sirka, config.obrazovka_vyska))
                elif tlacitko_reset.collidepoint(event.pos):
                    config.volume_sound = 0.5
                    config.volume_music = 0.5
                    config.potato_pc = False
                    config.fps = False
                    config.fps_limit = 0.125
                    config.fullscreen = False
                    pygame.display.set_mode((config.obrazovka_sirka, config.obrazovka_vyska))
                    secret_code = ""
                    zprava = "Settings reset successfully!"
                    zprava_cas = pygame.time.get_ticks() / 1000


                elif kod_rect.collidepoint(event.pos):
                    zadavani_kodu = True
                    secret_code = ""
                    zprava = ""
                else:
                    zadavani_kodu = False
            elif event.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed()[0]:
                    if slider_rect_sound.collidepoint(event.pos):
                        config.volume_sound = min(max((event.pos[0] - slider_rect_sound.x) / slider_rect_sound.width, 0), 1)
                    elif slider_rect_music.collidepoint(event.pos):
                        config.volume_music = min(max((event.pos[0] - slider_rect_music.x) / slider_rect_music.width, 0), 1)
                    elif slider_rect_fps_limit.collidepoint(event.pos):
                        config.fps_limit = min(max((event.pos[0] - slider_rect_fps_limit.x)/ slider_rect_fps_limit.width,0),1)
            elif event.type == pygame.KEYDOWN:
                if zadavani_kodu:
                    if event.key == pygame.K_RETURN:
                        if secret_code == "sparkyjegay":
                            config.prachy += 1000000
                            zprava = "+ 1 milion"
                        else:
                            zprava = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
                        zadavani_kodu = False
                        zprava_cas = pygame.time.get_ticks() / 1000


                    elif event.key == pygame.K_BACKSPACE:
                        secret_code = secret_code[:-1]
                    else:
                        if len(secret_code) < 14 and event.unicode.isprintable():
                            secret_code += event.unicode
                elif event.key == pygame.K_ESCAPE:
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
