


import os
from typing import List, Optional
from blog_writer.config.config import Config
from blog_writer.config.definitions import ROOT_DIR
from blog_writer.model.search import Document, SearchResult
from blog_writer.store.storage import Storage
from blog_writer.utils.file import read_file


class FileReferenceExtractor:
    def __init__(self, config: Config, storage: Storage, search_result: Optional[SearchResult] = None):
        self.config = config
        self.storage = storage
        self.reference_folder = f"{ROOT_DIR}/input/file_references"
        self.ignore_files = ["README.md"]
        self.search_result = search_result if search_result is not None else SearchResult()
        
    
    def invoke(self) -> SearchResult:
        all_content = []
        
        # Walk through all files in reference folder
        for root, _, files in os.walk(self.reference_folder):
            for file in files:
                # Skip ignored files
                if file in self.ignore_files:
                    continue
                    
                file_path = os.path.join(root, file)
                try:
                    content = read_file(file_path)
                    all_content.append(content)
                except Exception as e:
                    print(f"Error reading file {file_path}: {str(e)}")
                    continue
        
        codes: List[Document] = []
        for content in all_content:
            codes.append(Document(code=content))
            
        self.search_result.result["codes"] = codes
        return self.search_result
        
