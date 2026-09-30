import curses, random, time

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(50)
    sh, sw = stdscr.getmaxyx()
    score = 0
    circles = [{'y': random.randint(1, sh-2), 'x': random.randint(1, sw-2), 'spawn': time.time()}]
    spawn_interval = 1.5
    last_spawn = time.time()
    duration = 2.0

    while True:
        stdscr.clear()
        now = time.time()
        if now - last_spawn > spawn_interval:
            circles.append({'y': random.randint(1, sh-2), 'x': random.randint(1, sw-2), 'spawn': now})
            last_spawn = now
        for c in circles:
            stdscr.addstr(c['y'], c['x'], "O")
        stdscr.addstr(0, 0, f"Score: {score}")
        stdscr.refresh()

        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key != -1:
            for c in circles[:]:
                if key == ord('o'):
                    score += 1
                    circles.remove(c)

        circles = [c for c in circles if now - c['spawn'] < duration]

import curses
curses.wrapper(main)
