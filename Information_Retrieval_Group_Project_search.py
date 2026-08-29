import sys
import re
from nltk.stem import PorterStemmer

# Splits text into word tokens (reused from notebook)
def tokenize(text):
    # Return alphabetic tokens from the given text.
    tokens=re.findall(r"[A-Za-z]+",text)
    return tokens

# Converts tokens to lowercase (reused from notebook)
def normalize(tokens):
    # Convert every token to lowercase.
    return [token.lower() for token in tokens]

# Removes stop words (reused from notebook)
def remove_stopwords(tokens,stopwords):
    # Remove tokens present in the stop-word set.
    result=[]
    for token in tokens:
        if token not in stopwords:
            result.append(token)
    return result

# Applies Porter stemming (reused from notebook)
def stem(tokens,stemmer):
    # Stem every token.
    stemmed_tokens=[]
    for token in tokens:
        stemmed_tokens.append(stemmer.stem(token))
    return stemmed_tokens

# Loads stop words from the file (reused from notebook)
def load_stopwords(filename):
    # Load one stop word from each line.
    stopwords=set()
    try:
        with open(filename,"r",encoding="utf-8") as file:
            for line in file:
                word=line.strip().lower()
                if word:
                    stopwords.add(word)
    except FileNotFoundError:
        print("[ERROR] Stop-word file not found:",filename)
        sys.exit(1)
    return stopwords

# Loads the inverted index from the file into memory
def load_idx(filename):
    # Read the inverted index from disk.
    idx={}
    try:
        with open(filename,"r",encoding="utf-8") as f:
            header=f.readline().strip()
            if not header:
                return idx
            for raw_line in f:
                line=raw_line.rstrip("\n")
                if not line:
                    continue
                term,doc_str=line.split(" ",1)
                docs=[int(d) for d in doc_str.split(",")]
                idx[term]=docs
    except FileNotFoundError:
        print("[ERROR] Index file not found:",filename)
        sys.exit(1)
    return idx

# Two-pointer postings intersection (AND)
def intersect_postings(a_list,b_list):
    # Two-pointer merge for finding common docs
    i,j=0,0
    hits=[]
    while i<len(a_list) and j<len(b_list):
        if a_list[i]==b_list[j]:
            hits.append(a_list[i])
            i+=1
            j+=1
        elif a_list[i]<b_list[j]:
            i+=1
        else:
            j+=1
    return hits

# Two-pointer postings union (OR)
def union_postings(a_list,b_list):
    # Two-pointer merge for finding all docs.
    i,j=0,0
    hits=[]
    while i<len(a_list) and j<len(b_list):
        if a_list[i]==b_list[j]:
            hits.append(a_list[i])
            i+=1
            j+=1
        elif a_list[i]<b_list[j]:
            hits.append(a_list[i])
            i+=1
        else:
            hits.append(b_list[j])
            j+=1
    while i<len(a_list):
        hits.append(a_list[i])
        i+=1
    while j<len(b_list):
        hits.append(b_list[j])
        j+=1
    return hits

# Preprocess a single query term
def process_term(term,stemmer,sw_set):
    # Normalize, strip stopwords, and stem a query term.
    parts=tokenize(term)
    parts=normalize(parts)
    parts=remove_stopwords(parts,sw_set)
    parts=stem(parts,stemmer)
    return parts

# Parses and searches the query
def run_query(q_str,idx_map,stemmer,sw_set):
    # Parse and execute a simple Boolean query.
    parts=q_str.strip().split()
    if not parts:
        return []
    
    # Single term query
    if len(parts)==1:
        word=parts[0]
        tokens=process_term(word,stemmer,sw_set)
        if not tokens:
            return []
        return idx_map.get(tokens[0],[])
        
    # Two-term AND/OR query
    elif len(parts)==3:
        term1,op,term2=parts
        op=op.upper()
        if op not in ("AND","OR"):
            raise ValueError(f"Unsupported operator: '{op}'")
            
        t1=process_term(term1,stemmer,sw_set)
        t2=process_term(term2,stemmer,sw_set)
        
        p1=idx_map.get(t1[0],[]) if t1 else []
        p2=idx_map.get(t2[0],[]) if t2 else []
        
        if op=="AND":
            return intersect_postings(p1,p2)
        else:
            return union_postings(p1,p2)
            
    else:
        raise ValueError("Invalid query format")

def main():
    if len(sys.argv)!=3:
        print("Usage: python3 Information_Retrieval_Group_Project_search.py <query> <query_id>")
        print("Example: python3 Information_Retrieval_Group_Project_search.py \"aerodynamic AND slipstream\" q1")
        sys.exit(1)
        
    query=sys.argv[1]
    q_id=sys.argv[2]
    
    stemmer=PorterStemmer()
    stopwords_set=load_stopwords("stopwords.txt")
    
    index_file="Information_Retrieval_Group_Project_cran.index"
    idx_map=load_idx(index_file)
    
    try:
        results=run_query(query,idx_map,stemmer,stopwords_set)
    except ValueError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
        
    output_filename=f"{q_id}.txt"
    with open(output_filename,"w",encoding="utf-8") as outfile:
        for docid in results:
            outfile.write(f"{docid}\\n")
            
    print(f"[SUCCESS] Query: '{query}' | Match count: {len(results)} | Output: {output_filename}")

if __name__ == "__main__":
    main()
