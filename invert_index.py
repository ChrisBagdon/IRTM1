import string

class Inv_index:

    # Initialize object with empty dicts for index and postings
    def __init__(self):
        self.ind = {}
        self.postings = {}

    def index(self, filename):
        # Open file to process
        with open(filename) as file:
            # Initialize posting ID
            posting_id = 0
            # Process file line by line (tweet by tweet)
            for line in file:
                # Separate columns
                split_line = line.split("\t")
                doc_id = split_line[0]
                user_id = split_line[1]
                text = split_line[3]
                # Normalize text by removing tokens
                text = text.replace("[NEWLINE]", " ")
                text = text.replace("[TAB]", " ")
                # Remove # separately because hashtags often are not separated by spaces in tweets
                text = text.replace("#", " ")
                # Remove random newline chars
                text = text.replace("\n", "")
                # Normalize text by lower-casing, removing punctuation, and removing non ASCII chars
                text = normalize(text)
                # Find terms by splitting text on white space
                terms = text.split(" ")
                # Process terms
                for term in terms:
                    # If term has been found previously, add current document to term's posting
                    if term in self.ind.keys():
                        self.postings[self.ind[term][2]].append(doc_id)
                        # Recount postings
                        self.ind[term][1] = len(self.postings[self.ind[term][2]])
                    # If term is new, create new entry and posting
                    else:
                        self.ind[term] = [term, 1, posting_id]
                        self.postings[posting_id] = []
                        self.postings[posting_id].append(doc_id)
                        posting_id += 1

# Helper method for normalizing text
def normalize(text):
    output = ""
    for char in text.lower():
        if char in string.punctuation:
            continue
        try:
            char.encode("ascii")
            output += char
        except UnicodeEncodeError:
            output += ''
    return output