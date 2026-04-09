import pygame
from config import W, H

font_titre = None
font_bouton = None
font_petit = None
font_instr = None


def init_fonts():
    global font_titre, font_bouton, font_petit, font_instr
    if font_titre is None:
        font_titre  = pygame.font.Font(None, 88)
        font_bouton = pygame.font.Font(None, 38)
        font_petit  = pygame.font.Font(None, 22)
        font_instr  = pygame.font.Font(None, 26)


LABELS  = ["Océan", "Jungle", "Espace", "Instructions", "Quitter"]
ACTIONS = ["ocean", "jungle", "space", "instructions", "quitter"]

BOUTON_LARGEUR = 320
BOUTON_HAUTEUR = 54
BOUTON_DEBUT_Y = 210
BOUTON_PAS_Y   = 68


def rect_bouton(i):
    x = W // 2 - BOUTON_LARGEUR // 2
    y = BOUTON_DEBUT_Y + i * BOUTON_PAS_Y
    return (x, y, BOUTON_LARGEUR, BOUTON_HAUTEUR)


def bouton_clique(i, pos):
    x, y, w, h = rect_bouton(i)
    return x <= pos[0] <= x + w and y <= pos[1] <= y + h


def creer_menu():
    init_fonts()
    return {"selected": 0}


def creer_instructions():
    init_fonts()
    return {}


def gerer_menu(state, event):
    nb = len(LABELS)
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_DOWN or event.key == pygame.K_s:
            state["selected"] = (state["selected"] + 1) % nb
        elif event.key == pygame.K_UP or event.key == pygame.K_w:
            state["selected"] = (state["selected"] - 1) % nb
        elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
            return ACTIONS[state["selected"]]
        elif event.key == pygame.K_ESCAPE:
            return "quitter"
    elif event.type == pygame.MOUSEMOTION:
        for i in range(nb):
            if bouton_clique(i, event.pos):
                state["selected"] = i
    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        for i in range(nb):
            if bouton_clique(i, event.pos):
                return ACTIONS[i]
    return None


def gerer_instructions(state, event):
    if event.type == pygame.KEYDOWN:
        return "retour"
    return None


def dessiner_bouton(surf, i, selectionne):
    x, y, w, h = rect_bouton(i)
    if selectionne:
        couleur_fond = (70, 200, 120)
    else:
        couleur_fond = (40, 45, 58)
    pygame.draw.rect(surf, couleur_fond,    (x, y, w, h), border_radius=10)
    pygame.draw.rect(surf, (180, 185, 195), (x, y, w, h), 2, border_radius=10)
    txt = font_bouton.render(LABELS[i], True, (255, 255, 255))
    surf.blit(txt, (x + w // 2 - txt.get_width() // 2,
                    y + h // 2 - txt.get_height() // 2))


def dessiner_menu(surf, state):
    surf.fill((18, 22, 30))
    titre = font_titre.render("Eco Arcade", True, (255, 255, 255))
    surf.blit(titre, (W // 2 - titre.get_width() // 2, 80))
    for i in range(len(LABELS)):
        dessiner_bouton(surf, i, i == state["selected"])
    hint = font_petit.render("", True, (120, 125, 140))
    surf.blit(hint, (W // 2 - hint.get_width() // 2, H - 28))


def dessiner_instructions(surf, state):
    surf.fill((18, 22, 30))
    font_t = pygame.font.Font(None, 50)
    t = font_t.render("Instructions", True, (255, 255, 255))
    surf.blit(t, (W // 2 - t.get_width() // 2, 40))
    lignes = [
        ("OCÉAN",                                                        True),
        ("<- -> : déplacer le bateau",                                   False),
        ("ESPACE : lancer/rappeler le grappin",                          False),
        ("Attraper les déchets = +10 pts | Toucher un poisson = -1 vie", False),
        ("JUNGLE",                                                        True),
        ("<- -> : déplacer la voiture",                                   False),
        ("Le bac collecte les déchets | Éviter les singes",              False),
        ("ESPACE",                                                         True),
        ("<- -> : déplacer le vaisseau",                                   False),
        ("ESPACE : tirer | Détruire les débris pour marquer des points",  False),
        ("",                                                               False),
        ("P : Pause | ESC : menu",                                         False),
    ]
    y = 110
    for txt, gras in lignes:
        if gras:
            col        = (70, 210, 140)
            font_ligne = pygame.font.Font(None, 30)
        else:
            col        = (210, 215, 225)
            font_ligne = font_instr
        surf.blit(font_ligne.render(txt, True, col), (80, y))
        y += 36
    hint = font_instr.render(
        "Appuie sur n'importe quelle touche pour revenir",
        True, (100, 105, 115)
    )
    surf.blit(hint, (W // 2 - hint.get_width() // 2, H - 40))