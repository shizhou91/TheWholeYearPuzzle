from typing import List, Tuple, Dict, Set
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# ----------------------------
# Board definition
# ----------------------------

WIDTH = 7
HEIGHT = 7

FIXED_BLOCKED = {
    (0, 6), (1, 6),
    (6, 0), (6, 1), (6, 5), (6, 6)
}

# ----------------------------
# Pieces (NO FLIP, ROTATION ONLY)
# ----------------------------

PIECES = {
    "SQ": [(0, 0), (0, 1), (1, 0), (1, 1)],
    "CR": [(0, 1), (1, 0), (1, 1), (1, 2), (2, 1)],  # fixed cross
    "SZ": [(0, 0), (0, 1), (1, 1), (1, 2)],
    "TT": [(0, 0), (0, 1), (0, 2), (1, 1)],
    "NN": [(0, 0), (0, 1), (0, 2), (1, 0), (1, 2)],
    "LZ": [(0, 0), (0, 1), (1, 1), (2, 1), (2, 2)],
    "BB": [(0, 0), (1, 0), (1, 1), (2, 0), (2, 1)],
    "SL": [(0, 1), (1, 1), (2, 0), (2, 1)],
    "LL": [(0, 1), (1, 1), (2, 1), (3, 0), (3, 1)],
}

# ----------------------------
# Geometry helpers
# ----------------------------

def rotate(shape: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
    return [(y, -x) for x, y in shape]

def normalize(shape: List[Tuple[int, int]]) -> Tuple[Tuple[int, int], ...]:
    min_x = min(x for x, _ in shape)
    min_y = min(y for _, y in shape)
    return tuple(sorted((x - min_x, y - min_y) for x, y in shape))

def all_rotations(shape: List[Tuple[int, int]]) -> Set[Tuple[Tuple[int, int], ...]]:
    result = set()
    cur = shape
    for _ in range(4):
        result.add(normalize(cur))
        cur = rotate(cur)
    return result

# ----------------------------
# Date → blocked cells
# ----------------------------

def get_date_blocked(month: int, day: int) -> Set[Tuple[int, int]]:
    blocked = set(FIXED_BLOCKED)

    # Months: 2 x 6 (rows 0,1)
    month -= 1
    blocked.add((month // 6, month % 6))

    # Days: rows 2–6, 7 columns (offset by +2 to match actual calendar layout)
    day -= 1
    blocked.add((2 + day // 7, (day % 7 + 2) % 7))

    # Subtract the fixed blocked cells that month/day would overlap with
    # (FIXED_BLOCKED already covers bottom-right corner pairs)
    month_cell = ((month // 6), (month % 6))
    day_cell = (2 + day // 7, day % 7)

    return blocked

# ----------------------------
# Solver
# ----------------------------

def solve(board, empty, pieces_left, placements) -> bool:
    if not empty:
        return True

    anchor = min(empty)

    for piece in list(pieces_left):
        for cells in placements[piece]:
            if anchor not in cells:
                continue
            if cells <= empty:
                for c in cells:
                    board[c] = piece
                empty.difference_update(cells)
                pieces_left.remove(piece)

                if solve(board, empty, pieces_left, placements):
                    return True

                for c in cells:
                    board[c] = "."
                empty.update(cells)
                pieces_left.add(piece)

    return False
  


def render_png(board, month: int, day: int, filename: str):
    fig, ax = plt.subplots(figsize=(7, 7))

    COLORS = {
        "SQ": "#FFD966",
        "CR": "#FF6666",
        "SZ": "#66CCFF",
        "TT": "#99FF99",
        "NN": "#FFB266",
        "LZ": "#CC99FF",
        "BB": "#FF99CC",
        "SL": "#66FFCC",
        "LL": "#C0C0C0",
        "##": "#333333",
    }

    for x in range(HEIGHT):
        for y in range(WIDTH):
            cell = board[(x, y)]
            color = COLORS.get(cell, "#FFFFFF")

            rect = patches.Rectangle(
                (y, HEIGHT - x - 1),
                1,
                1,
                linewidth=1,
                edgecolor="black",
                facecolor=color,
            )
            ax.add_patch(rect)

            # if cell not in ("##", ".."):
            #     ax.text(
            #         y + 0.5,
            #         HEIGHT - x - 0.5,
            #         cell,
            #         ha="center",
            #         va="center",
            #         fontsize=10,
            #         weight="bold",
            #     )

    ax.set_xlim(0, WIDTH)
    ax.set_ylim(0, HEIGHT)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(f"Calendar Puzzle Solution – {month}/{day}")

    plt.axis("equal")
    plt.tight_layout()
    plt.savefig(filename, dpi=200)
    plt.close()

    print(f"PNG saved to {filename}")

# ----------------------------
# Main
# ----------------------------

def main(month: int, day: int):
    blocked = get_date_blocked(month, day)

    board = {}
    empty = set()

    for i in range(HEIGHT):
        for j in range(WIDTH):
            if (i, j) in blocked:
                board[(i, j)] = "##"
            else:
                board[(i, j)] = ".."
                empty.add((i, j))

    placements = {}

    for name, shape in PIECES.items():
        placements[name] = []
        for rot in all_rotations(shape):
            max_x = max(x for x, _ in rot)
            max_y = max(y for _, y in rot)
            for i in range(HEIGHT - max_x):
                for j in range(WIDTH - max_y):
                    cells = {(i + x, j + y) for x, y in rot}
                    if cells & blocked:
                        continue
                    placements[name].append(cells)

    if not solve(board, empty, set(PIECES.keys()), placements):
        print("No solution.")
        return

    print(f"\nSolution for {month}/{day}\n")
    for i in range(HEIGHT):
        print(" ".join(board[(i, j)] for j in range(WIDTH)))
        
    filename = f"solution_{month:02d}_{day:02d}.png"
    render_png(board, month, day, filename)

# ----------------------------
# Run
# ----------------------------

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python calendar_puzzle_solver.py <month> <day>")
    else:
        main(int(sys.argv[1]), int(sys.argv[2]))
