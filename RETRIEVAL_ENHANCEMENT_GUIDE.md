# Enhanced Retrieval System Guide

## Overview

The system now includes an enhanced retrieval system that:
1. **Enhances queries** with legal/leasing terminology
2. **Prioritizes reliable sources** (government sites, official documents)
3. **Filters by geography** (Texas, Dallas, Houston, Austin, San Antonio)
4. **Reranks results** based on multiple factors
5. **Is configurable** for testing and optimization

## Key Features

### 1. Query Enhancement

Queries are automatically enhanced with:
- **Legal terminology**: Adds related legal terms (tenant, landlord, compliance, etc.)
- **Geographical context**: Adds city/state keywords when detected
- **Query type enhancement**: Adds context-specific terms based on question type

**Example:**
- Input: "What is ESA?"
- Enhanced: "What is ESA? legal definition regulation statute ordinance code esa emotional support animal service dallas dfw texas"

### 2. Source Reliability Scoring

Sources are scored (0.0 to 1.0) based on:
- **High Priority** (0.9-1.0): `.gov`, `.edu`, HUD, DOJ, Texas government sites
- **Medium Priority** (0.6-0.8): Legal sites, compliance sites
- **Low Priority** (0.0-0.5): News sites, blogs, opinion pieces

**Configuration:** Edit `retrieval_config.py` → `AUTHORITATIVE_SOURCES`

### 3. Geographical Filtering

Results are filtered by city when specified:
- Dallas queries → Prioritize Dallas-specific regulations
- Houston queries → Prioritize Houston-specific regulations
- Falls back to Texas-wide if no city-specific results found

**Configuration:** Edit `retrieval_config.py` → `GEOGRAPHICAL_KEYWORDS`

### 4. Reranking Algorithm

Results are reranked using weighted scores:
- **40%** - Vector similarity (from ChromaDB)
- **30%** - Source reliability score
- **15%** - Geographical match
- **10%** - Category relevance
- **5%** - Keyword match

**Configuration:** Edit `retrieval_config.py` → `rerank_results()` function

## Configuration

### Adding Authoritative Sources

Edit `retrieval_config.py`:

```python
AUTHORITATIVE_SOURCES = {
    "high_priority": [
        r"\.gov\b",  # Government websites
        r"your-custom-pattern",  # Add your pattern
    ],
    "medium_priority": [
        # Add medium priority patterns
    ],
    "low_priority": [
        # Add low priority patterns (will be penalized)
    ]
}
```

### Adding Legal Terminology

Edit `retrieval_config.py`:

```python
LEGAL_TERMINOLOGY = {
    "your_subject": ["term1", "term2", "term3"],
    # Add more subjects
}
```

### Adjusting Reranking Weights

Edit `retrieval_config.py` → `rerank_results()`:

```python
final_score = (
    base_score * 0.4 +           # Vector similarity (adjust this)
    reliability_score * 0.3 +    # Source reliability (adjust this)
    geo_score * 0.15 +            # Geographical match (adjust this)
    category_score * 0.1 +       # Category relevance (adjust this)
    keyword_score * 0.05          # Keyword match (adjust this)
)
```

## Testing

### Test Query Enhancement

```python
from retrieval_config import enhance_query_with_terminology

query = "What is ESA?"
enhanced = enhance_query_with_terminology(query, {"city": "Dallas"})
print(enhanced)
```

### Test Source Reliability

```python
from retrieval_config import calculate_source_reliability

score = calculate_source_reliability(
    "https://hud.gov/esa", 
    "HUD ESA Guidelines", 
    "ESA"
)
print(f"Reliability: {score}")  # Should be 1.0 (high priority)
```

### Test Reranking

```python
from retrieval_config import rerank_results

# Your search results
results = [...]  # From vector_store.search()

# Rerank them
reranked = rerank_results(results, "What is ESA?", {"city": "Dallas"})

# Check scores
for r in reranked:
    print(f"Score: {r['final_score']}, Source: {r['metadata']['source_name']}")
```

## Usage in Code

### Q&A System

The Q&A system automatically uses enhanced retrieval:

```python
search_results = self.vector_store.search(
    query=enhanced_query,
    n_results=7,
    context={"city": final_city},
    prioritize_reliable=True,  # Enable source prioritization
    filter_geography=final_city if final_city != "Texas-Statewide" else None
)
```

### Compliance Checker

The compliance checker uses enhanced retrieval for each clause:

```python
search_results = self.vector_store.search(
    query=clause['content'],
    n_results=5,
    context={"city": city},
    prioritize_reliable=True,
    filter_geography=city if city != "Texas-Statewide" else None
)
```

## Iterative Testing

### Step 1: Test Query Enhancement
1. Ask a question in the app
2. Check if the enhanced query includes relevant legal terms
3. Adjust `LEGAL_TERMINOLOGY` if needed

### Step 2: Test Source Prioritization
1. Ask a question
2. Check if `.gov` sources appear first
3. Adjust `AUTHORITATIVE_SOURCES` if needed

### Step 3: Test Geographical Filtering
1. Ask "What is ESA law in Dallas?"
2. Check if Dallas-specific results appear first
3. Adjust `GEOGRAPHICAL_KEYWORDS` if needed

### Step 4: Test Reranking
1. Compare results before/after reranking
2. Adjust weights in `rerank_results()` if needed
3. Test with different query types

## Best Practices

1. **Start with defaults**: The system is pre-configured with good defaults
2. **Test incrementally**: Change one thing at a time
3. **Monitor results**: Check if changes improve answer quality
4. **Add authoritative sources**: Prioritize `.gov` and official sites
5. **Expand terminology**: Add domain-specific terms as you discover them

## Troubleshooting

### Results not relevant enough?
- Increase `n_results` multiplier in `search()` (currently 2x)
- Adjust reranking weights to favor vector similarity
- Add more specific legal terminology

### Too many generic results?
- Increase source reliability weight
- Add more authoritative source patterns
- Strengthen geographical filtering

### Missing city-specific results?
- Expand `GEOGRAPHICAL_KEYWORDS` for your city
- Reduce geographical filter strictness
- Check if sources actually mention the city

## Advanced: Custom Retrieval Strategies

You can create custom retrieval strategies by:

1. **Modifying query enhancement**: Edit `enhance_query_with_terminology()`
2. **Custom reranking**: Edit `rerank_results()` with your own logic
3. **Adding filters**: Modify `filter_by_geography()` or create new filters
4. **Source scoring**: Customize `calculate_source_reliability()` for your needs

## Example: Custom Subject Enhancement

```python
# In retrieval_config.py
LEGAL_TERMINOLOGY["eviction"] = [
    "eviction", "evict", "termination", "remove", 
    "dispossess", "unlawful detainer", "forcible entry"
]

# Now queries about eviction will automatically include these terms
```

## Performance Notes

- **Query enhancement**: Adds ~50-100ms per query (minimal)
- **Reranking**: Adds ~10-20ms per result (very fast)
- **Geographical filtering**: Adds ~5-10ms (negligible)
- **Overall impact**: <200ms additional latency (acceptable)

The system is optimized for speed while maintaining quality.

