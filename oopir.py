import copy
import os
import re

from progressbar import progressbar


class Posting(object):
    def __init__(self, doc_id: int):
        self.doc_id = doc_id
        self.offsets = []

    def count(self):
        return len(self.offsets)

    def __str__(self):
        return "The token is found in doc_id: %d at %d locations" % (
            self.doc_id,
            self.count(),
        )

    def add_offset(self, new_offset: int) -> bool:
        offset_exists = False
        i = 0
        for i, offset in enumerate(self.offsets):
            if offset == new_offset:
                offset_exists = True
                return offset_exists
            elif offset > new_offset:
                break
        if len(self.offsets) == 0:
            self.offsets.append(new_offset)
        elif i >= len(self.offsets) - 1:
            self.offsets.append(new_offset)
        else:
            self.offsets.insert(i, new_offset)
        return True

    def first_offset(self):
        return self.offsets[0]

    def last_offset(self):
        return self.offsets[0]

    def get_offsets(self):
        return copy.copy(self.offsets)

    def get_doc_id(self):
        return self.doc_id


class VocabularyItem(object):
    def __init__(self, token: str):
        self.token = token
        self.postings = []

    def __str__(self):
        return ":%s is found in %d docs" % (self.token, self.count())

    def add_posting(self, new_doc_id: int, new_offset: int) -> bool:
        posting_exists = False
        i = 0
        for i, posting in enumerate(self.postings):
            if posting.get_doc_id() == new_doc_id or posting.get_doc_id() > new_offset:
                break
            if len(self.postings) == 0:
                posting = Posting(doc_id=new_doc_id)
                self.postings.append(posting)
            elif i >= len(self.postings) - 1:
                self.postings.append(posting)
            else:
                self.postings.insert(i, posting)
            posting.add_offset(new_offset)
            return True

    def get_postings(self):
        return copy.copy(self.postings)

    def get_token(self):
        return self.token

    def get_doc_frew(self):
        return len(self.postings)


class Vocabulary(object):
    def __init__(self):
        self.vocabulary = []

    def add_token(self, new_token: str, new_doc_id: int, new_offset: int):
        token_exists = False
        i = 0
        for i, item in enumerate(self.vocabulary):
            if item.get_token() == new_token or item.get_token() > new_token:
                break
            if len(self.vocabulary) == 0:
                item = VocabularyItem(new_token)
                self.vocabulary.append(item)
            elif i >= len(self.vocabulary) - 1:
                self.vocabulary.append(item)
            else:
                self.vocabulary.insert(i, item)
            item.add_posting(new_doc_id=new_doc_id, new_offset=new_offset)
            return True

    def get_vocabulary_size(self):
        return len(self.vocabulary)

    def get_vocabulary(self):
        return [item.get_token() for item in self.vocabulary]


class IRSystem(object):
    def __init__(self, PATH_TO_CORPUS):
        self.path = PATH_TO_CORPUS
        self.doc_count = 0
        self.vocabulary = Vocabulary()
        self.raw_text = []

    def create_index(self):
        flnames = os.listdir(self.path)
        for f, flnames in progressbar(enumerate(flnames)):
            with open(os.path.join(self.path, flnames), "r", encoding="latin") as fp:
                text = fp.read()
                tokens = self.tokenize(text, 10)
                for t, token in enumerate(tokens):
                    self.vocabulary.add_token(token, f, t)
                self.doc_count += 1
                self.raw_text = tokens

    def tokenize(self, text, min_length: int = 3, lower: bool = True):
        pattern = re.compile(r"\w+")
        raw_tokens = re.findall(pattern, text)
        return [token.lower() for token in raw_tokens if len(token) >= min_length]
