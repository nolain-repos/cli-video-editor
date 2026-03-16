import os
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


def get_path_input(prompt, validate=None):
    """Read a file path character by character, validating directories on each '/'."""
    sys.stdout.write(prompt)
    sys.stdout.flush()

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    buf = []

    def redraw(error=""):
        line = "".join(buf)
        sys.stdout.write(f"\r\033[K{prompt}{line}")
        if error:
            sys.stdout.write(f"\033[2m  {error}\033[0m")
            col = len(prompt) + len(line)
            sys.stdout.write(f"\r\033[{col}C")
        sys.stdout.flush()

    def autocomplete():
        path = "".join(buf)
        if not path:
            directory = "."
            prefix = ""
        elif "/" in path:
            parts = path.rsplit("/", 1)
            directory = parts[0] if parts[0] else "/"
            prefix = parts[1] if len(parts) > 1 else ""
        else:
            directory = "."
            prefix = path

        if not os.path.isdir(directory):
            return

        try:
            entries = os.listdir(directory)
            matches = [e for e in entries if e.startswith(prefix)]
            
            if len(matches) == 1:
                completion = matches[0]
                if directory == ".":
                    new_path = completion
                elif directory == "/":
                    new_path = "/" + completion
                else:
                    new_path = directory + "/" + completion
                
                if os.path.isdir(new_path):
                    new_path += "/"
                
                buf.clear()
                buf.extend(list(new_path))
                redraw()
            elif len(matches) > 1:
                common = os.path.commonprefix(matches)
                if len(common) > len(prefix):
                    if directory == ".":
                        new_path = common
                    elif directory == "/":
                        new_path = "/" + common
                    else:
                        new_path = directory + "/" + common
                    buf.clear()
                    buf.extend(list(new_path))
                    redraw()
        except (OSError, PermissionError):
            pass

    try:
        tty.setraw(fd)
        while True:
            ch = sys.stdin.read(1)

            if ch in ("\r", "\n"):
                if validate:
                    error = validate("".join(buf))
                    if error:
                        redraw(error)
                        continue
                redraw()
                sys.stdout.write("\r\n")
                sys.stdout.flush()
                return "".join(buf)
            
            if ch == "\t":
                autocomplete()
                continue

            if ch == "\x03":
                raise KeyboardInterrupt

            if ch in ("\x7f", "\x08"):
                if buf:
                    buf.pop()
                redraw()
                continue

            if ch == "\x1b":
                ch2 = sys.stdin.read(1)
                if ch2 == "[":
                    sys.stdin.read(1)
                continue

            if ch < " ":
                continue

            if ch == "/":
                dir_path = "".join(buf)
                if not dir_path or os.path.isdir(dir_path):
                    buf.append("/")
                    redraw()
                else:
                    redraw("(not a valid directory)")
                continue

            buf.append(ch)
            redraw()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


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


def resolve_input_path(path):
    if not os.path.splitext(path)[1]:
        path += ".mp4"
    if not os.path.dirname(path):
        path = os.path.join(os.getcwd(), path)
    return path


def resolve_output_path(path, input_path):
    if not os.path.splitext(path)[1]:
        path += ".mp4"
    if not os.path.dirname(path):
        input_dir = os.path.dirname(input_path)
        path = os.path.join(input_dir, path)
    return path


def main():
    clear_screen()
    print("  \033[1m=== CLI Video Editor ===\033[0m\n")

    def check_input_exists(raw):
        resolved = resolve_input_path(raw)
        if not os.path.isfile(resolved):
            return "(file not found)"
        return ""

    input_video = resolve_input_path(get_path_input("  Input video path: ", validate=check_input_exists))
    output_video = resolve_output_path(get_path_input("  Output video path: "), input_video)

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
