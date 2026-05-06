import pygame
import sys

pygame.init()

SCREEN_W, SCREEN_H = 400, 300
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Play Button")

# ── Colors ──────────────────────────────────────────────
SKY_BLUE      = (173, 216, 230)   # background
GOLD_DARK     = (210, 140,  10)   # outer border
GOLD_MID      = (240, 175,  20)   # button face (dark band)
GOLD_LIGHT    = (255, 210,  80)   # button face (light band)
CREAM         = (255, 245, 210)   # inner highlight rim
WHITE         = (255, 255, 255)   # text fill
SHADOW        = (180, 140,  30)   # text shadow / outline

# ── Button geometry ─────────────────────────────────────
BTN_W, BTN_H = 212, 90
BTN_X = (SCREEN_W - BTN_W) // 2
BTN_Y = (SCREEN_H - BTN_H) // 2
RADIUS = 18

# ── Font — replace with your font file path ─────────────
FONT_PATH = "../angrybirds-regular.ttf"   # ← put your font file here
FONT_SIZE = 54
font = pygame.font.Font(FONT_PATH, FONT_SIZE)

def draw_button(surf, hovered=False):
    surf = self.game.screen
    r = pygame.Rect(BTN_X, BTN_Y, BTN_W, BTN_H)

    # 1) Dark gold outer border
    pygame.draw.rect(surf, GOLD_DARK, r, 18)

    # 2) Main gold face (inset by 3px)
    inner = r.inflate(-6, -6)
    pygame.draw.rect(surf, GOLD_MID, inner, RADIUS - 2)

    # 3) Lighter highlight stripe across top half
    top_half = pygame.Rect(inner.x, inner.y, inner.w, inner.h // 2)
    highlight_surf = pygame.Surface((inner.w, inner.h // 2), pygame.SRCALPHA)
    highlight_surf.fill((0, 0, 0, 0))
    pygame.draw.rect(highlight_surf, GOLD_LIGHT,
                     (0, 0, inner.w, inner.h // 2),
                     border_radius=RADIUS - 2)
    surf.blit(highlight_surf, top_half.topleft)

    # 4) Cream inner rim
    rim = inner.inflate(-6, -6)
    pygame.draw.rect(surf, CREAM, rim, RADIUS - 4)

    # 5) Gold fill inside rim
    fill = rim.inflate(-8, -8)
    color = GOLD_LIGHT if hovered else GOLD_MID
    pygame.draw.rect(surf, color, fill, RADIUS - 6)

    # 6) Text with chunky outline/shadow
    label = "PLAY"
    text_surf = font.render(label, True, WHITE)
    shadow_surf = font.render(label, True, SHADOW)

    tx = r.centerx - text_surf.get_width() // 2
    ty = r.centery - text_surf.get_height() // 2 - 2

    # Draw shadow offsets
    for dx, dy in [(-2, 2), (2, 2), (0, 3), (-2, -1), (2, -1)]:
        surf.blit(shadow_surf, (tx + dx, ty + dy))
    surf.blit(text_surf, (tx, ty))

clock = pygame.time.Clock()
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit(); sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            btn_rect = pygame.Rect(BTN_X, BTN_Y, BTN_W, BTN_H)
            if btn_rect.collidepoint(mx, my):
                print("Play clicked!")

    mx, my = pygame.mouse.get_pos()
    hovered = pygame.Rect(BTN_X, BTN_Y, BTN_W, BTN_H).collidepoint(mx, my)

    screen.fill(SKY_BLUE)
    draw_button(screen, hovered)
    pygame.display.flip()
    clock.tick(60)
