from typing import List, Dict


class Answer:
    def __init__(self, question: str, answer: str):
        self.question = question
        self.answer_data = answer


class Document:
    def __init__(self, url: str = "", answers: List[Answer] = None):
        if answers is None:
            answers = []
        self.url = url
        self.answers = answers

    def get_by_question(self, question: str) -> str:
        for answer in self.answers:
            if answer.question == question:
                return answer.answer_data
        return ""

class SearchResult:
    def __init__(self, doc_per_topic: Dict[str, List[Document]] = None):
        if doc_per_topic is None:
            doc_per_topic = {}
        self.result = doc_per_topic
