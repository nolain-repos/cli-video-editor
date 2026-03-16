import sys
import tty
import termios

from veditor import VideoEditor


ACTIONS = ["Zoom", "Mute", "Spatial Crop", "Time Crop"]


def read_key():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == "\x1b":
            ch2 = sys.stdin.read(1)
            if ch2 == "[":
                ch3 = sys.stdin.read(1)
                if ch3 == "A":
                    return "up"
                if ch3 == "B":
                    return "down"
            return "escape"
        if ch in ("\r", "\n"):
            return "enter"
        if ch == "\x03":
            raise KeyboardInterrupt
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


def clear_screen():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def show_menu(title, options, header=""):
    selected = 0
    while True:
        clear_screen()
        if header:
            print(header)
        print(f"  \033[1m{title}\033[0m\n")
        for i, option in enumerate(options):
            if i == selected:
                print(f"  \033[7m > {option} \033[0m")
            else:
                print(f"    {option}")
        print("\n  \033[2m↑/↓ Navigate · Enter Select\033[0m")

        key = read_key()
        if key == "up":
            selected = (selected - 1) % len(options)
        elif key == "down":
            selected = (selected + 1) % len(options)
        elif key == "enter":
            return selected


def get_input(prompt, type_fn=float, optional=False):
    while True:
        raw = input(prompt)
        if optional and raw.strip() == "":
            return None
        try:
            return type_fn(raw.strip())
        except (ValueError, TypeError):
            print(f"  Invalid input, expected {type_fn.__name__}.")


def format_action(action):
    name, params = action
    parts = ", ".join(f"{k}={v}" for k, v in params.items() if v is not None)
    labels = {
        "zoom": "Zoom",
        "mute": "Mute",
        "spatial_crop": "Spatial Crop",
        "time_crop": "Time Crop",
    }
    return f"{labels[name]}({parts})"


def build_header(actions):
    if not actions:
        return "  \033[2mNo actions queued yet.\033[0m\n"
    lines = ["  \033[1mQueued actions:\033[0m"]
    for i, a in enumerate(actions, 1):
        lines.append(f"    {i}. {format_action(a)}")
    lines.append("")
    return "\n".join(lines)


def configure_zoom():
    clear_screen()
    print("  \033[1mConfigure Zoom\033[0m\n")
    tstart = get_input("  Start time (s): ")
    tend = get_input("  End time (s): ")
    w = get_input("  Horizontal center (0.0–1.0): ")
    h = get_input("  Vertical center (0.0–1.0): ")
    zoom_factor = get_input("  Zoom factor: ")
    return ("zoom", {
        "tstart": tstart, "tend": tend,
        "w": w, "h": h, "zoom_factor": zoom_factor,
    })


def configure_mute():
    clear_screen()
    print("  \033[1mConfigure Mute\033[0m\n")
    print("  \033[2mLeave empty for video start/end.\033[0m\n")
    tstart = get_input("  Start time (s): ", optional=True)
    tend = get_input("  End time (s): ", optional=True)
    return ("mute", {"tstart": tstart, "tend": tend})


def configure_spatial_crop():
    clear_screen()
    print("  \033[1mConfigure Spatial Crop\033[0m\n")
    x1 = get_input("  Left boundary (px): ", int)
    y1 = get_input("  Top boundary (px): ", int)
    x2 = get_input("  Right boundary (px): ", int)
    y2 = get_input("  Bottom boundary (px): ", int)
    return ("spatial_crop", {"x1": x1, "y1": y1, "x2": x2, "y2": y2})


def configure_time_crop():
    clear_screen()
    print("  \033[1mConfigure Time Crop\033[0m\n")
    tstart = get_input("  Start time (s): ")
    tend = get_input("  End time (s): ")
    return ("time_crop", {"tstart": tstart, "tend": tend})


CONFIGURATORS = [configure_zoom, configure_mute, configure_spatial_crop, configure_time_crop]


def action_pool_menu(actions):
    options = ACTIONS + ["← Back"]
    header = build_header(actions)
    idx = show_menu("Add Action", options, header=header)
    if idx == len(ACTIONS):
        return None
    return CONFIGURATORS[idx]()


def apply_actions(actions, input_video, output_video):
    editor = VideoEditor()
    for name, params in actions:
        if name == "zoom":
            editor.add_zoom(**params)
        elif name == "mute":
            editor.add_mute(**params)
        elif name == "spatial_crop":
            editor.add_spatial_crop(**params)
        elif name == "time_crop":
            editor.add_time_crop(**params)

    print(f"  {input_video} → {output_video}\n")
    editor.run(input_video, output_video)
    print("\n  Done.")


def main():
    clear_screen()
    print("  \033[1m=== CLI Video Editor ===\033[0m\n")
    input_video = input("  Input video path: ").strip()
    output_video = input("  Output video path: ").strip()

    actions = []

    while True:
        header = build_header(actions)
        idx = show_menu("Main Menu", ["Add Action", "Finish Editing", "Exit"], header=header)

        if idx == 2:
            clear_screen()
            print("  Exited.")
            return

        if idx == 0:
            result = action_pool_menu(actions)
            if result is not None:
                actions.append(result)

        elif idx == 1:
            if not actions:
                continue
            clear_screen()
            print("  \033[1mProcessing…\033[0m\n")
            apply_actions(actions, input_video, output_video)
            return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        clear_screen()
        print("  Interrupted.")
