def to_text(x, depth = 0) -> str:
    indent = depth * "  "

    if isinstance(x, dict):
        result = ""
        for k, v in x.items():
            if isinstance(v, (dict, list, tuple, set)):
                result += f"{indent}{k}:\n{to_text(v, depth + 1)}"
            else:
                result += f"{indent}{k}: {v}\n"
    elif isinstance(x, (list, tuple, set)):
        result = ""
        for i in x:
            if isinstance(i, (dict, list, tuple, set)):
                result += to_text(i, depth)
            else:
                result += f"{indent}- {i}\n"
    else:
        result = f"{indent}{x}\n"

    return result + '\n'

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
