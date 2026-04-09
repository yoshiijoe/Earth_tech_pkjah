import os
import json
import pygame

W   = 900
H   = 600
FPS = 60

_BASE  = os.path.dirname(os.path.abspath(__file__))
ASSETS = os.path.join(_BASE, "assets")
SAVE   = os.path.join(_BASE, "..", "save_simple.json")


def clamp(x, a, b):
    if x < a:
        return a
    elif x > b:
        return b
    else:
        return x


def lerp_col(c1, c2, t):
    resultat = []
    for i in range(3):
        valeur = int(c1[i] + (c2[i] - c1[i]) * t)
        resultat.append(valeur)
    return tuple(resultat)


_cache = {}

_TAILLES = {
    "boat":          (96,  60),
    "grapple":       (34,  34),
    "fish_orange":   (48,  32),
    "fish_blue":     (48,  32),
    "fish_purple":   (48,  32),
    "car":           (180, 135),
    "monkey":        (54,  56),
    "ship":          (56,  72),
    "laser":         (6,   28),
    "debris_small":  (26,  26),
    "debris_medium": (40,  40),
    "debris_large":  (56,  56),
    "trash_bottle":  (55,  55),
    "trash_can":     (55,  55),
    "trash_bag":     (55,  55),
    "trash_tire":    (55,  55),
    "trash_box":     (55,  55),
}


def sprite(nom, taille=None):
    sz  = taille or _TAILLES.get(nom)
    cle = (nom, sz)
    if cle in _cache:
        return _cache[cle]
    chemin = os.path.join(ASSETS, nom + ".png")
    img = pygame.image.load(chemin).convert_alpha()
    if sz is not None:
        img = pygame.transform.scale(img, sz)
    _cache[cle] = img
    return img


def load_save():
    try:
        f = open(SAVE)
        donnees = json.load(f)
        f.close()
        return donnees
    except:
        return {"best": {"ocean": 0, "jungle": 0, "space": 0}}


def save_now(donnees):
    try:
        f = open(SAVE, "w")
        json.dump(donnees, f)
        f.close()
    except:
        pass