import random
import pygame
from config import W, H, clamp, lerp_col, sprite

# ── Constantes ────────────────────────────────────────────────────────────────
SHIP_Y      = H - 95        # position Y fixe du vaisseau (remplace @property)
TEMPS_TOTAL = 60.0


# ── Spawn helper ──────────────────────────────────────────────────────────────
def spawner_debris(state):
    """
    Ajoute un débris spatial à la liste.
    CM1 : if/elif  |  CM2 : append  |  CM3 : random.randint, random.uniform
    """
    # Remplacement de random.choices (non vu en cours) par if/elif (CM1)
    r = random.random()
    if r < 0.6:
        sz = "small"
    elif r < 0.9:
        sz = "medium"
    else:
        sz = "large"

    # CM5 : dictionnaire pour les hp selon la taille
    hp_par_taille = {"small": 1, "medium": 2, "large": 3}
    hp = hp_par_taille.get(sz, 1)

    state["debris"].append({
        "sz":     sz,
        "hp":     hp,
        "max_hp": hp,
        "img":    sprite("debris_" + sz),
        "x":      random.uniform(40, W - 40),
        "y":      -60.0,
        "vx":     random.uniform(-15, 15),
        "vy":     random.uniform(60, 110 + state["diff"] * 2),
        "rot":    random.uniform(0, 360),
        "rots":   random.uniform(-60, 60),
    })


# ── Création de l'état (CM5 : dictionnaire) ───────────────────────────────────
def creer_space(data):
    """Initialise et retourne le dictionnaire d'état du jeu Espace."""
    # Fond étoilé généré une seule fois (CM1 : for  |  CM3 : random)
    bg = pygame.Surface((W, H))
    bg.fill((8, 10, 18))
    for _ in range(180):
        x = random.randint(0, W)
        y = random.randint(0, H)
        r = random.choice([1, 1, 1, 2])
        c = random.randint(180, 255)
        pygame.draw.circle(bg, (c, c, c), (x, y), r)

    state = {
        "font":        pygame.font.Font(None, 28),
        "bg":          bg,
        "ship_img":    sprite("ship"),
        "laser_img":   sprite("laser"),
        # Vaisseau
        "ship_x":      float(W // 2),
        "vx":          0.0,
        # Tir
        "lasers":      [],      # CM2 : liste de [x, y]
        "cool":        0.0,
        "energy":      100.0,
        # Entités (CM2 : listes)
        "debris":      [],
        "float_texts": [],
        # Stats
        "score":       0,
        "lives":       3,
        "time_left":   TEMPS_TOTAL,
        "diff":        0.0,
        "spawn_t":     0.0,
        "details":     [],
    }
    return state


# ── Gestion des événements ─────────────────────────────────────────────────────
def gerer_space(state, event):
    """
    Gère un événement pygame.
    Retourne 'menu', 'pause' ou None.
    CM1 : if/elif
    """
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            return "menu"
        elif event.key == pygame.K_p:
            return "pause"
        elif event.key == pygame.K_SPACE:
            if state["cool"] <= 0 and state["energy"] >= 12:
                state["energy"] -= 12
                state["cool"]    = 0.2
                state["lasers"].append([state["ship_x"] - 18, SHIP_Y + 10])
                state["lasers"].append([state["ship_x"] + 18, SHIP_Y + 10])
    return None


# ── Mise à jour ────────────────────────────────────────────────────────────────
def mettre_a_jour_space(state, dt):
    """
    Met à jour toute la physique du jeu Espace.
    Retourne 'fin' si la partie est terminée, sinon None.
    CM1 : if/elif, for  |  CM2 : append, remove, len  |  CM5 : dict.get
    """
    state["time_left"] -= dt
    state["diff"]      += dt

    # — Fin de partie —
    if state["time_left"] <= 0 or state["lives"] <= 0:
        state["details"] = [("Débris détruits", str(state["score"]))]
        return "fin"

    # — Vaisseau —
    keys = pygame.key.get_pressed()
    ax = 0
    if keys[pygame.K_LEFT] or keys[pygame.K_a]:
        ax -= 1250
    if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
        ax += 1250
    state["vx"]     = clamp(state["vx"] * (1 - 10 * dt) + ax * dt, -300, 300)
    state["ship_x"] = clamp(state["ship_x"] + state["vx"] * dt, 40, W - 40)

    # — Énergie et cooldown —
    state["energy"] = min(100.0, state["energy"] + 28 * dt)
    if state["cool"] > 0:
        state["cool"] -= dt

    # — Lasers —
    for l in state["lasers"][:]:    # CM1 : for  |  CM2 : copie de liste
        l[1] -= 560 * dt
        if l[1] < -20:
            state["lasers"].remove(l)   # CM2 : remove

    # — Débris —
    ship_rect = pygame.Rect(state["ship_x"] - 25, SHIP_Y - 20, 50, 60)

    # CM5 : dictionnaire points par taille
    pts_par_taille = {"small": 1, "medium": 2, "large": 3}

    for d in state["debris"][:]:
        d["x"]   += d["vx"]   * dt
        d["y"]   += d["vy"]   * dt
        d["rot"] += d["rots"] * dt

        dr = pygame.Rect(0, 0, d["img"].get_width(), d["img"].get_height())
        dr.center = (int(d["x"]), int(d["y"]))

        touche = False
        for l in state["lasers"][:]:
            if dr.collidepoint(int(l[0]), int(l[1])):
                if l in state["lasers"]:
                    state["lasers"].remove(l)
                d["hp"] -= 1
                touche = True
                if d["hp"] <= 0:
                    pts = pts_par_taille.get(d["sz"], 1)    # CM5 : dict.get
                    state["score"] += pts
                    state["float_texts"].append(
                        [d["x"], d["y"], "+" + str(pts), 0.0, (255, 220, 60)]
                    )
                    if d in state["debris"]:
                        state["debris"].remove(d)
                break

        if touche and d not in state["debris"]:
            continue
        if dr.colliderect(ship_rect):
            state["lives"] -= 1
            if d in state["debris"]:
                state["debris"].remove(d)
        elif d["y"] > H + 50:
            if d in state["debris"]:
                state["debris"].remove(d)

    # — Spawn —
    state["spawn_t"] += dt
    seuil = max(0.4, 1.2 - state["diff"] * 0.02)
    if state["spawn_t"] >= seuil:
        state["spawn_t"] = 0.0
        spawner_debris(state)

    # — Textes flottants —
    for ft in state["float_texts"][:]:
        ft[1] -= 45 * dt
        ft[3] += dt
        if ft[3] > 1.0:
            state["float_texts"].remove(ft)

    return None


# ── Dessin ─────────────────────────────────────────────────────────────────────
def dessiner_space(screen, state):
    """
    Affiche tout le jeu Espace.
    CM1 : for, if  |  CM2 : itération de liste  |  CM5 : dict.get
    """
    screen.blit(state["bg"], (0, 0))

    for l in state["lasers"]:
        screen.blit(state["laser_img"], (int(l[0]), int(l[1])))

    screen.blit(state["ship_img"], (int(state["ship_x"] - 28), SHIP_Y - 35))

    for d in state["debris"]:
        img = pygame.transform.rotate(d["img"], d["rot"])
        cx  = int(d["x"])
        cy  = int(d["y"])
        screen.blit(img, img.get_rect(center=(cx, cy)))
        if d["max_hp"] > 1:
            bw  = img.get_width()
            pct = d["hp"] / d["max_hp"]
            pygame.draw.rect(screen, (70, 70, 70),
                             (cx - bw // 2, cy - img.get_height() // 2 - 10, bw, 5))
            pygame.draw.rect(screen, lerp_col((255, 60, 60), (70, 210, 140), pct),
                             (cx - bw // 2, cy - img.get_height() // 2 - 10,
                              int(bw * pct), 5))

    for ft in state["float_texts"]:
        a = int(255 * (1 - ft[3]))
        s = state["font"].render(ft[2], True, ft[4])
        s.set_alpha(a)
        screen.blit(s, (int(ft[0]), int(ft[1])))

    # HUD — bande semi-transparente en haut
    hud = pygame.Surface((W, 38))
    hud.set_alpha(140)
    hud.fill((0, 0, 0))
    screen.blit(hud, (0, 0))

    # Score (gauche)
    font_score = pygame.font.Font(None, 36)
    score_lbl = state["font"].render("SCORE", True, (120, 130, 160))
    score_val = font_score.render(str(state["score"]), True, (255, 255, 255))
    screen.blit(score_lbl, (12, 4))
    screen.blit(score_val, (12, 20))

    # Vies (droite)
    font_coeur = pygame.font.Font(None, 30)
    vies_str = ""
    for _ in range(state["lives"]):     # CM1 : for
        vies_str += "♥ "
    vies_str = vies_str.rstrip()
    screen.blit(font_coeur.render("VIES", True, (120, 130, 160)), (W - 68, 4))
    screen.blit(font_coeur.render(vies_str,  True, (220, 70, 70)),  (W - 68, 20))

    # Énergie (centre)
    pct = state["energy"] / 100.0
    screen.blit(state["font"].render("NRJ", True, (180, 180, 200)), (W // 2 - 108, 10))
    pygame.draw.rect(screen, (40, 40, 55), (W // 2 - 80, 12, 160, 14), border_radius=7)
    if pct > 0.3:
        ecol = (70, 210, 140)
    else:
        ecol = (220, 80, 80)
    pygame.draw.rect(screen, ecol, (W // 2 - 80, 12, int(160 * pct), 14), border_radius=7)

    # Barre de temps verticale (bord droit)
    tpct = max(0, state["time_left"] / TEMPS_TOTAL)
    pygame.draw.rect(screen, (40, 40, 55), (W - 22, 48, 12, H - 68), border_radius=6)
    fh = int((H - 68) * tpct)
    pygame.draw.rect(screen, lerp_col((255, 60, 60), (70, 210, 140), tpct),
                     (W - 22, 48 + (H - 68) - fh, 12, fh), border_radius=6)
    font_t = pygame.font.Font(None, 22)
    t_lbl  = font_t.render(str(int(state["time_left"])) + "s", True, (180, 180, 200))
    screen.blit(t_lbl, (W - 26 - t_lbl.get_width() // 2, H - 52))