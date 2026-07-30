from services.service import Service

class UnsureService(Service):

    def answer(self, query: str) -> str:
        return "unsure"