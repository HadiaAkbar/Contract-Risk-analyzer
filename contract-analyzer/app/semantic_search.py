from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def search_chunks(chunks: list, query: str, top_k: int = 5) -> list:
    """TF-IDF cosine similarity search — works fully offline, no external embeddings API
    required. Returns list of (index, text, score)."""
    if not chunks:
        return []

    corpus = chunks + [query]
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf = vectorizer.fit_transform(corpus)
    except ValueError:
        return []

    query_vec = tfidf[-1]
    doc_vecs = tfidf[:-1]
    scores = cosine_similarity(query_vec, doc_vecs).flatten()

    ranked = sorted(
        [(i, chunks[i], float(scores[i])) for i in range(len(chunks))],
        key=lambda x: x[2],
        reverse=True,
    )
    return [r for r in ranked if r[2] > 0][:top_k]
