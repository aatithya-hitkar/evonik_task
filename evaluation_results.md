# Evaluation Results

## Retrieval Metrics

- **Hit@3**: 0.833 (83.3%)
- **Recall@3**: 0.733 (73.3%)

## Generation Quality Rubric

### 3-Point Scale:

**3 - Excellent**
- Factually accurate based on recipe data
- Complete answer addressing all parts of the question
- Properly cites source recipes

**2 - Good** 
- Mostly accurate with minor gaps
- Addresses main question but may miss details
- Some citation of sources

**1 - Poor**
- Inaccurate or incomplete information
- Fails to address the question adequately
- No proper source citation

## Test Case Scores

| Test ID | Question | Score | Notes |
|---------|----------|-------|-------|
| 1 | How do I make carbonara? | 3 | Excellent: Complete step-by-step instructions, factually accurate, properly cites Recipe 1 |
| 2 | What vegetarian dinner options do you have? | 2 | Good: Identifies some options but misses several vegetarian recipes, cites sources |
| 3 | How long should I cook quinoa? | 3 | Excellent: Accurate cooking time and method, properly cites source recipe |
| 4 | What can I substitute for eggs in baking? | 3 | Excellent: Correctly states no information available, appropriate response |
| 5 | How do I make pancakes fluffy? | 3 | Excellent: Comprehensive tips, accurate information, properly cites Recipe 1 |
| 6 | What spices go in chicken tacos? | 2 | Good: Lists correct spices but lacks specific quantities, cites source |

**Average Score: 2.67/3 (89%)**

## Failure Analysis

### Retrieval Performance
- **Strong Hit Rate (83.3%)**: The system successfully retrieves at least one relevant recipe for 5 out of 6 queries
- **Good Recall (73.3%)**: Captures most relevant recipes, though some vegetarian options were missed in query #2

### Generation Quality Analysis

**Strengths:**
- Excellent factual accuracy when relevant recipes are retrieved
- Consistent source citation (all responses properly reference recipe numbers)
- Appropriate handling of queries with no relevant information (query #4)
- Detailed, actionable responses for cooking instructions

**Areas for Improvement:**
- **Query #2 (Vegetarian options)**: Retrieved only 2 of 5 relevant vegetarian recipes, leading to incomplete answer
- **Query #6 (Taco spices)**: Missing specific quantities that were available in the source recipe

**Technical Performance:**
- Average response latency: 5.8 seconds
- No API errors or generation failures
- Consistent response format and quality

### Recommendations
1. **Improve retrieval diversity**: Enhance vector search to capture more varied relevant recipes for broad queries
2. **Include quantities**: Modify prompt to encourage inclusion of specific measurements when available
3. **Expand vegetarian tagging**: Better categorization of vegetarian recipes in the database
