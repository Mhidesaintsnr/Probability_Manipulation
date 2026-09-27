"""
SEE THE ODDS - Pygame Edition
A transparent gambling-math education simulator.

Two modes:
  - Fair 50/50: true fair coin, win chance is exactly 50%
  - House Edge: win chance is secretly lower (shown honestly on screen here,
    unlike a real predatory game), to demonstrate how "50/50-feeling" games
    can still guarantee long-run losses.

"""

import pygame
import random
import sys

pygame.init()
WIDTH, HEIGHT = 460, 760
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("See The Odds")
clock = pygame.time.Clock()

FONT = pygame.font.SysFont("arial", 20)
FONT_BOLD = pygame.font.SysFont("arial", 20, bold=True)
FONT_BIG = pygame.font.SysFont("arial", 30, bold=True)
FONT_SMALL = pygame.font.SysFont("arial", 15)
FONT_TINY = pygame.font.SysFont("arial", 13)

BG = (15, 17, 21)
PANEL = (26, 29, 36)
LINE = (42, 46, 56)
TEXT = (238, 240, 244)
SUB = (154, 161, 173)
ACCENT = (242, 193, 78)
ACCENT2 = (78, 203, 141)
LOSE = (226, 87, 76)
WARN = (231, 163, 62)

HOUSE_WIN_PROB = 0.46
PLAYER_WIN_PROB = 0.70
STARTING_BALANCE = 1000

# ---------- STATE ----------
mode = "fair"
balance = STARTING_BALANCE
wins = 0
rounds = 0
wagered = 0
history = [STARTING_BALANCE]
choice = "HEAD"
stake_text = "50"
stake_active = False
message = ""
message_color = TEXT
last_stake = None
loss_streak = 0
escalate_count = 0
show_warning = False
spin_timer = 0
spinning = False
last_answer = None


def win_prob():
    if mode == "fair":
        return 0.5
    elif mode == "house":
        return HOUSE_WIN_PROB
    else:
        return PLAYER_WIN_PROB


def reset():
    global balance, wins, rounds, wagered, history, last_stake, loss_streak
    global escalate_count, show_warning, message, last_answer
    balance = STARTING_BALANCE
    wins = 0
    rounds = 0
    wagered = 0
    history = [STARTING_BALANCE]
    last_stake = None
    loss_streak = 0
    escalate_count = 0
    show_warning = False
    message = ""
    last_answer = None


def check_chasing(stake):
    global last_stake, loss_streak, escalate_count, show_warning
    if last_stake is not None and loss_streak > 0 and stake > last_stake:
        escalate_count += 1
    if escalate_count >= 2:
        show_warning = True


def play_round(stake):
    global balance, wins, rounds, wagered, loss_streak, last_stake, last_answer
    wagered += stake
    rounds += 1
    win = random.random() < win_prob()
    answer = choice if win else ("TAIL" if choice == "HEAD" else "HEAD")
    if win:
        balance += stake  # net gain (2x payout minus the stake already "spent")
        wins += 1
        loss_streak = 0
    else:
        balance -= stake
        loss_streak += 1
    check_chasing(stake)
    last_stake = stake
    last_answer = answer
    history.append(max(balance, 0))
    return win, answer


# ---------- LAYOUT ----------
fair_btn = pygame.Rect(20, 70, 133, 40)
house_btn = pygame.Rect(163, 70, 133, 40)
player_btn = pygame.Rect(306, 70, 134, 40)

stake_box = pygame.Rect(20, 400, 420, 38)
head_btn = pygame.Rect(20, 450, 205, 42)
tail_btn = pygame.Rect(235, 450, 205, 42)
flip_btn = pygame.Rect(20, 505, 420, 46)
fast_btn = pygame.Rect(20, 560, 420, 40)
reset_btn = pygame.Rect(20, 610, 420, 36)

chart_rect = pygame.Rect(20, 660, 420, 80)


def draw_button(rect, text, active=False, disabled=False, primary=False):
    color = PANEL
    border = LINE
    text_color = TEXT
    if primary and not disabled:
        color = ACCENT
        text_color = (34, 26, 0)
    if active:
        border = ACCENT
    if disabled:
        color = (20, 22, 27)
        text_color = SUB
    pygame.draw.rect(screen, color, rect, border_radius=10)
    if not primary:
        pygame.draw.rect(screen, border, rect, 2, border_radius=10)
    label = FONT.render(text, True, text_color)
    screen.blit(label, label.get_rect(center=rect.center))


def draw_stat(x, y, w, value, label):
    r = pygame.Rect(x, y, w, 46)
    pygame.draw.rect(screen, BG, r, border_radius=8)
    pygame.draw.rect(screen, LINE, r, 1, border_radius=8)
    v = FONT_BOLD.render(str(value), True, TEXT)
    screen.blit(v, v.get_rect(center=(r.centerx, r.y + 16)))
    l = FONT_TINY.render(label, True, SUB)
    screen.blit(l, l.get_rect(center=(r.centerx, r.y + 34)))


def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    cur = ""
    for w in words:
        test = (cur + " " + w).strip()
        if font.size(test)[0] > max_width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    return lines


def draw_chart(rect):
    pygame.draw.rect(screen, PANEL, rect, border_radius=8)
    pygame.draw.rect(screen, LINE, rect, 1, border_radius=8)
    data = history[-200:]
    if len(data) < 2:
        return
    max_v = max(max(data), 1)
    min_v = min(min(data), 0)
    rng = (max_v - min_v) or 1
    pad = 6
    step_x = (rect.width - 2 * pad) / (len(data) - 1)

    # baseline (starting balance)
    base_y = rect.bottom - pad - ((STARTING_BALANCE - min_v) / rng) * (rect.height - 2 * pad)
    pygame.draw.line(screen, LINE, (rect.left, base_y), (rect.right, base_y), 1)

    points = []
    for i, v in enumerate(data):
        x = rect.left + pad + i * step_x
        y = rect.bottom - pad - ((v - min_v) / rng) * (rect.height - 2 * pad)
        points.append((x, y))
    if len(points) >= 2:
        pygame.draw.lines(screen, ACCENT, False, points, 2)


# ---------- MAIN LOOP ----------
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            if stake_active:
                if event.key == pygame.K_BACKSPACE:
                    stake_text = stake_text[:-1]
                elif event.key == pygame.K_RETURN:
                    stake_active = False
                elif event.unicode.isdigit():
                    stake_text += event.unicode

        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = event.pos
            if fair_btn.collidepoint(mx, my):
                mode = "fair"
            elif house_btn.collidepoint(mx, my):
                mode = "house"
            elif player_btn.collidepoint(mx, my):
                mode = "player"
            elif stake_box.collidepoint(mx, my):
                stake_active = True
            else:
                stake_active = False

            if head_btn.collidepoint(mx, my):
                choice = "HEAD"
            elif tail_btn.collidepoint(mx, my):
                choice = "TAIL"
            elif flip_btn.collidepoint(mx, my) and not spinning:
                stake = int(stake_text) if stake_text.isdigit() and int(stake_text) > 0 else 0
                if stake == 0:
                    message, message_color = "Enter a valid stake.", LOSE
                elif stake > balance:
                    message, message_color = "Insufficient balance.", LOSE
                else:
                    win, answer = play_round(stake)
                    message = f"Correct! Landed on {answer}. +{stake}" if win else f"Landed on {answer}. -{stake}"
                    message_color = ACCENT2 if win else LOSE
                    spinning = True
                    spin_timer = 12
            elif fast_btn.collidepoint(mx, my):
                stake = int(stake_text) if stake_text.isdigit() and int(stake_text) > 0 else 0
                if stake == 0:
                    message, message_color = "Enter a valid stake.", LOSE
                else:
                    n = 1000
                    while n > 0 and balance >= stake:
                        play_round(stake)
                        n -= 1
                    message, message_color = "Simulated 1,000 rounds (or until balance ran out).", TEXT
            elif reset_btn.collidepoint(mx, my):
                reset()

    if spinning:
        spin_timer -= 1
        if spin_timer <= 0:
            spinning = False

    # ---------- DRAW ----------
    screen.fill(BG)

    title = FONT_BIG.render("See The Odds", True, TEXT)
    screen.blit(title, (20, 15))
    sub_lines = wrap_text("A transparent coin-toss simulator showing the real math behind '50/50' and house-edge games.", FONT_SMALL, WIDTH - 40)
    for i, line in enumerate(sub_lines):
        screen.blit(FONT_SMALL.render(line, True, SUB), (20, 48 + i * 16))

    draw_button(fair_btn, "Fair 50/50", active=(mode == "fair"))
    draw_button(house_btn, "House Edge", active=(mode == "house"))
    draw_button(player_btn, "Player Favored", active=(mode == "player"))

    # mode description
    if mode == "fair":
        desc = "True fair coin. Your true win chance is exactly 50%."
    elif mode == "house":
        desc = f"Realistic house-edge game. True win chance is only {int(HOUSE_WIN_PROB*100)}%, even though it still feels like '50/50.'"
    else:
        desc = f"Player-favored game, for comparison only. True win chance is {int(PLAYER_WIN_PROB*100)}% — no real platform would offer this, since the house would lose money."
    for i, line in enumerate(wrap_text(desc, FONT_SMALL, WIDTH - 40)):
        screen.blit(FONT_SMALL.render(line, True, SUB), (20, 118 + i * 16))

    # stats grid
    gy = 155
    draw_stat(20, gy, 133, round(balance), "BALANCE")
    draw_stat(163, gy, 133, f"{round((wins/rounds)*100) if rounds else '—'}%" if rounds else "—", "WIN RATE")
    draw_stat(306, gy, 134, rounds, "ROUNDS")
    draw_stat(20, gy + 52, 133, wagered, "WAGERED")
    net = balance - STARTING_BALANCE
    draw_stat(163, gy + 52, 133, f"{'+' if net>=0 else ''}{round(net)}", "NET")
    draw_stat(306, gy + 52, 134, f"{int(win_prob()*100)}%", "TRUE WIN CHANCE")

    # warning
    if show_warning:
        warn_rect = pygame.Rect(20, 264, 420, 46)
        pygame.draw.rect(screen, (40, 32, 15), warn_rect, border_radius=8)
        pygame.draw.rect(screen, WARN, warn_rect, 1, border_radius=8)
        wtext = "You raised your stake after losses — a pattern called 'chasing losses.'"
        for i, line in enumerate(wrap_text(wtext, FONT_TINY, 400)):
            screen.blit(FONT_TINY.render(line, True, WARN), (30, 270 + i * 16))

    # coin
    coin_center = (WIDTH // 2, 355)
    coin_radius = 34 if not spinning else int(34 * abs(pygame.math.Vector2(1, 0).rotate((spin_timer * 60) % 360).x)) or 6
    face = last_answer if last_answer and not spinning else choice
    color = ACCENT if face == "HEAD" else ACCENT2
    text_color = (58, 44, 5) if face == "HEAD" else (13, 58, 36)
    pygame.draw.circle(screen, color, coin_center, max(coin_radius, 6))
    pygame.draw.circle(screen, (202, 162, 58), coin_center, max(coin_radius, 6), 3)
    if coin_radius > 15:
        letter = FONT_BOLD.render("H" if face == "HEAD" else "T", True, text_color)
        screen.blit(letter, letter.get_rect(center=coin_center))

    # stake box
    pygame.draw.rect(screen, PANEL, stake_box, border_radius=8)
    pygame.draw.rect(screen, ACCENT if stake_active else LINE, stake_box, 2, border_radius=8)
    screen.blit(FONT_TINY.render("STAKE", True, SUB), (stake_box.x, stake_box.y - 18))
    screen.blit(FONT.render(stake_text if stake_text else "0", True, TEXT), (stake_box.x + 10, stake_box.y + 8))

    draw_button(head_btn, "HEAD", active=(choice == "HEAD"))
    draw_button(tail_btn, "TAIL", active=(choice == "TAIL"))
    draw_button(flip_btn, "Flip once" if not spinning else "Flipping...", primary=True, disabled=spinning)
    draw_button(fast_btn, "Fast-forward 1,000 rounds")
    draw_button(reset_btn, "Reset simulation")

    if message:
        for i, line in enumerate(wrap_text(message, FONT_SMALL, WIDTH - 40)):
            screen.blit(FONT_SMALL.render(line, True, message_color), (20, 648 + i * 16 - 20))

    draw_chart(chart_rect)
    screen.blit(FONT_TINY.render("Balance over time", True, SUB), (20, 644))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()