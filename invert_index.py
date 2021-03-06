import string
from nltk import ngrams
class Inv_index:

    # Initialize object with empty dicts for index and postings
    def __init__(self):
        self.ind = {}
        self.postings = {}
        self.bi_ind = {}

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
                    # Add term's bigrams to bigram index
                    for bigram in ngrams("$" + term + "$", 2):
                        bigram = "".join([x for x in bigram])
                        if bigram in self.bi_ind:
                            if term not in self.bi_ind[bigram]:
                                self.bi_ind[bigram].append(term)
                        else:
                            self.bi_ind[bigram] = []
                            self.bi_ind[bigram].append(term)


    def query(self, text):
        text = text.lower()
        terms = text.split(" ")
        if len(terms) == 1:
            try:
                # Check for wildcards. First edit query based on * position
                if "*" in text:
                    term_cans = []
                    inner_wild = False
                    # If query begins with and ends with *, simply remove start and end markers
                    if text.startswith("*") and text.endswith("*"):
                        wild_text = text[1:-1]
                    # If query begins with * remove start of term marker
                    elif text.startswith("*"):
                        wild_text = text[1:]+"$"
                    # If query ends with *, remove end marker
                    elif text.endswith("*"):
                        wild_text = "$"+ text[:-1]
                    # If * is inside query, flag for skipping post processing
                    else:
                        ast = text.find("*")
                        wild_text = "$" + text.replace("*","") + "$"
                        inner_wild = True
                    # Break query into bigrams
                    for bigram in ngrams(wild_text, 2):
                        bigram = "".join([x for x in bigram])
                        # For first bigram create list of terms containing bigrams
                        if len(term_cans) == 0:
                            term_cans = self.bi_ind[bigram]
                        # Intersect current list of terms with list of current bigram
                        else:
                            term_cans = [term for term in term_cans if term in self.bi_ind[bigram]]
                    docs = []
                    # Get docs containing terms
                    for term_can in term_cans:
                        # Post process terms
                        if not inner_wild:
                            # Check if query without * is within terms
                            # Prevents returning "moon" when searching "mon*"
                            if text.replace("*", "") not in term_can:
                                continue
                        for doc_id in self.postings[self.ind[term_can][2]]:
                            docs.append(doc_id)
                    return set(docs)
                else:
                    return self.postings[self.ind[text.lower()][2]]  # return postings list for a single term query
            except:
                print(f"{text} could not be found in index")

        else:
            set_list = []
            for term in terms:
                try:
                    set_list.append(self.postings[self.ind[term][2]])
                except:
                    pass
            return set.intersection(*set_list)  # return postings list for a bi-word query

    def query_intersection(self, term1, term2):
        ### Takes in two terms and queries the dataset for intersecting postings

        # Initialize intersection list
        intersections_ints = []

        # Get the sorted postings lists for each queried term with query(text) method;
        # Convert the postings from strings to integers and sort
        postings_1_ints = sorted([int(posting) for posting in self.query(term1)])
        postings_2_ints = sorted([int(posting) for posting in self.query(term2)])

        # Initialize iterators for each postings list
        postings_1_iter = iter(postings_1_ints)
        postings_2_iter = iter(postings_2_ints)

        # Initialize iteration through postings lists
        next_postings_1 = next(postings_1_iter)
        next_postings_2 = next(postings_2_iter)

        print(next_postings_1, next_postings_2)

        # While there are postings left in both lists
        while next_postings_1 != None and next_postings_2 != None:
            # If the postings are equal
            if next_postings_1 == next_postings_2:
                # Add posting to the intersections
                intersections_ints.append(next_postings_1)
                # Progress through each postings list in parallel
                next_postings_1 = next(postings_1_iter, None)
                next_postings_2 = next(postings_2_iter, None)
            # If the first posting is less than the second posting
            elif next_postings_1 < next_postings_2:
                # Iterate through the first postings list
                next_postings_1 = next(postings_1_iter, None)
            # If the first posting surpasses the second posting
            else:
                # Iterate through the second postings list
                next_postings_2 = next(postings_2_iter, None)

        # Convert intersection postings to strings
        intersections = [str(posting) for posting in intersections_ints]
        return intersections


# Helper method for normalizing text
def normalize(text):
    output = ""
    for char in text.lower():
        # Remove punc
        if char in string.punctuation:
            continue
        # Check if char is ascii, skip if not. This handles non-alphanumeric languages which often do not use whitespace.
        # It also removes emojis
        try:
            char.encode("ascii")
            output += char
        except UnicodeEncodeError:
            output += ''
    return output
