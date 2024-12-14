import random
import copy


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


def count_inversions(numbers):
    inversions = 0
    for i in range(len(numbers)):
        for j in range(i + 1, len(numbers)):
            if numbers[i] != 0 and numbers[j] != 0 and numbers[i] > numbers[j]:
                inversions += 1
    return inversions


def is_solvable(puzzle):
    numbers = [num for row in puzzle for num in row]

    blank_row = 0
    for i in range(4):
        if 0 in puzzle[i]:
            blank_row = 4 - i
            break

    inversions = count_inversions(numbers)

    return (blank_row % 2 == 0) == (inversions % 2 == 1)


def generate_15_puzzle(seed, reverse_rate=0.2, reverse_steps=15):
    random.seed(seed)
    
    # reverse play to generate ood sample
    if random.random() < reverse_rate:
        numbers = list(range(1, 16)) + [0]  # 0-15
        numbers = [numbers[i : i + 4] for i in range(0, 16, 4)]
        puzzle = Board(numbers)
        for _ in range(reverse_steps):
            # direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
            if puzzle.locate(0) == (0, 0):
                direction = random.choice(["DOWN", "RIGHT"])
            elif puzzle.locate(0) == (0, 3):
                direction = random.choice(["DOWN", "LEFT"])
            elif puzzle.locate(0) == (3, 0):
                direction = random.choice(["UP", "RIGHT"])
            elif puzzle.locate(0) == (3, 3):
                direction = random.choice(["UP", "LEFT"])
            elif puzzle.locate(0)[0] == 0:
                direction = random.choice(["DOWN", "LEFT", "RIGHT"])
            elif puzzle.locate(0)[0] == 3:
                direction = random.choice(["UP", "LEFT", "RIGHT"])
            elif puzzle.locate(0)[1] == 0:
                direction = random.choice(["UP", "DOWN", "RIGHT"])
            elif puzzle.locate(0)[1] == 3:
                direction = random.choice(["UP", "DOWN", "LEFT"])
            else:
                direction = random.choice(["UP", "DOWN", "LEFT", "RIGHT"])
            puzzle.move(direction)
        return puzzle.board

    numbers = list(range(16))  # 0-15
    random.shuffle(numbers)

    puzzle = [numbers[i : i + 4] for i in range(0, 16, 4)]

    if not is_solvable(puzzle):
        pos1 = pos2 = None
        for i in range(4):
            for j in range(4):
                if puzzle[i][j] != 0:
                    if pos1 is None:
                        pos1 = (i, j)
                    elif pos2 is None:
                        pos2 = (i, j)
                        break
            if pos2 is not None:
                break

        puzzle[pos1[0]][pos1[1]], puzzle[pos2[0]][pos2[1]] = puzzle[pos2[0]][pos2[1]], puzzle[pos1[0]][pos1[1]]

    return puzzle


def is_solution(puzzle, moves):
    target = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 0]]

    current = [row[:] for row in puzzle]

    space_row = space_col = None
    for i in range(4):
        for j in range(4):
            if current[i][j] == 0:
                space_row, space_col = i, j
                break
        if space_row is not None:
            break

    directions = {"UP": (-1, 0), "DOWN": (1, 0), "LEFT": (0, -1), "RIGHT": (0, 1)}

    for move in moves:
        if move not in directions:
            return False

        dr, dc = directions[move]
        new_row, new_col = space_row + dr, space_col + dc

        if not (0 <= new_row < 4 and 0 <= new_col < 4):
            return False

        current[space_row][space_col], current[new_row][new_col] = current[new_row][new_col], current[space_row][space_col]

        space_row, space_col = new_row, new_col

    return current == target


if __name__ == '__main__':
    puzzle = generate_15_puzzle(0, 1, 15)
    print(puzzle)