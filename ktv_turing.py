import csv
import time
import sys
import os

# --- Cross-platform key reading block ---
if os.name == 'nt':
    import msvcrt


    def get_key():
        """Returns 'LEFT', 'RIGHT', 'ENTER' or None for Windows"""
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key == b'\r': return 'ENTER'
            # In Windows, arrow keys return a two-part code: 0x00 or 0xE0, then the key code
            if key in (b'\xe0', b'\x00'):
                try:
                    key = msvcrt.getch()
                    if key == b'K': return 'LEFT'
                    if key == b'M': return 'RIGHT'
                except:
                    pass
        return None
else:
    import tty, termios


    def get_key():
        """Returns 'LEFT', 'RIGHT', 'ENTER' or None for Linux/Mac"""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            # Read 1 byte
            ch = sys.stdin.read(1)
            if ch == '\r' or ch == '\n': return 'ENTER'

            # Handle Escape sequences (arrow keys)
            if ch == '\x1b':
                seq = sys.stdin.read(2)
                if seq == '[D': return 'LEFT'
                if seq == '[C': return 'RIGHT'
        except:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return None


# --- Turing Machine Class ---
class TuringMachine:
    def __init__(self, rules, tape_input, start_state, start_pos=0, blank_symbol='_'):
        self.rules = rules
        # Tape: dictionary {index: symbol}
        self.tape = dict(enumerate(tape_input))
        self.blank_symbol = blank_symbol
        self.head_position = start_pos
        self.current_state = start_state
        self.step_counter = 0

    def get_tape_symbol(self):
        return self.tape.get(self.head_position, self.blank_symbol)

    def print_state(self):
        """Output the tape and the head position"""
        self._render(self.head_position, f"Step {self.step_counter} | State: [{self.current_state}]")

    def _render(self, current_head_pos, title=""):
        """Internal rendering function for use in both simulation and setup"""
        if not self.tape:
            min_pos = current_head_pos
            max_pos = current_head_pos
        else:
            positions = list(self.tape.keys()) + [current_head_pos]
            min_pos = min(positions)
            max_pos = max(positions)

        padding = 2
        start_index = min_pos - padding
        end_index = max_pos + padding

        tape_line = ""
        pointer_line = ""

        for i in range(start_index, end_index + 1):
            sym = self.tape.get(i, self.blank_symbol)
            cell_str = f" {sym} "

            if i == current_head_pos:
                pointer_str = " ▼ "
            else:
                pointer_str = "   "

            tape_line += cell_str
            pointer_line += pointer_str

        print(f"\n--- {title} ---")
        print(pointer_line)
        print(tape_line)

    def step(self):
        read_sym = self.get_tape_symbol()
        key = (self.current_state, read_sym)

        if key not in self.rules:
            print(f"\nHALT: No transition for ({self.current_state}, {read_sym})")
            return False

        new_sym, action, new_state = self.rules[key]

        self.tape[self.head_position] = new_sym
        self.current_state = new_state
        self.step_counter += 1

        if action == 'R':
            self.head_position += 1
            return True
        elif action == 'L':
            self.head_position -= 1
            return True
        elif action == 'S':
            print("\nHALT: Stop command (S)")
            return False
        return False

    def run(self, delay=0.5):
        print("\n=== Starting Emulation ===")
        self.print_state()
        while True:
            if not self.step():
                break
            self.print_state()
            time.sleep(delay)


# --- Loading and Setup Functions ---
def load_csv_rules(filepath):
    rules = {}
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File '{filepath}' not found.")

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            raise ValueError("File is empty.")

        alphabet = header[1:]
        for row in reader:
            if not row: continue
            state = row[0].strip()
            commands = row[1:]
            for char_idx, cell in enumerate(commands):
                cell = cell.strip()
                if not cell: continue
                if char_idx >= len(alphabet): continue

                trigger_sym = alphabet[char_idx]
                parts = cell.replace(',', ' ').split()
                if len(parts) == 3:
                    rules[(state, trigger_sym)] = (parts[0], parts[1].upper(), parts[2])
    return rules


def interactive_head_setup(tape_input, blank_symbol):
    """
    Allows the user to move the head left/right before starting.
    """
    # Temporary machine for rendering only
    temp_tm = TuringMachine({}, tape_input, "SETUP", 0, blank_symbol)
    head_pos = 0

    print("\n" * 2)
    print("=== HEAD POSITION SETUP ===")
    print("Use [<-] and [->] keys to move the head.")
    print("Press [ENTER] to confirm position.")
    time.sleep(1)  # Pause to allow reading

    while True:
        # Clear screen (cls for Windows, clear for Unix)
        os.system('cls' if os.name == 'nt' else 'clear')

        print("=== HEAD POSITION SETUP ===")
        print(f"Current position: {head_pos}")
        print("Press [ENTER] to start.")

        # Use _render method to show current position
        temp_tm._render(head_pos, "Select Position")

        # Wait for input (loop to avoid heavy CPU usage)
        while True:
            key = get_key()
            if key:
                break
            time.sleep(0.05)

        if key == 'LEFT':
            head_pos -= 1
        elif key == 'RIGHT':
            head_pos += 1
        elif key == 'ENTER':
            return head_pos


def main():
    # 1. File path input
    if len(sys.argv) > 1:
        config_filename = sys.argv[1]
        with open(config_filename) as config:
            configs = config.readlines()
    else:
        configs = []
        print("No parameter provided")

    while True:
        if len(configs) > 0 and configs[0] != '0':
            csv_path = configs[0].strip()
        else:
            csv_path = input("Enter path to CSV file: ").strip()
        if os.path.exists(csv_path): break
        print("File not found.")

    # 2. Loading
    try:
        rules = load_csv_rules(csv_path)
    except Exception as e:
        print(f"Read error: {e}")
        return

    # 3. Settings
    if len(configs) > 1 and configs[1] != '\n':
        blank = configs[1].strip() or '_'
    else:
        blank = input("Blank cell symbol (Enter = '_'): ").strip() or '_'

    if len(configs) > 2 and configs[2] != '\n':
        start_state = configs[2].strip()
    else:
        start_state = input("Start state: ").strip()

    if len(configs) > 3 and configs[3] != '\n':
        tape_str = configs[3].strip()
    else:
        tape_str = input("Input tape: ").strip()

    if len(configs) > 4 and configs[4] != '\n':
        start_pos = int(configs[4])
    else:
        # 4. INTERACTIVE POSITION SELECTION
        print("Moving to head setup...")
        start_pos = interactive_head_setup(tape_str, blank)

    # 5. Delay
    try:
        if len(configs) > 5 and configs[5] != '\n':
            delay = float(configs[5].strip() or 0.5)
        else:
            delay = float(input("\nDelay (sec, Enter=0.5): ").strip() or 0.5)
    except:
        delay = 0.5

    # 6. Launch
    tm = TuringMachine(rules, tape_str, start_state, start_pos, blank)
    try:
        tm.run(delay)
    except KeyboardInterrupt:
        print("\nInterrupted.")


if __name__ == "__main__":
    main()