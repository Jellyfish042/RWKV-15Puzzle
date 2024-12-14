import tkinter as tk
from tkinter import messagebox, font
import random
import time
from threading import Thread
from tools import generate_15_puzzle


random.seed(0)


def dummy_initial_state_generator():
    # return [[15, 0, 2, 12], [14, 7, 11, 8], [1, 5, 3, 4], [6, 13, 10, 9]]
    return generate_15_puzzle(random.randint(0, 1000000))


class ModernFifteenPuzzle:
    def __init__(self, master):
        self.master = master
        self.master.title("15 Puzzle")
        self.master.geometry("900x640")
        self.master.resizable(False, False)

        self.colors = {
            "bg": "#1a1b26",
            "tile": "#7aa2f7",
            "correct": "#9ece6a",
            "empty": "#f7768e",
            "text": "#a9b1d6",
            "button_bg": "#414868",
            "button_hover": "#565f89",
            "tile_text": "#ffffff",
        }

        self.model = DummyModel()
        self.initial_state_generator = dummy_initial_state_generator
        self.correct_positions = {i: i + 1 for i in range(15)}
        self.tiles = list(range(1, 16)) + [None]
        self.moves = 0
        self.time = 0
        self.running = False
        self.buttons = []
        self.timer_id = None
        self.is_model_running = False

        self.manual_control = True
        self.timer_running = False

        self.create_layout()
        self.new_game()

    def create_layout(self):
        self.main_layout = tk.Frame(self.master, bg=self.colors["bg"])
        self.main_layout.pack(expand=True, fill="both")

        self.create_reasoning_display()

        self.game_container = tk.Frame(self.main_layout, bg=self.colors["bg"])
        self.game_container.pack(side="right", expand=True, fill="both", padx=20, pady=20)

        self.create_title()
        self.create_stats_display()
        self.create_game_grid()
        self.create_control_buttons()

    def create_reasoning_display(self):
        self.reasoning_container = tk.Frame(self.main_layout, bg=self.colors["bg"], width=400)
        self.reasoning_container.pack(side="left", fill="both", padx=20, pady=20)
        self.reasoning_container.pack_propagate(False)

        title = tk.Label(self.reasoning_container, text="Reasoning Process", font=font.Font(family="Helvetica", size=16, weight="bold"), bg=self.colors["bg"], fg=self.colors["text"])
        title.pack(pady=(0, 10))

        text_frame = tk.Frame(self.reasoning_container, bg=self.colors["bg"])
        text_frame.pack(expand=True, fill="both")

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side="right", fill="y")

        # self.reasoning_text = tk.Text(text_frame, wrap=tk.WORD, bg=self.colors["button_bg"], fg=self.colors["tile_text"], font=("Consolas", 12), padx=10, pady=10, maxundo=0)
        self.reasoning_text = tk.Text(text_frame, wrap=tk.WORD, bg=self.colors["button_bg"], fg=self.colors["tile_text"], font=("Consolas", 12), padx=10, pady=10, maxundo=0)

        self.reasoning_text.pack(expand=True, fill="both")

        self.reasoning_text.tag_configure("move", foreground="#9ece6a")

        self.reasoning_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.configure(command=self.reasoning_text.yview)

    def create_control_buttons(self):
        self.control_frame = tk.Frame(self.game_container, bg=self.colors["bg"])
        self.control_frame.pack(pady=20)

        buttons_info = [("New Game", self.new_game), ("Start Model", self.start_model)]

        for text, command in buttons_info:
            btn = tk.Button(self.control_frame, text=text, font=font.Font(family="Helvetica", size=12), command=command, bg=self.colors["button_bg"], fg=self.colors["tile_text"], borderwidth=0, padx=15, pady=8)
            btn.pack(side="left", padx=5)

            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg=self.colors["button_hover"]) if b["state"] != "disabled" else None)
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg=self.colors["button_bg"]) if b["state"] != "disabled" else None)

    def start_model(self):
        if not self.is_model_running and self.manual_control:
            self.is_model_running = True
            self.manual_control = False
            self.set_buttons_state("disabled")

            self.reasoning_text.configure(state="normal")
            self.reasoning_text.delete(1.0, tk.END)
            self.reasoning_text.configure(state="disabled")

            def recall(text, move=None):
                def update():
                    self.update_reasoning(text)
                    if move and move != "None":
                        self.make_move(move)

                self.master.after(0, update)

            def run_model():
                try:
                    self.model.solve(self, recall)
                finally:

                    def restore():
                        self.set_buttons_state("normal")
                        self.manual_control = True
                        self.is_model_running = False

                    self.master.after(0, restore)

            Thread(target=run_model, daemon=True).start()

    def new_game(self):
        if self.timer_id:
            self.master.after_cancel(self.timer_id)
            self.timer_id = None

        self.manual_control = True
        self.timer_running = False
        self.time = 0
        self.moves = 0
        self.is_model_running = False

        self.reasoning_text.configure(state="normal")
        self.reasoning_text.delete(1.0, tk.END)
        self.reasoning_text.configure(state="disabled")

        self.tiles = self.flatten_initial_state(self.initial_state_generator())
        self.update_buttons()
        self.update_labels()

        self.manual_control = True
        self.timer_running = True
        self.update_timer()

    def create_title(self):
        title = tk.Label(self.game_container, text="15 PUZZLE", font=font.Font(family="Helvetica", size=24, weight="bold"), bg=self.colors["bg"], fg=self.colors["text"])
        title.pack(pady=(0, 20))

    def create_stats_display(self):
        info_frame = tk.Frame(self.game_container, bg=self.colors["bg"])
        info_frame.pack(fill="x", pady=(0, 20))

        moves_frame = tk.Frame(info_frame, bg=self.colors["bg"])
        moves_frame.pack(side="left", expand=True)

        tk.Label(moves_frame, text="MOVES", font=font.Font(family="Helvetica", size=12), bg=self.colors["bg"], fg=self.colors["text"]).pack()

        self.moves_label = tk.Label(moves_frame, text="0", font=font.Font(family="Helvetica", size=20, weight="bold"), bg=self.colors["bg"], fg=self.colors["text"])
        self.moves_label.pack()

        time_frame = tk.Frame(info_frame, bg=self.colors["bg"])
        time_frame.pack(side="right", expand=True)

        tk.Label(time_frame, text="TIME", font=font.Font(family="Helvetica", size=12), bg=self.colors["bg"], fg=self.colors["text"]).pack()

        self.time_label = tk.Label(time_frame, text="0s", font=font.Font(family="Helvetica", size=20, weight="bold"), bg=self.colors["bg"], fg=self.colors["text"])
        self.time_label.pack()

    def create_game_grid(self):
        self.game_frame = tk.Frame(self.game_container, bg=self.colors["bg"])
        self.game_frame.pack(padx=10, pady=10)

        button_size = 80
        for i in range(4):
            for j in range(4):
                frame = tk.Frame(self.game_frame, width=button_size, height=button_size, bg=self.colors["bg"])
                frame.grid(row=i, column=j, padx=2, pady=2)
                frame.grid_propagate(False)

                button = tk.Button(frame, font=font.Font(family="Helvetica", size=24, weight="bold"), borderwidth=0, command=lambda row=i, col=j: self.button_click(row, col))
                button.place(relwidth=1, relheight=1)

                button.bind("<Enter>", lambda e, btn=button: self.on_hover(btn))
                button.bind("<Leave>", lambda e, btn=button: self.on_leave(btn))

                self.buttons.append(button)

    def update_buttons(self):
        for i in range(16):
            value = self.tiles[i]
            button = self.buttons[i]

            if value is None:
                button.configure(text="", bg=self.colors["empty"], state="disabled")
            else:
                is_correct = value == self.correct_positions.get(i)
                button.configure(text=str(value), bg=self.colors["correct"] if is_correct else self.colors["tile"], fg=self.colors["tile_text"], state="normal")

    def update_timer(self):
        if self.timer_running:
            self.time += 1
            self.update_labels()
            self.timer_id = self.master.after(1000, self.update_timer)

    def update_labels(self):
        self.moves_label.config(text=str(self.moves))
        self.time_label.config(text=f"{self.time}s")

    def button_click(self, row, col):
        if not self.manual_control:
            return

        index = row * 4 + col
        empty_index = self.tiles.index(None)

        if self.is_adjacent(index, empty_index):
            self.tiles[index], self.tiles[empty_index] = self.tiles[empty_index], self.tiles[index]
            self.moves += 1
            self.update_buttons()
            self.update_labels()

            if self.is_solved():
                self.timer_running = False
                self.manual_control = False

    def is_adjacent(self, index1, index2):
        row1, col1 = index1 // 4, index1 % 4
        row2, col2 = index2 // 4, index2 % 4
        return abs(row1 - row2) + abs(col1 - col2) == 1

    def is_solved(self):
        return self.tiles[:-1] == list(range(1, 16)) and self.tiles[-1] is None

    def on_hover(self, button):
        if button["state"] != "disabled":
            current_bg = button["bg"]
            if current_bg == self.colors["tile"]:
                button.configure(bg=self.colors["button_hover"])
            elif current_bg == self.colors["correct"]:
                button.configure(bg="#7fb347")

    def on_leave(self, button):
        if button["state"] != "disabled":
            text = button["text"]
            index = self.buttons.index(button)
            if text and int(text) == self.correct_positions.get(index):
                button.configure(bg=self.colors["correct"])
            else:
                button.configure(bg=self.colors["tile"])

    def update_reasoning(self, text):
        # print(text, end='', flush=True)

        # if text in ["UP ", "DOWN ", "LEFT ", "RIGHT "]:
        #     text += "\n"

        self.reasoning_text.configure(state="normal")

        last_line_start = self.reasoning_text.index("end-1c linestart")
        last_line_end = self.reasoning_text.index("end-1c")
        current_last_line = self.reasoning_text.get(last_line_start, last_line_end)

        self.reasoning_text.insert(tk.END, text)

        # max_lines = 50
        # total_lines = int(self.reasoning_text.index('end-1c').split('.')[0])
        # if total_lines > max_lines:
        #     lines_to_delete = total_lines - max_lines
        #     self.reasoning_text.delete("1.0", f"{lines_to_delete + 1}.0")

        if current_last_line.startswith("> Move") or text.strip().startswith("> Move"):
            print(current_last_line)
            current_line_start = self.reasoning_text.index("end-1c linestart")
            current_line_end = self.reasoning_text.index("end-1c")
            self.reasoning_text.tag_remove("move", current_line_start, current_line_end)
            self.reasoning_text.tag_add("move", current_line_start, current_line_end)

        self.reasoning_text.see(tk.END)

        # last_line = self.reasoning_text.index("end-1c linestart")
        # self.reasoning_text.see(last_line)

        self.reasoning_text.configure(state="disabled")

    def flatten_initial_state(self, initial_state):
        flattened = []
        for row in initial_state:
            for num in row:
                flattened.append(None if num == 0 else num)
        return flattened

    def make_move(self, move):
        empty_index = self.tiles.index(None)
        row, col = empty_index // 4, empty_index % 4

        move_changes = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}

        if move not in move_changes:
            return False

        dx, dy = move_changes[move]
        new_row, new_col = row + dx, col + dy

        if 0 <= new_row < 4 and 0 <= new_col < 4:
            new_index = new_row * 4 + new_col
            self.tiles[empty_index], self.tiles[new_index] = self.tiles[new_index], self.tiles[empty_index]
            self.moves += 1
            self.update_buttons()
            self.update_labels()

            self.check_completion()
            return True

        return False

    def button_click(self, row, col):
        if not self.manual_control:
            return

        index = row * 4 + col
        empty_index = self.tiles.index(None)

        if self.is_adjacent(index, empty_index):
            self.tiles[index], self.tiles[empty_index] = self.tiles[empty_index], self.tiles[index]
            self.moves += 1
            self.update_buttons()
            self.update_labels()

            self.check_completion()

    def set_buttons_state(self, state):
        for button in self.buttons:
            if button["text"]:
                button.configure(state=state)

        for widget in self.control_frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(state=state)

    def check_completion(self):
        if self.is_solved():
            self.timer_running = False
            if self.timer_id:
                self.master.after_cancel(self.timer_id)
                self.timer_id = None

            self.manual_control = False
            self.is_model_running = False

            # messagebox.showinfo("Puzzle Solved!", f"\nMoves: {self.moves}\nTime: {self.time} seconds")

            return True
        return False


class DummyModel:
    def __init__(self):
        import os

        os.environ["RWKV_JIT_ON"] = "1"
        os.environ["RWKV_CUDA_ON"] = "0"

        from rwkv_model import RWKV
        from rwkv.utils import PIPELINE, PIPELINE_ARGS
        from rwkv.rwkv_tokenizer import TRIE_TOKENIZER

        self.model = RWKV(model=MODEL_PATH, strategy="cuda fp16", verbose=False)
        self.pipeline = PIPELINE(self.model, "rwkv_vocab_v20230424")
        self.pipeline.tokenizer = TRIE_TOKENIZER("puzzle15_vocab.txt")
        self.gen_args = PIPELINE_ARGS(top_k=1, alpha_frequency=0, alpha_presence=0, token_stop=[59])

        self.model.forward([0, 1], None)

        self.ui_callback = None
        self.history = ""

    def my_callback(self, text):
        # print(text, end='', flush=True)
        # if text in ['UP ', 'DOWN ', 'RIGHT ', 'LEFT ']:
        #     print('rrr', text)
        #     time.sleep(0.02)
        self.history += text
        if text.endswith("\n"):
            lines = self.history.strip().split("\n")
            last_line = lines[-1]
            if last_line.startswith("> Move"):
                # print(last_line)
                move = last_line.split(" ")[-1].strip()
                self.ui_callback(text, move)
                self.history = ""
                return
            self.history = ""
        self.ui_callback(text, "None")

    def solve(self, puzzle, recall):
        self.ui_callback = recall
        self.history = ""
        # prepare input
        board = [x if x else 0 for x in puzzle.tiles]
        board = [board[i : i + 4] for i in range(0, 16, 4)]
        formatted_rows = []
        for row in board:
            formatted_row = [str(num).ljust(3) for num in row]
            formatted_rows.append("".join(formatted_row))
        input_str = "<input>\n<board>\n" + "\n".join(formatted_rows) + "\n</board>\n</input>\n"
        print(input_str)
        self.ui_callback(input_str, "None")

        # generate solution
        self.pipeline.generate(input_str, token_count=100000, args=self.gen_args, callback=self.my_callback)


def main():
    root = tk.Tk()
    root.configure(bg="#1a1b26")
    game = ModernFifteenPuzzle(root)
    root.mainloop()


if __name__ == "__main__":
    
    MODEL_PATH = 'rwkv_15puzzle_20241214.pth'
    
    main()
