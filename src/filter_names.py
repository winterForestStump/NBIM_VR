import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class CompanyMatcher:
    def __init__(self, list_companies, csv_companies):
        self.list_companies = list_companies
        self.csv_companies = csv_companies
        
    def preprocess(self, text):
        """Enhanced preprocessing"""
        if not isinstance(text, str):
            return ""
        
        text = text.lower().strip()
        # Remove legal entities and common words
        remove_words = ['inc', 'llc', 'ltd', 'corp', 'corporation', 
                       'co', 'company', 'the', 'and', '&']
        for word in remove_words:
            text = text.replace(word, '')
        
        # Remove punctuation and extra spaces
        text = ''.join(e for e in text if e.isalnum() or e.isspace())
        return ' '.join(text.split())
    
    def find_matches(self, similarity_threshold=0.7):
        """Find matches using TF-IDF and cosine similarity"""
        # Preprocess all names
        processed_list = [self.preprocess(name) for name in self.list_companies]
        processed_csv = [self.preprocess(name) for name in self.csv_companies]
        
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4))
        all_names = processed_list + processed_csv
        tfidf_matrix = vectorizer.fit_transform(all_names)
        
        # Split matrix
        list_vectors = tfidf_matrix[:len(processed_list)]
        csv_vectors = tfidf_matrix[len(processed_list):]
        
        # Calculate similarity
        similarity_matrix = cosine_similarity(list_vectors, csv_vectors)
        
        # Find matches
        matches = []
        for i in range(len(self.list_companies)):
            max_similarity = similarity_matrix[i].max()
            if max_similarity >= similarity_threshold:
                best_match_idx = similarity_matrix[i].argmax()
                matches.append({
                    'list_company': self.list_companies[i],
                    'csv_company': self.csv_companies[best_match_idx],
                    'similarity': max_similarity,
                    'match_type': 'fuzzy' if max_similarity < 0.95 else 'exact'
                })
        
        return pd.DataFrame(matches)
    
def main():
    company_names = pd.read_csv('data/company_names.csv')
    queries = []
    for company in range(len(company_names)):
        queries.append(company_names['0'][company])

    equity = pd.read_csv('data/eq_20250630.csv', delimiter=';', encoding='utf-16le')
    equity.drop(columns=['Incorporation Country'], inplace=True)
    equities = []
    for company in range(len(equity)):
        equities.append(equity['Name'][company])

    matcher = CompanyMatcher(queries, equities)
    matches_df = matcher.find_matches(similarity_threshold=0.75)
    matches_df.to_csv('data/matches_df.csv', index=False)

if __name__ == "__main__":
    main()