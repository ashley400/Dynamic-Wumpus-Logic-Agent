import random

class WumpusWorld:
    def __init__(self, size):
        self.size = size
        self.grid = [["" for _ in range(size)] for _ in range(size)]
        self.agent_pos = (0, 0)
        self.place_hazards()

    def place_hazards(self):
        x, y = self.random_empty()
        self.grid[x][y] = "W"
        for _ in range(self.size):
            x, y = self.random_empty()
            self.grid[x][y] = "P"

    def random_empty(self):
        while True:
            x = random.randint(0, self.size - 1)
            y = random.randint(0, self.size - 1)
            if self.grid[x][y] == "" and (x, y) != (0, 0):
                return x, y

    def get_percepts(self, x, y):
        p = []
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                if self.grid[nx][ny] == "P":
                    p.append("Breeze")
                if self.grid[nx][ny] == "W":
                    p.append("Stench")
        return p


class KnowledgeBase:
    def __init__(self):
        self.clauses = []

    def tell(self, clause):
        self.clauses.append(clause)

    def ask(self, query):
        clauses = self.clauses + [[negate(query)]]
        return not resolution(clauses)


def negate(x):
    return x[1:] if x.startswith("~") else "~" + x


def resolve(ci, cj):
    r = []
    for di in ci:
        for dj in cj:
            if di == negate(dj):
                new = list(set(ci + cj))
                new.remove(di)
                new.remove(dj)
                r.append(new)
    return r


def resolution(clauses):
    new = []
    while True:
        n = len(clauses)
        pairs = [(clauses[i], clauses[j]) for i in range(n) for j in range(i+1, n)]

        for (ci, cj) in pairs:
            resolvents = resolve(ci, cj)
            if [] in resolvents:
                return True
            new.extend(resolvents)

        if all(c in clauses for c in new):
            return False

        for c in new:
            if c not in clauses:
                clauses.append(c)


class Agent:
    def __init__(self, world):
        self.world = world
        self.kb = KnowledgeBase()
        self.visited = set()
        self.pos = (0, 0)

    def neighbors(self, x, y):
        n = []
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            if 0 <= nx < self.world.size and 0 <= ny < self.world.size:
                n.append((nx, ny))
        return n

    def update_kb(self, percepts, x, y):
        if "Breeze" not in percepts:
            for nx, ny in self.neighbors(x, y):
                self.kb.tell([f"~P{nx}{ny}"])
        if "Stench" not in percepts:
            for nx, ny in self.neighbors(x, y):
                self.kb.tell([f"~W{nx}{ny}"])

    def safe(self, x, y):
        return self.kb.ask(f"P{x}{y}") == False and self.kb.ask(f"W{x}{y}") == False

    def move(self):
        x, y = self.pos
        p = self.world.get_percepts(x, y)
        print("Pos:", self.pos, "Percepts:", p)
        self.update_kb(p, x, y)
        self.visited.add((x, y))

        for nx, ny in self.neighbors(x, y):
            if (nx, ny) not in self.visited and self.safe(nx, ny):
                self.pos = (nx, ny)
                return True
        return False


world = WumpusWorld(4)
agent = Agent(world)

steps = 0
while agent.move():
    steps += 1

print("Steps:", steps)