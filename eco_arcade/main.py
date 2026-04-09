import sys
import pygame
from config import W, H, FPS, load_save, save_now
import menu as menu_mod

screen = None
clock = None
running = True
data = {}

scene_courante = {}
pile_scenes = []


def aller(nouvelle_scene):
    global scene_courante
    del pile_scenes[:]
    scene_courante = nouvelle_scene


def empiler(nouvelle_scene):
    global scene_courante
    pile_scenes.append(scene_courante)
    scene_courante = nouvelle_scene


def depiler():
    global scene_courante
    if len(pile_scenes) > 0:
        scene_courante = pile_scenes.pop()


font_pause_grand = None
font_pause_petit = None


def init_fonts_pause():
    global font_pause_grand, font_pause_petit
    if font_pause_grand is None:
        font_pause_grand = pygame.font.Font(None, 64)
        font_pause_petit = pygame.font.Font(None, 28)


def gerer_pause(state, event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
            return "reprendre"
        elif event.key == pygame.K_m:
            return "menu"
    return None


def dessiner_pause(surf, state):
    init_fonts_pause()
    sous_type = state["sous_scene"]["type"]
    sous_state = state["sous_scene"]["state"]
    if sous_type == "ocean":
        import ocean as ocean_mod
        ocean_mod.dessiner_ocean(surf, sous_state)
    elif sous_type == "jungle":
        import jungle as jungle_mod
        jungle_mod.dessiner_jungle(surf, sous_state)
    elif sous_type == "space":
        import space as space_mod
        space_mod.dessiner_space(surf, sous_state)
    voile = pygame.Surface((W, H))
    voile.set_alpha(160)
    voile.fill((0, 0, 0))
    surf.blit(voile, (0, 0))
    t = font_pause_grand.render("PAUSE", True, (255, 255, 255))
    surf.blit(t, (W // 2 - t.get_width() // 2, H // 2 - 60))
    hints = ["P / ESC : reprendre", "M : menu principal"]
    for i in range(len(hints)):
        r = font_pause_petit.render(hints[i], True, (200, 205, 215))
        surf.blit(r, (W // 2 - r.get_width() // 2, H // 2 + 10 + i * 36))


font_fin_grand = None
font_fin_petit = None


def init_fonts_fin():
    global font_fin_grand, font_fin_petit
    if font_fin_grand is None:
        font_fin_grand = pygame.font.Font(None, 64)
        font_fin_petit = pygame.font.Font(None, 30)


def creer_fin(mode, scene_state):
    score = scene_state.get("score", 0)
    meilleur = data["best"].get(mode, 0)
    if score > meilleur:
        data["best"].update({mode: score})
        save_now(data)
    meilleur = data["best"].get(mode, 0)
    details = scene_state.get("details", [])
    return {"mode": mode, "score": score, "meilleur": meilleur, "details": details}


def gerer_fin(state, event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_RETURN or event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
            return "menu"
    return None


def dessiner_fin(surf, state):
    init_fonts_fin()
    surf.fill((12, 14, 20))
    t = font_fin_grand.render("Fin de partie", True, (255, 255, 255))
    surf.blit(t, (W // 2 - t.get_width() // 2, 80))
    lignes = [
        ("Mode",     state["mode"].upper()),
        ("Score",    str(state["score"])),
        ("Meilleur", str(state["meilleur"])),
    ]
    for detail in state["details"]:
        lignes.append(detail)
    y = 180
    for k, v in lignes:
        if k == "Score":
            col = (70, 210, 140)
        else:
            col = (210, 215, 225)
        r = font_fin_petit.render(k + " :  " + v, True, col)
        surf.blit(r, (W // 2 - r.get_width() // 2, y))
        y += 44
    if state["score"] >= state["meilleur"] and state["score"] > 0:
        font_record = pygame.font.Font(None, 36)
        rec = font_record.render("★ NOUVEAU RECORD ★", True, (255, 210, 40))
        surf.blit(rec, (W // 2 - rec.get_width() // 2, y + 10))
    hint = font_fin_petit.render("ESC / Entrée : retour au menu", True, (100, 105, 115))
    surf.blit(hint, (W // 2 - hint.get_width() // 2, H - 50))


def initialiser():
    global screen, clock, data, scene_courante
    pygame.init()
    pygame.display.set_caption("Eco Arcade")
    screen = pygame.display.set_mode((W, H))
    clock = pygame.time.Clock()
    data = load_save()
    scene_courante = {"type": "menu", "state": menu_mod.creer_menu()}


def lancer():
    global running, scene_courante

    initialiser()

    while running:
        dt = min(clock.tick(FPS) / 1000.0, 0.05)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                s_type = scene_courante["type"]
                s_state = scene_courante["state"]

                if s_type == "menu":
                    action = menu_mod.gerer_menu(s_state, event)
                    if action == "ocean":
                        import ocean as ocean_mod
                        aller({"type": "ocean", "state": ocean_mod.creer_ocean(data)})
                    elif action == "jungle":
                        import jungle as jungle_mod
                        aller({"type": "jungle", "state": jungle_mod.creer_jungle(data)})
                    elif action == "space":
                        import space as space_mod
                        aller({"type": "space", "state": space_mod.creer_space(data)})
                    elif action == "instructions":
                        aller({"type": "instructions", "state": menu_mod.creer_instructions()})
                    elif action == "quitter":
                        running = False

                elif s_type == "instructions":
                    action = menu_mod.gerer_instructions(s_state, event)
                    if action == "retour":
                        aller({"type": "menu", "state": menu_mod.creer_menu()})

                elif s_type == "ocean":
                    import ocean as ocean_mod
                    action = ocean_mod.gerer_ocean(s_state, event)
                    if action == "menu":
                        aller({"type": "menu", "state": menu_mod.creer_menu()})
                    elif action == "pause":
                        empiler({"type": "pause", "state": {"sous_scene": scene_courante}})

                elif s_type == "jungle":
                    import jungle as jungle_mod
                    action = jungle_mod.gerer_jungle(s_state, event)
                    if action == "menu":
                        aller({"type": "menu", "state": menu_mod.creer_menu()})
                    elif action == "pause":
                        empiler({"type": "pause", "state": {"sous_scene": scene_courante}})

                elif s_type == "space":
                    import space as space_mod
                    action = space_mod.gerer_space(s_state, event)
                    if action == "menu":
                        aller({"type": "menu", "state": menu_mod.creer_menu()})
                    elif action == "pause":
                        empiler({"type": "pause", "state": {"sous_scene": scene_courante}})

                elif s_type == "pause":
                    action = gerer_pause(s_state, event)
                    if action == "reprendre":
                        depiler()
                    elif action == "menu":
                        aller({"type": "menu", "state": menu_mod.creer_menu()})

                elif s_type == "fin":
                    action = gerer_fin(s_state, event)
                    if action == "menu":
                        aller({"type": "menu", "state": menu_mod.creer_menu()})

        s_type = scene_courante["type"]
        s_state = scene_courante["state"]

        if s_type == "ocean":
            import ocean as ocean_mod
            resultat = ocean_mod.mettre_a_jour_ocean(s_state, dt)
            if resultat == "fin":
                aller({"type": "fin", "state": creer_fin("ocean", s_state)})
        elif s_type == "jungle":
            import jungle as jungle_mod
            resultat = jungle_mod.mettre_a_jour_jungle(s_state, dt)
            if resultat == "fin":
                aller({"type": "fin", "state": creer_fin("jungle", s_state)})
        elif s_type == "space":
            import space as space_mod
            resultat = space_mod.mettre_a_jour_space(s_state, dt)
            if resultat == "fin":
                aller({"type": "fin", "state": creer_fin("space", s_state)})

        s_type = scene_courante["type"]
        s_state = scene_courante["state"]

        if s_type == "menu":
            menu_mod.dessiner_menu(screen, s_state)
        elif s_type == "instructions":
            menu_mod.dessiner_instructions(screen, s_state)
        elif s_type == "ocean":
            import ocean as ocean_mod
            ocean_mod.dessiner_ocean(screen, s_state)
        elif s_type == "jungle":
            import jungle as jungle_mod
            jungle_mod.dessiner_jungle(screen, s_state)
        elif s_type == "space":
            import space as space_mod
            space_mod.dessiner_space(screen, s_state)
        elif s_type == "pause":
            dessiner_pause(screen, s_state)
        elif s_type == "fin":
            dessiner_fin(screen, s_state)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    lancer()