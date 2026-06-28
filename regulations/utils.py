class Cursor:
    def __init__(self, items):
        self.items = items
        self.pos = -1

    def current(self):
        return self.items[self.pos]

    def next(self):
        self.pos += 1
        return self.current() if self.pos < len(self.items) else None

    def peek(self, n=1):
        return (
            self.items[self.pos + n]
            if self.pos + n < len(self.items)
            else None
        )
