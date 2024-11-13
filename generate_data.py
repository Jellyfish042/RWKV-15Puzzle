from collections import deque
from logger import DataLogger
import random
import copy
from tools import *
from tqdm import tqdm
import json
import multiprocessing as mp
import os
from functools import partial


class Board:
    def __init__(self, board):
        self.board = copy.deepcopy(board)

    def __eq__(self, other):
        return self.board == other.board

    def __str__(self):
        formatted_rows = []
        for row in self.board:
            # formatted_row = [str(num).rjust(2) for num in row]
            formatted_row = [str(num).ljust(3) for num in row]
            formatted_rows.append("".join(formatted_row))
        return "<board>\n" + "\n".join(formatted_rows) + "\n</board>"
        # return "<board>\n" + "\n".join(" ".join(str(cell) for cell in row) for row in self.board) + "\n</board>"

    def locate(self, number):
        for i in range(4):
            for j in range(4):
                if self.board[i][j] == number:
                    return (i, j)

    def move(self, direction):
        direction = direction.lower()
        i, j = self.locate(0)
        if direction == "up":
            self.board[i][j], self.board[i - 1][j] = self.board[i - 1][j], self.board[i][j]
        elif direction == "down":
            self.board[i][j], self.board[i + 1][j] = self.board[i + 1][j], self.board[i][j]
        elif direction == "left":
            self.board[i][j], self.board[i][j - 1] = self.board[i][j - 1], self.board[i][j]
        elif direction == "right":
            self.board[i][j], self.board[i][j + 1] = self.board[i][j + 1], self.board[i][j]
        else:
            raise ValueError("Invalid direction")


def generate_path(start, end):
    """
    Generate a path from start to end point on a 4x4 board
    Moving pattern: alternates between horizontal and vertical movements

    Args:
        start: Starting coordinate tuple (x, y) where:
               x represents row (0-3 from top to bottom)
               y represents column (0-3 from left to right)
        end: Ending coordinate tuple (x, y)
    Returns:
        Tuple of (coordinate path, direction path)
    """
    coord_path = [start]
    direction_path = []
    current = list(start)
    move_horizontal = True

    while tuple(current) != end:
        dx = end[0] - current[0]  # vertical distance to target (row difference)
        dy = end[1] - current[1]  # horizontal distance to target (column difference)

        # If both directions need movement
        if dx != 0 and dy != 0:
            if move_horizontal:
                # Move left/right
                if dy > 0:
                    current[1] += 1
                    direction_path.append("RIGHT")
                else:
                    current[1] -= 1
                    direction_path.append("LEFT")
                move_horizontal = False
            else:
                # Move up/down
                if dx > 0:
                    current[0] += 1
                    direction_path.append("DOWN")
                else:
                    current[0] -= 1
                    direction_path.append("UP")
                move_horizontal = True
        # If only one direction needs movement
        elif dy != 0:  # only horizontal movement needed
            if dy > 0:
                current[1] += 1
                direction_path.append("RIGHT")
            else:
                current[1] -= 1
                direction_path.append("LEFT")
        elif dx != 0:  # only vertical movement needed
            if dx > 0:
                current[0] += 1
                direction_path.append("DOWN")
            else:
                current[0] -= 1
                direction_path.append("UP")

        coord_path.append(tuple(current))

    return coord_path, direction_path


def find_shortest_path(start, end, mask):
    """
    Find shortest path from start to end point and return both directions and coordinates

    Args:
        start: Starting coordinate tuple (x, y)
        end: Ending coordinate tuple (x, y)
        mask: 4x4 tuple of tuples containing boolean values
             True for passable positions, False for obstacles
    Returns:
        Tuple of (directions_list, coordinates_list) where:
        - directions_list: List of directions (UP, DOWN, LEFT, RIGHT)
        - coordinates_list: List of coordinate tuples (x, y) including start and end
        Returns (None, None) if no path exists
    """
    if not mask[start[0]][start[1]] or not mask[end[0]][end[1]]:
        return None, None

    moves = {(0, 1): "RIGHT", (0, -1): "LEFT", (1, 0): "DOWN", (-1, 0): "UP"}

    # Store position, directions, and path coordinates
    queue = deque([(start, [], [start])])
    visited = {start}

    while queue:
        (current_x, current_y), directions, coords = queue.popleft()

        if (current_x, current_y) == end:
            return directions, coords

        for (dx, dy), direction in moves.items():
            next_x, next_y = current_x + dx, current_y + dy
            next_pos = (next_x, next_y)

            if 0 <= next_x < 4 and 0 <= next_y < 4 and mask[next_x][next_y] and next_pos not in visited:

                queue.append((next_pos, directions + [direction], coords + [next_pos]))
                visited.add(next_pos)

    return None, None


def create_current_mask(original_mask, banned_position):
    new_mask = [list(row) for row in original_mask]
    new_mask[banned_position[0]][banned_position[1]] = False
    return tuple(tuple(row) for row in new_mask)


def format_path(path):
    return " ".join(path) + " "


def format_coords(coords):
    return " ".join(str(x) for x in coords) + " "


def solve(board, logger):

    logger.print_and_log(f"<input>\n{str(board)}\n</input>\n")
    logger.print_and_log("<reasoning>")

    all_steps = []
    for step in STEPS:

        logger.print_and_log(step)

        if "Move" in step:

            target_number = int(step.split(" ")[-4])
            number_position = board.locate(target_number)
            logger.print_and_log(f"=> Check position: {number_position} ")
            if number_position == NUMBER_TARGET[target_number]:
                logger.print_and_log("[Number is in place, skip]")
                continue
            logger.print_and_log("[Number is not in place]")

            # may need to use fomula
            if step == "### Step 4: Move 3 to (1, 2)":
                logger.print_and_log("=> Check for special case")
                if board.locate(3) == (0, 3) or (board.locate(0) == (0, 3) and board.locate(3) == (1, 3)):
                    logger.print_and_log("[Special case (A)]")
                    logger.print_and_log("=> Move blank to (1, 1) ")
                    mask = ((False, False, False, True), (True, True, True, True), (True, True, True, True), (True, True, True, True))
                    blank_path, _ = find_shortest_path(board.locate(0), (1, 1), mask)
                    for blank_direction in blank_path:
                        board.move(blank_direction)
                        logger.print_and_log(f"> Move {blank_direction} ")
                        logger.print_and_log(str(board))
                    all_steps += blank_path
                    logger.print_and_log("=> Use formula A: UP RIGHT RIGHT DOWN LEFT UP LEFT DOWN ")
                    for direction in FORMULA_A:
                        board.move(direction)
                        logger.print_and_log(f"> Move {direction} ")
                        logger.print_and_log(str(board))
                    all_steps += FORMULA_A
                    logger.print_and_log(f"Path taken so far: {format_path(all_steps)}\n")
                    continue
                else:
                    logger.print_and_log("[Not special case]")
            elif step == "### Step 9: Move 7 to (2, 2)":
                logger.print_and_log("=> Check for special case")
                if board.locate(7) == (1, 3) or (board.locate(0) == (1, 3) and board.locate(7) == (2, 3)):
                    logger.print_and_log("[Special case (A)]")
                    logger.print_and_log("=> Move blank to (2, 1) ")
                    mask = ((False, False, False, False), (False, False, False, True), (True, True, True, True), (True, True, True, True))
                    blank_path, _ = find_shortest_path(board.locate(0), (2, 1), mask)
                    for blank_direction in blank_path:
                        board.move(blank_direction)
                        logger.print_and_log(f"> Move {blank_direction} ")
                        logger.print_and_log(str(board))
                    all_steps += blank_path
                    logger.print_and_log("=> Use formula A: UP RIGHT RIGHT DOWN LEFT UP LEFT DOWN ")
                    for direction in FORMULA_A:
                        board.move(direction)
                        logger.print_and_log(f"> Move {direction} ")
                        logger.print_and_log(str(board))
                    all_steps += FORMULA_A
                    logger.print_and_log(f"Path taken so far: {format_path(all_steps)}\n")
                    continue
                else:
                    logger.print_and_log("[Not special case]")
            elif step == "### Step 12: Move 9 to (2, 1)":
                logger.print_and_log("=> Check for special case")
                if board.locate(9) == (3, 0) or (board.locate(0) == (3, 0) and board.locate(9) == (3, 1)):
                    logger.print_and_log("[Special case (B)]")
                    logger.print_and_log("=> Move blank to (3, 0) ")
                    mask = ((False, False, False, False), (False, False, False, False), (False, True, True, True), (True, True, True, True))
                    blank_path, _ = find_shortest_path(board.locate(0), (3, 0), mask)
                    for blank_direction in blank_path:
                        board.move(blank_direction)
                        logger.print_and_log(f"> Move {blank_direction} ")
                        logger.print_and_log(str(board))
                    all_steps += blank_path
                    logger.print_and_log("=> Use formula B: UP RIGHT DOWN RIGHT UP LEFT LEFT DOWN RIGHT UP RIGHT ")
                    for direction in FORMULA_B:
                        board.move(direction)
                        logger.print_and_log(f"> Move {direction} ")
                        logger.print_and_log(str(board))
                    all_steps += FORMULA_B
                    logger.print_and_log(f"Path taken so far: {format_path(all_steps)}\n")
                    continue
                else:
                    logger.print_and_log("[Not special case]")
            elif step == "### Step 15: Move 10 to (2, 2)":
                logger.print_and_log("=> Check for special case")
                if board.locate(10) == (3, 1) or (board.locate(0) == (3, 1) and board.locate(10) == (3, 2)):
                    logger.print_and_log("[Special case (B)]")
                    logger.print_and_log("=> Move blank to (3, 1) ")
                    mask = ((False, False, False, False), (False, False, False, False), (False, False, True, True), (False, True, True, True))
                    blank_path, _ = find_shortest_path(board.locate(0), (3, 1), mask)
                    for blank_direction in blank_path:
                        board.move(blank_direction)
                        logger.print_and_log(f"> Move {blank_direction} ")
                        logger.print_and_log(str(board))
                    all_steps += blank_path
                    logger.print_and_log("=> Use formula B: UP RIGHT DOWN RIGHT UP LEFT LEFT DOWN RIGHT UP RIGHT ")
                    for direction in FORMULA_B:
                        board.move(direction)
                        logger.print_and_log(f"> Move {direction} ")
                        logger.print_and_log(str(board))
                    all_steps += FORMULA_B
                    logger.print_and_log(f"Path taken so far: {format_path(all_steps)}\n")
                    continue
                else:
                    logger.print_and_log("[Not special case]")

            # coord_path, direction_path = generate_path(board.locate(target_number), NUMBER_TARGET[target_number])
            direction_path, coord_path = find_shortest_path(board.locate(target_number), NUMBER_TARGET[target_number], MASK[step])
            coord_path = coord_path[1:]
            logger.print_and_log(f"=> Planned path: {format_coords(coord_path)}")
            for direction, target_position in zip(direction_path, coord_path):
                logger.print_and_log(f"=> Move blank to {target_position} ")
                current_blank_position = board.locate(0)
                mask = create_current_mask(MASK[step], board.locate(target_number))  # avoid changing the number's position
                blank_path, _ = find_shortest_path(current_blank_position, target_position, mask)
                # only for debugging
                # if blank_path is None:
                #     print(board, mask, current_blank_position, target_position, target_number)
                for blank_direction in blank_path:
                    board.move(blank_direction)
                    logger.print_and_log(f"> Move {blank_direction} ")
                    logger.print_and_log(str(board))
                all_steps += blank_path

                logger.print_and_log("# Adjust number position")
                board.move(REVERSE_DIRECTION[direction])
                logger.print_and_log(f"> Move {REVERSE_DIRECTION[direction]} ")
                logger.print_and_log(str(board))
                all_steps.append(REVERSE_DIRECTION[direction])

        elif "Place" in step:
            if step == "### Step 5: Place 3 and 4 in correct position":
                logger.print_and_log("=> Move blank to (0, 3) ")
                mask = ((False, False, False, True), (True, True, False, True), (True, True, True, True), (True, True, True, True))
                blank_path, _ = find_shortest_path(board.locate(0), (0, 3), mask)
                for blank_direction in blank_path:
                    board.move(blank_direction)
                    logger.print_and_log(f"> Move {blank_direction} ")
                    logger.print_and_log(str(board))
                all_steps += blank_path
                logger.print_and_log("=> Place 3 and 4 in correct position")
                for blank_direction in ["LEFT", "DOWN"]:
                    board.move(blank_direction)
                    logger.print_and_log(f"> Move {blank_direction} ")
                    logger.print_and_log(str(board))
                all_steps += ["LEFT", "DOWN"]
            elif step == "### Step 10: Place 7 and 8 in correct position":
                logger.print_and_log("=> Move blank to (1, 3) ")
                mask = ((False, False, False, False), (False, False, False, True), (True, True, False, True), (True, True, True, True))
                blank_path, _ = find_shortest_path(board.locate(0), (1, 3), mask)
                for blank_direction in blank_path:
                    board.move(blank_direction)
                    logger.print_and_log(f"> Move {blank_direction} ")
                    logger.print_and_log(str(board))
                all_steps += blank_path
                logger.print_and_log("=> Place 7 and 8 in correct position")
                for blank_direction in ["LEFT", "DOWN"]:
                    board.move(blank_direction)
                    logger.print_and_log(f"> Move {blank_direction} ")
                    logger.print_and_log(str(board))
                all_steps += ["LEFT", "DOWN"]
            elif step == "### Step 13: Place 9 and 13 in correct position":
                logger.print_and_log("=> Move blank to (3, 0) ")
                mask = ((False, False, False, False), (False, False, False, False), (False, False, True, True), (True, True, True, True))
                blank_path, _ = find_shortest_path(board.locate(0), (3, 0), mask)
                for blank_direction in blank_path:
                    board.move(blank_direction)
                    logger.print_and_log(f"> Move {blank_direction} ")
                    logger.print_and_log(str(board))
                all_steps += blank_path
                logger.print_and_log("=> Place 9 and 13 in correct position")
                for blank_direction in ["UP", "RIGHT"]:
                    board.move(blank_direction)
                    logger.print_and_log(f"> Move {blank_direction} ")
                    logger.print_and_log(str(board))
                all_steps += ["UP", "RIGHT"]
            elif step == "### Step 16: Place 10 and 14 in correct position":
                logger.print_and_log("=> Move blank to (3, 1) ")
                mask = ((False, False, False, False), (False, False, False, False), (False, False, False, True), (False, True, True, True))
                blank_path, _ = find_shortest_path(board.locate(0), (3, 1), mask)
                for blank_direction in blank_path:
                    board.move(blank_direction)
                    logger.print_and_log(f"> Move {blank_direction} ")
                    logger.print_and_log(str(board))
                all_steps += blank_path
                logger.print_and_log("=> Place 10 and 14 in correct position")
                for blank_direction in ["UP", "RIGHT"]:
                    board.move(blank_direction)
                    logger.print_and_log(f"> Move {blank_direction} ")
                    logger.print_and_log(str(board))
                all_steps += ["UP", "RIGHT"]

        else:  # finetune 11, 12, 15
            final_positions = (board.board[2][2], board.board[2][3], board.board[3][2], board.board[3][3])
            path = FINETUNE_PATH[final_positions]
            all_steps += path
            for direction in path:
                board.move(direction)
                logger.print_and_log(f"> Move {direction} ")
                logger.print_and_log(str(board))
            logger.print_and_log("[Finetune complete]")

        logger.print_and_log(f"Path taken so far: {format_path(all_steps)}")

    logger.print_and_log("</reasoning>\n")
    logger.print_and_log(f"<output>\n{format_path(all_steps)}\n</output>\n")

    return all_steps


TARGET_BOARD = Board([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]])
NUMBER_TARGET = {
    1: (0, 0),
    2: (0, 1),
    3: (1, 2),
    4: (0, 2),
    5: (1, 0),
    6: (1, 1),
    7: (2, 2),
    8: (1, 2),
    9: (2, 1),
    13: (2, 0),
    10: (2, 2),
    14: (2, 1),
}
STEPS = [
    "### Step 1: Move 1 to (0, 0)",
    "### Step 2: Move 2 to (0, 1)",
    "### Step 3: Move 4 to (0, 2)",
    "### Step 4: Move 3 to (1, 2)",
    "### Step 5: Place 3 and 4 in correct position",
    "### Step 6: Move 5 to (1, 0)",
    "### Step 7: Move 6 to (1, 1)",
    "### Step 8: Move 8 to (1, 2)",
    "### Step 9: Move 7 to (2, 2)",
    "### Step 10: Place 7 and 8 in correct position",
    "### Step 11: Move 13 to (2, 0)",
    "### Step 12: Move 9 to (2, 1)",
    "### Step 13: Place 9 and 13 in correct position",
    "### Step 14: Move 14 to (2, 1)",
    "### Step 15: Move 10 to (2, 2)",
    "### Step 16: Place 10 and 14 in correct position",
    "### Step 17: finetune 11, 12, 15",
]
MASK = {
    "### Step 1: Move 1 to (0, 0)": ((True, True, True, True), (True, True, True, True), (True, True, True, True), (True, True, True, True)),
    "### Step 2: Move 2 to (0, 1)": ((False, True, True, True), (True, True, True, True), (True, True, True, True), (True, True, True, True)),
    "### Step 3: Move 4 to (0, 2)": ((False, False, True, True), (True, True, True, True), (True, True, True, True), (True, True, True, True)),
    "### Step 4: Move 3 to (1, 2)": ((False, False, False, True), (True, True, True, True), (True, True, True, True), (True, True, True, True)),
    "### Step 6: Move 5 to (1, 0)": ((False, False, False, False), (True, True, True, True), (True, True, True, True), (True, True, True, True)),
    "### Step 7: Move 6 to (1, 1)": ((False, False, False, False), (False, True, True, True), (True, True, True, True), (True, True, True, True)),
    "### Step 8: Move 8 to (1, 2)": ((False, False, False, False), (False, False, True, True), (True, True, True, True), (True, True, True, True)),
    "### Step 9: Move 7 to (2, 2)": ((False, False, False, False), (False, False, False, True), (True, True, True, True), (True, True, True, True)),
    "### Step 11: Move 13 to (2, 0)": ((False, False, False, False), (False, False, False, False), (True, True, True, True), (True, True, True, True)),
    "### Step 12: Move 9 to (2, 1)": ((False, False, False, False), (False, False, False, False), (False, True, True, True), (True, True, True, True)),
    "### Step 14: Move 14 to (2, 1)": ((False, False, False, False), (False, False, False, False), (False, True, True, True), (False, True, True, True)),
    "### Step 15: Move 10 to (2, 2)": ((False, False, False, False), (False, False, False, False), (False, False, True, True), (False, True, True, True)),
}
REVERSE_DIRECTION = {"UP": "DOWN", "DOWN": "UP", "LEFT": "RIGHT", "RIGHT": "LEFT"}
FORMULA_A = ["UP", "RIGHT", "RIGHT", "DOWN", "LEFT", "UP", "LEFT", "DOWN"]
FORMULA_B = ["UP", "RIGHT", "DOWN", "RIGHT", "UP", "LEFT", "LEFT", "DOWN", "RIGHT", "UP", "RIGHT"]
FINETUNE_PATH = {
    (0, 11, 15, 12): ["RIGHT", "DOWN"],
    (0, 12, 11, 15): ["DOWN", "RIGHT"],
    (0, 15, 12, 11): ["RIGHT", "DOWN", "LEFT", "UP", "RIGHT", "DOWN"],
    (11, 0, 15, 12): ["DOWN"],
    (11, 12, 0, 15): ["RIGHT"],
    (11, 12, 15, 0): [],
    (12, 0, 11, 15): ["LEFT", "DOWN", "RIGHT"],
    (12, 15, 0, 11): ["RIGHT", "UP", "LEFT", "DOWN", "RIGHT"],
    (12, 15, 11, 0): ["UP", "LEFT", "DOWN", "RIGHT"],
    (15, 0, 12, 11): ["DOWN", "LEFT", "UP", "RIGHT", "DOWN"],
    (15, 11, 0, 12): ["UP", "RIGHT", "DOWN"],
    (15, 11, 12, 0): ["LEFT", "UP", "RIGHT", "DOWN"],
}


def generate_single(seed):
    puzzle_lst = generate_15_puzzle(seed)
    board = Board(puzzle_lst)
    logger = DataLogger(False)
    solution = solve(board=board, logger=logger)
    if is_solution(puzzle_lst, solution):
        return logger.log
    else:
        raise ValueError("Solution is incorrect")


def worker_function(worker_id, base_seed):
    seed = base_seed + worker_id
    result = generate_single(seed=seed)
    return result


def stream_save_result(result, file_path):
    with open(file_path, "a", encoding="utf-8") as f:
        json_line = json.dumps({"text": result}, ensure_ascii=False)
        f.write(json_line + "\n")


def parallel_generate(sample_count, base_seed, output_file, num_processes=None):
    if os.path.exists(output_file):
        os.remove(output_file)

    if num_processes is None:
        num_processes = mp.cpu_count()

    pool = mp.Pool(processes=num_processes)

    worker = partial(worker_function, base_seed=base_seed)

    with tqdm(total=sample_count) as pbar:
        for i, result in enumerate(pool.imap_unordered(worker, range(sample_count))):
            stream_save_result(result, output_file)
            pbar.update(1)

    pool.close()
    pool.join()


if __name__ == "__main__":

    # for seed in tqdm(range(10000)):

    #     logger = DataLogger(print_to_console=False)

    #     puzzle_lst = generate_15_puzzle(seed)
    #     board = Board(puzzle_lst)

    #     solution = solve(board=board, logger=logger)

    #     # print(puzzle_lst)
    #     if not is_solution(puzzle_lst, solution):
    #         print("Solution is incorrect!")
    #         break

    SAMPLE_COUNT = 100
    SEED = 42
    OUTPUT_FILE = "puzzle_data.jsonl"

    parallel_generate(sample_count=SAMPLE_COUNT, base_seed=SEED, output_file=OUTPUT_FILE)
