class User:
    def __init__(self, _id: int, name: str):
        self.id = _id
        self.name = name

    # for testing
    def __str__(self):
        return f"id = {self.id}, name = {self.name}\n"
