import json
from typing import List, Dict

from pydantic import BaseModel


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
        
    def load_from_json(self, json_data: str):
        data = json.loads(json_data)
        for topic,docs in data['result'].items():
            self.result[topic] = []
            for doc in docs:
                document = Document(url=doc["url"])
                for answer in doc["answers"]:
                    document.answers.append(Answer(answer["question"],answer["answer_data"]))
                self.result[topic].append(document)
        
        
    def get_minified(self) -> str:
        minified = ""
        for _,docs in self.result.items():
            for doc in docs:
                for answer in doc.answers:
                    minified += answer.answer_data + "\n"
        return minified
