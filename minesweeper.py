import itertools
import random
import time


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        if len(self.cells) == self.count:
            return self.cells

        return set()

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        if (self.count == 0):
            return self.cells

        return set()

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # Remove from self.cells
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # Remove from self.cells
        if cell in self.cells:
            self.cells.remove(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def mark_additional_cells(self):
        """
        Marks additional cells as safe or as mines if it can be
        concluded based on the AI's knowledge base.
        """
        mines = []
        safes = []
        for sentence in self.knowledge:
            # mark any additional cells as mines if it can be concluded based on the AI's knowledge base
            if sentence.known_mines():
                for cell in sentence.known_mines():
                    if cell in self.mines:
                        continue

                    mines.append(cell)

                continue

            # mark any additional cells as safe if it can be concluded based on the AI's knowledge base
            if sentence.known_safes():
                for cell in sentence.known_safes():
                    if cell in self.safes:
                        continue

                    safes.append(cell)

                continue

        for mine in mines:
            self.mark_mine(mine)

        for safe in safes:
            self.mark_safe(safe)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        self.moves_made.add(cell)
        self.mark_safe(cell)

        # Add a new sentence to the knowledge base
        neighbors = set()
        for row in range(cell[0] - 1, cell[0] + 2):
            for col in range(cell[1] - 1, cell[1] + 2):
                neighbor = (row, col)

                if neighbor in self.mines:
                    count -= 1
                    continue

                if (
                    neighbor in self.safes or
                    neighbor == cell or
                    row >= self.height or
                    row < 0 or
                    col < 0 or
                    col >= self.width):
                    continue

                neighbors.add(neighbor)

        if (len(neighbors) > 0):
            sentence = Sentence(
                cells=neighbors,
                count=count
            )

            self.knowledge.append(sentence)

        self.mark_additional_cells()

        newInferences = True

        while newInferences:
            newInferences = False
            knownSafes = set()
            knownMines = set()

            for sentence in self.knowledge:
                if sentence.known_safes():
                    knownSafes.update(sentence.known_safes())
                if sentence.known_mines():
                    knownMines.update(sentence.known_mines())

            for cell in knownSafes:
                if cell not in self.safes:
                    self.mark_safe(cell)
                    newInferences = True

            for cell in knownMines:
                if cell not in self.mines:
                    self.mark_mine(cell)
                    newInferences = True

            newSentences = []
            for sentence in self.knowledge.copy():
                # infer new sentences
                for potential_subset in self.knowledge.copy():
                    if sentence == potential_subset:
                        continue

                    if potential_subset.cells.issubset(sentence.cells):
                        new_count = sentence.count - potential_subset.count
                        new_cells = sentence.cells - potential_subset.cells

                        newSentence = Sentence(
                            cells=new_cells,
                            count=new_count
                        )

                        if len(new_cells) > 0 and newSentence not in self.knowledge:
                            newSentences.append(newSentence)
                            newInferences = True

            if len(newSentences) <= 0:
                continue

            for sentence in newSentences:
                self.knowledge.append(sentence)

        self.mark_additional_cells()

        return None

    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            if (
                cell in self.moves_made):
                continue

            return cell

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        possibleMoves = []
        for row in range(self.height):
            for col in range(self.width):
                cell = (row, col)

                if cell in self.moves_made or cell in self.mines:
                    continue

                possibleMoves.append(cell)

        if len(possibleMoves) == 0:
            return None

        moveMade = random.choice(possibleMoves)

        self.moves_made.add(moveMade)

        return moveMade


def test_minesweeper_ai():
    # Initialize the game and AI
    game = Minesweeper(height=4, width=4, mines=1)
    ai = MinesweeperAI(height=4, width=4)

    # Manually set a known mine for this test case
    known_mine = (0, 0)
    game.mines.add(known_mine)
    game.board[0][0] = True

    # Inform AI of the known mine
    ai.mark_mine(known_mine)

    # Manually add a sentence to AI's knowledge
    ai.knowledge.append(Sentence({(1, 2), (0, 3), (1, 3)}, 1))

    # Invoke add_knowledge on a cell that is safe
    ai.add_knowledge((1, 1), 1)

    # Check the knowledge base and state of AI
    print(f"Mines: {ai.mines}")
    print(f"Safes: {ai.safes}")
    for sentence in ai.knowledge:
        print(f"Sentence: {sentence}")

test_minesweeper_ai()