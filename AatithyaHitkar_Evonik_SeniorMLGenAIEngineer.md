# Evonik — Senior ML/GenAI Engineer Technical Assessment
**Candidate:** Aatithya Hitkar
**Date:** 12th November 2025
**Total Time Spent:** 5 Hour 30 min

---

## Task 1: Mini-RAG System

### 1.1 System Design

**Architecture Overview:**
```
Recipe JSON → Text Concatenation → OpenAI text-embedding-3-small → FAISS IndexFlatIP → Cosine Similarity Search → GPT-4o-mini → Response with Citations
```

**Design Components:**
1. **Data Ingestion:** Load 15 recipes from JSON file, each containing title, cuisine_type, serves, ingredients, instructions, and optional garnish_serving
2. **Chunking Strategy:** Each recipe treated as single document with concatenated text (title + cuisine + ingredients + instructions)
3. **Embedding Model:** OpenAI text-embedding-3-small (1536 dimensions), chosen for cost-effectiveness and good performance on text similarity
4. **Retrieval Method:** FAISS IndexFlatIP with cosine similarity, k=3 retrieval, L2 normalization for embeddings
5. **Answer Generation:** GPT-4o-mini, temperature=0.7, max_completion_tokens=500
6. **Guardrails:** System prompt enforces citation requirements and abstention when no relevant recipes found

**Scale Considerations:** For 10K+ recipes would implement hierarchical indexing, recipe chunking by sections, and approximate nearest neighbor search (IndexIVFFlat)

---

### 1.2 Prompts

**System Prompt:**
```
You are a helpful cooking assistant. Answer cooking questions based only on the provided recipe context.

Requirements:
- Use only information from the provided recipes
- Always cite which recipes you reference
- If the recipes don't contain relevant information, say "I don't have information about that in my recipe collection"
- Keep responses practical and helpful
- Focus only on cooking and recipe topics
```

**Retrieval-Augmented User Prompt Template:**
```
Context:
{context}

User Question: {query}

Based on the recipe information above, answer the user's question. Remember to cite which recipes you're referencing.
```

**Example with Retrieved Context:**
```
Context:
Here are the relevant recipes from my database:

Recipe 1: Classic Spaghetti Carbonara
Cuisine: Italian
Serves: 2
Ingredients:
- 200g spaghetti
- 100g guanciale (or pancetta)
- 2 large eggs
- 1 large egg yolk
- 50g freshly grated Pecorino Romano cheese
- Freshly ground black pepper
- Salt for pasta water
Instructions:
1. Bring a large pot of salted water to a boil and cook spaghetti according to package directions until 'al dente'.
2. While pasta is cooking, heat a large pan over medium heat. Add diced guanciale and cook slowly until crispy.
3. In a bowl, whisk together eggs, egg yolk, and grated Pecorino Romano cheese.
4. Reserve 1 cup of pasta water before draining the pasta.
5. Add hot pasta to the pan with guanciale and toss to combine.
6. Remove from heat and quickly stir in the egg mixture, adding pasta water as needed to create a creamy sauce.
7. Serve immediately with extra cheese and black pepper.

User Question: How do I make carbonara?

Based on the recipe information above, answer the user's question. Remember to cite which recipes you're referencing.
```

---

### 1.3 Evaluation

#### Test Dataset (6 Q/A Pairs)

| ID | Question | Gold Answer | Ground Truth Sources |
|----|----------|-------------|---------------------|
| Q1 | How do I make carbonara? | For carbonara, cook 200g spaghetti until al dente. Dice 100g guanciale and cook until crispy. Mix 2 eggs, 1 egg yolk, and 50g grated Pecorino Romano with black pepper. Add hot pasta to the guanciale pan, then quickly mix in the egg mixture off heat. Add pasta water to create a creamy sauce. Serve with more cheese and pepper. | Classic Spaghetti Carbonara |
| Q2 | What vegetarian dinner options do you have? | I have several vegetarian options: Chana Masala (chickpea curry with spices), Mediterranean Greek Salad with feta cheese, Fresh Guacamole as a side, Spanish Gazpacho cold soup, and Quinoa Salad with lemon vinaigrette. | Quick Chana Masala, Mediterranean Greek Salad, Fresh Guacamole, Spanish Gazpacho (Cold Soup), Quinoa Salad with Lemon Vinaigrette |
| Q3 | How long should I cook quinoa? | Cook quinoa by combining 1 cup rinsed quinoa with 2 cups water. Bring to a boil, then reduce heat to low, cover, and simmer for 15 minutes until water is absorbed. Let it sit covered for 5 more minutes, then fluff with a fork. | Quinoa Salad with Lemon Vinaigrette |
| Q4 | What can I substitute for eggs in baking? | I don't have information about egg substitutes for baking in my recipe collection. | Should abstain - no source |
| Q5 | How do I make pancakes fluffy? | For fluffy pancakes, don't overmix the batter - it should be lumpy. Mix wet and dry ingredients separately, then combine just until incorporated. Use baking powder (3.5 tsp for 1.5 cups flour) and cook on medium-low heat until bubbles form on surface before flipping. | Fluffy American Pancakes |
| Q6 | What spices go in chicken tacos? | For chicken tacos, use 1 tbsp chili powder, 1 tsp cumin, 1/2 tsp paprika, 1/2 tsp onion powder, and 1/4 tsp garlic powder. Mix these spices and coat diced chicken breast before cooking in olive oil. | Simple Chicken Tacos |

---

#### Retrieval Performance

**Metric:** Hit@3 and Recall@3  
**Results:**
- Total queries: 6
- Hit@3: 5/6 (83.3%)
- Recall@3: 73.3%
- **Analysis:** Query #4 (egg substitutes) correctly retrieved no relevant recipes as none exist in database

---

#### Generation Quality Evaluation

**Rubric (3-point scale):**
1. **Factual Accuracy:** Complete and accurate information based on retrieved recipes
2. **Citation Quality:** Proper attribution to source recipes
3. **Abstention Appropriateness:** Correct refusal when no relevant information available

**Evaluation Method:** Manual scoring based on comparison with gold answers and retrieved context

**Scores:**

| Question | Score | Notes |
|----------|-------|-------|
| Q1 | 3 | Excellent: Complete step-by-step instructions, factually accurate, properly cites Recipe 1 |
| Q2 | 2 | Good: Identifies some options but misses several vegetarian recipes, cites sources |
| Q3 | 3 | Excellent: Accurate cooking time and method, properly cites source recipe |
| Q4 | 3 | Excellent: Correctly states no information available, appropriate response |
| Q5 | 3 | Excellent: Comprehensive tips, accurate information, properly cites Recipe 1 |
| Q6 | 2 | Good: Lists correct spices but lacks specific quantities, cites source |

**Average Score:** 2.67/3 (89%)

---

### 1.4 Failure Case Analysis

**Failed Query:** "What vegetarian dinner options do you have?"

**What Happened:**
- **Retrieved:** Quick Chana Masala, Quinoa Salad with Lemon Vinaigrette, Easy Thai Green Curry with Chicken
- **Generated Answer:** Listed only 2 vegetarian options, missed Mediterranean Greek Salad, Fresh Guacamole, and Spanish Gazpacho
- **Expected:** Should have retrieved and mentioned all 3 vegetarian recipes
- **Root Cause:** Retrieval issue - vector similarity didn't capture all vegetarian recipes due to diverse ingredient lists and cooking methods

**Proposed Fixes:**
1. **Immediate:** Add explicit vegetarian tags to recipe metadata for better filtering
2. **Short-term:** Implement hybrid search combining semantic similarity with keyword matching for dietary restrictions


---

### 1.5 Operations & Logging

**Five Critical Fields to Log:**

| Field | Type | Purpose | Example |
|-------|------|---------|---------|
| 1. `query_id` | string | Unique request tracking and debugging | "req_20241112_143052_abc123" |
| 2. `user_query` | string | Understanding user intent and failure analysis | "How do I make carbonara?" |
| 3. `retrieved_doc_ids` | list | Debugging retrieval quality and relevance | ["recipe_001", "recipe_007", "recipe_012"] |
| 4. `retrieval_scores` | list | Monitoring retrieval confidence and thresholds | [0.89, 0.76, 0.65] |
| 5. `generation_metadata` | dict | Model performance and cost tracking | {"model": "gpt-4o-mini", "tokens": 245, "latency_ms": 1200} |

**Additional Logging Considerations:** Timestamp, model version, temperature setting, user session ID, response quality score

**Privacy & Data Protection Notes:**
- Hash user queries containing potential PII before logging
- 30-day retention policy for query logs, 1-year for aggregated metrics
- AES-256 encryption for stored logs
- Role-based access control for log data
- GDPR compliance with right to deletion and data portability

---

## Task 2: Multi-Label Document Tagger

### 2.1 Design

**Approach:** LLM-based few-shot structured output (OpenAI GPT-4o-mini)  
**Dataset:** 20 customer support ticket documents  
**Labels:** account_access, account_update, api_access, billing, browser, cancellation, feature_request, integration, mobile_app, performance, product_feedback, product_inquiry, refund, reporting, security, shipping, technical_issue, ui_feedback, urgent  
**Rationale:** Few-shot learning approach selected for multi-label classification of customer support tickets using complete original label set of 19 categories with confidence threshold of 0.3 to filter predictions

**JSON Schema:**
```json
{
  "predicted_labels": [
    {
      "label": "string",
      "confidence": "float"
    }
  ]
}
```

---

### 2.2 Implementation & Results

**Dataset Split:**
- Training examples: 3 documents with labels
- Test examples: 17 documents

**Few-Shot Prompt:**
```
You are an expert text tagger for customer support tickets. Your task is to tag support tickets into relevant categories with confidence scores.

Available categories: account_access, technical_issue, urgent, billing, refund, mobile_app, product_inquiry, account_update, reporting, cancellation, feature_request, ui_feedback, integration, api_access, shipping, performance, browser, security, product_feedback

Instructions:
1. Analyze the text and identify ALL relevant categories
2. Provide confidence scores (0.0 to 1.0) for each predicted category
3. Only include categories with confidence >= 0.3
4. Return ONLY a valid JSON object with no additional text

Here are some examples:

Example 1:
Text: "Dear Support, I'm unable to log in to my account after the last password reset."
Output: {"predicted_labels": [{"label": "account_access", "confidence": 0.95}, {"label": "technical_issue", "confidence": 0.85}, {"label": "urgent", "confidence": 0.7}]}

Example 2:
Text: "Hi Team, my payment was charged twice yesterday. Please process a refund."
Output: {"predicted_labels": [{"label": "billing", "confidence": 0.98}, {"label": "refund", "confidence": 0.95}, {"label": "urgent", "confidence": 0.8}]}

Example 3:
Text: "Dear Support, can you enable dark mode for the web dashboard?"
Output: {"predicted_labels": [{"label": "feature_request", "confidence": 0.95}, {"label": "ui_feedback", "confidence": 0.85}]}

Now classify this text:
Text: "{text}"
Output:
```

**Metric:** Macro-F1 Score = 0.493

**Per-Label Performance:**

| Label | Precision | Recall | F1-Score | Support |
|-------|-----------|--------|----------|---------|
| account_access | 1.000 | 1.000 | 1.000 | 2 |
| account_update | 1.000 | 0.750 | 0.857 | 4 |
| api_access | 1.000 | 1.000 | 1.000 | 1 |
| billing | 0.750 | 0.750 | 0.750 | 4 |
| browser | 1.000 | 1.000 | 1.000 | 1 |
| cancellation | 0.500 | 0.500 | 0.500 | 2 |
| feature_request | 1.000 | 1.000 | 1.000 | 2 |
| integration | 0.000 | 0.000 | 0.000 | 1 |
| mobile_app | 1.000 | 1.000 | 1.000 | 2 |
| performance | 1.000 | 1.000 | 1.000 | 1 |
| product_feedback | 0.000 | 0.000 | 0.000 | 1 |
| refund | 0.000 | 0.000 | 0.000 | 1 |
| reporting | 0.500 | 1.000 | 0.667 | 1 |
| security | 0.000 | 0.000 | 0.000 | 1 |
| shipping | 1.000 | 1.000 | 1.000 | 1 |
| technical_issue | 1.000 | 1.000 | 1.000 | 6 |
| ui_feedback | 0.500 | 1.000 | 0.667 | 1 |
| urgent | 0.286 | 1.000 | 0.444 | 2 |

---

### 2.3 Error Analysis

**Mistake #1: Missing Label Categories**
- **Document:** "Hi Team, please cancel my subscription renewal." (ID 7)
- **Predicted:** cancellation (0.95), urgent (0.7)
- **Actual:** billing, cancellation, refund
- **Why it failed:** The model correctly identified the cancellation request but failed to recognize the billing and refund implications of subscription cancellation. The model also incorrectly added an urgent classification not present in the ground truth.
- **Proposed Fix:** Include additional few-shot examples that demonstrate the relationship between cancellation requests and their billing/refund implications. Enhance the prompt with explicit guidance on when cancellations involve financial processes.

**Mistake #2: Label Substitution**
- **Document:** "Hi, please help reset my two-factor authentication so I can log in again." (ID 17)
- **Predicted:** account_access (0.9), technical_issue (0.8), urgent (0.7)
- **Actual:** account_access, security
- **Why it failed:** The model correctly identified the account access component but misclassified the security aspect as a technical issue. Additionally, it incorrectly assigned an urgency label not present in the ground truth.
- **Proposed Fix:** Incorporate few-shot examples that clearly distinguish between technical issues and security-related requests. Include examples of authentication and security procedures to improve the model's understanding of security contexts.

---

### 2.4 Performance Notes (Optional)

- **Average Latency:** 2 seconds per document
- **Cost:** Minimal computational cost
- **Model:** GPT-4o-mini

---

## Task 3: Production LLMOps Runbook

### 3.1 Deployment Architecture (AWS)

**System Diagram:**
```
GitHub → CodePipeline → ECS Fargate Container → S3 (recipes/FAISS) → OpenAI API
         ↓                    ↓                    ↓
    Auto Deploy         Bearer Token Auth     Langfuse Tracking
         ↓                    ↓                    ↓
    CloudWatch Logs ← Application Metrics ← Cost/Performance Data
```

**Components:**
- **ECS Fargate**: Containerized RAG API service with auto-scaling
- **S3**: Recipe data storage (recipe_data.json) + FAISS index files
- **AWS Secrets Manager**: OpenAI API keys + Bearer tokens + Langfuse keys
- **CloudWatch**: Application logs, metrics, and alerting
- **Langfuse**: LLM observability, cost tracking, prompt management

**Data Flow:** User request → ECS Fargate → S3 recipe retrieval → OpenAI API → Langfuse tracking → CloudWatch logging → Response

---

### 3.2 Security & Privacy

**Secrets Management:**
- OpenAI API key, Bearer authentication tokens, Langfuse API keys stored in AWS Secrets Manager
- Monthly rotation schedule for API keys with zero-downtime updates
- Environment-specific secret isolation (dev/staging/prod)

**PII Handling:**
- Recipe queries scanned for PII patterns before processing
- Automatic redaction/anonymization of detected personal information
- 30-day retention policy with encrypted storage
- GDPR compliance with data deletion rights
- Role-based access controls for sensitive data

---

### 3.3 Monitoring & KPIs (3 Dashboards)

**Dashboard 1: Quality Metrics**
- **KPIs:** Response accuracy scores, retrieval hit@3 metrics, user satisfaction ratings, prompt performance comparison
- **Alert Thresholds:** Accuracy below 85%, hit rate below 80%, satisfaction below 4.0/5
- **Tools:** Langfuse + CloudWatch

**Dashboard 2: Performance Metrics**
- **KPIs:** End-to-end API response time (<2s target), OpenAI API latency, P95/P99 latency percentiles, timeout error rates
- **Alert Thresholds:** P95 latency >3s, error rate >5%, timeout rate >1%
- **Tools:** Langfuse + CloudWatch

**Dashboard 3: Cost & Usage**
- **KPIs:** OpenAI token usage trends, daily/monthly spend tracking, cost per query analysis, ECS compute costs
- **Alert Thresholds:** Budget alerts at 80% threshold, cost per query >$0.10, daily spend >$100
- **Tools:** Langfuse + AWS Cost Explorer

---

### 3.4 Deployment & Rollback Strategy

**Evaluation in Production:**
Blue/green ECS service deployment with 10% canary traffic testing using weighted target groups and automated quality metrics validation.

**Rollback Plan:**
Instant ECS service rollback to previous task definition revision via AWS CLI with health check validation and traffic switching.

---

### 3.5 Versioning & Governance

**Version Control:**
Git-tagged releases with semantic versioning, Langfuse prompt versioning with experiment tracking, infrastructure-as-code using Terraform.

**Change Management:**
Peer review process for all changes, automated testing pipeline, staging environment validation before production deployment.

---

## Bonus: Tool Calling Interface

### Function Definition

**JSON Schema:**
```json
{
  "type": "function",
  "function": {
    "name": "search_recipes",
    "description": "Search for relevant recipes based on a cooking query. Use this when the user asks about recipes, ingredients, cooking methods, or food-related questions.",
    "parameters": {
      "type": "object",
      "properties": {
        "query": {
          "type": "string",
          "description": "The user's cooking or recipe-related query"
        },
        "k": {
          "type": "integer",
          "description": "Number of recipes to retrieve (default: 3)",
          "default": 3
        }
      },
      "required": ["query"]
    }
  }
}
```

---

### Example Interaction

**User Query:** "What vegetarian dinner options do you have?"

**Tool Call:**
```json
{
  "function": "search_recipes",
  "arguments": {
    "query": "vegetarian dinner options",
    "k": 3
  }
}
```

**Tool Response:**
```json
{
  "recipes": [
    {
      "recipe_number": 1,
      "title": "Quick Chana Masala",
      "cuisine_type": "Indian",
      "serves": 4,
      "ingredients": ["2 cans chickpeas", "1 onion diced", "3 cloves garlic minced", "1 tbsp ginger minced", "1 can crushed tomatoes", "2 tsp cumin", "2 tsp coriander", "1 tsp turmeric", "1 tsp garam masala", "Salt to taste", "Fresh cilantro"],
      "instructions": ["Heat oil in large pan", "Sauté onion until golden", "Add garlic and ginger, cook 1 minute", "Add spices, cook until fragrant", "Add tomatoes and chickpeas", "Simmer 15 minutes", "Garnish with cilantro"],
      "score": 0.85
    },
    {
      "recipe_number": 2,
      "title": "Quinoa Salad with Lemon Vinaigrette",
      "cuisine_type": "Mediterranean",
      "serves": 6,
      "ingredients": ["1 cup quinoa", "2 cups water", "1 cucumber diced", "2 tomatoes diced", "1/4 cup red onion", "1/4 cup olive oil", "2 tbsp lemon juice", "Salt and pepper"],
      "instructions": ["Rinse quinoa", "Combine quinoa and water in pot", "Bring to boil, reduce heat, cover", "Simmer 15 minutes until water absorbed", "Let sit 5 minutes, fluff with fork", "Mix with vegetables and dressing"],
      "score": 0.78
    }
  ],
  "total_found": 2
}
```

**Final Answer:** "I have several vegetarian dinner options for you! Based on Recipe 1 (Quick Chana Masala) and Recipe 2 (Quinoa Salad with Lemon Vinaigrette), here are two great choices: The Chana Masala is a flavorful Indian chickpea curry that serves 4 - you sauté onions, garlic, and ginger, add spices like cumin and garam masala, then simmer with tomatoes and chickpeas. The Quinoa Salad is a fresh Mediterranean option that serves 6 - cook quinoa for 15 minutes, then mix with diced cucumber, tomatoes, and a lemon vinaigrette. Both are nutritious and satisfying vegetarian meals!"

---

## LLM Usage Appendix

| When | Tool | Model & Version | Key Params | System Prompt | Exact Prompt Used | Why It Helped | Tool/API Calls |
|------|------|-----------------|------------|---------------|-------------------|---------------|----------------|
| [Task/Stage] | [ChatGPT/Claude/Copilot] | [Model version] | [temp, top_p, etc.] | [Yes/No, brief description] | [The actual prompt you sent] | [Specific benefit] | [None/Which tools] |
| [Task/Stage] | [Tool name] | [Model version] | [Parameters] | [System prompt used] | [The actual prompt you sent] | [Specific benefit] | [None/Which tools] |
| [Task/Stage] | [Tool name] | [Model version] | [Parameters] | [System prompt used] | [The actual prompt you sent] | [Specific benefit] | [None/Which tools] |

**Example Responses (if using LLM-as-judge):**
```
[Sample output from your evaluation prompts]
```

**Code Generation Examples (if used):**
```python
# [Show 1-2 examples where AI helped with code]
```

---

## Data & Privacy Statement

**Data Source:**  
All data used in this assessment was generated synthetically using ChatGPT for demonstration purposes. No real proprietary data, personal information (PII), or confidential information was used.

**Data Characteristics:**
- **Task 1 (RAG System)**: 15 recipe documents stored in JSON format with structured fields (title, cuisine_type, serves, ingredients, instructions, optional garnish_serving). Topics cover various international cuisines including Italian, Indian, Mediterranean, American, Mexican. Average recipe contains 5-10 ingredients and 5-8 instruction steps.
- **Task 2 (Document Tagger)**: 20 customer support ticket documents with multi-label classifications across 19 categories (account_access, billing, technical_issue, etc.). Text format with varying lengths from brief queries to detailed support requests.

**Privacy Compliance:**
This implementation demonstrates privacy-aware design suitable for handling real user data in production, including PII detection, data minimization, encryption, and retention policies as outlined in Task 1.5 and Task 3.2.

---

## Repository & Reproducibility (Optional)

**GitHub Repository:** [Link to your repo if created]

**Repository Structure:**
```
├── README.md                 # Setup and usage instructions
├── data/                     # Recipe text files (6-12 files)
├── src/
│   ├── rag_system.py        # RAG implementation
│   ├── tagger.py            # Document tagger
│   └── evaluate.py          # Evaluation script
├── prompts/                  # Saved prompts
├── results/                  # Evaluation results
└── requirements.txt          # Dependencies
```

**One-Command Reproduction:**
```bash
[Your command to run evaluations, e.g., python evaluate.py]
```

**Setup Instructions:** [Brief setup steps if repo provided]

---

## Assumptions & Decisions

1. **Recipe chunking strategy**: Assumed each recipe should be treated as a single document rather than splitting into sections, as recipes are typically consumed as complete units
2. **Evaluation methodology**: Used manual scoring for generation quality assessment rather than automated metrics, as recipe accuracy requires domain knowledge
3. **Production architecture**: Assumed AWS deployment over other cloud providers based on common enterprise preferences and service maturity
4. **Tool calling implementation**: Assumed function calling approach would provide better user experience than traditional RAG for conversational interactions
5. **Data privacy**: Assumed production deployment would handle recipe queries (low PII risk) but designed framework to accommodate higher-risk data types

---

## References & Tools

**Libraries Used:**
- sentence-transformers==2.2.2
- faiss-cpu==1.7.4
- numpy==1.24.3
- openai==1.3.0
- python-dotenv==1.0.0

**External Resources:**
- OpenAI API documentation for embeddings and chat completions
- FAISS documentation for vector similarity search
- Sentence Transformers documentation for embedding models

**AI Assistance:**
- ChatGPT used to generate synthetic recipe data and customer support tickets for demonstration purposes
- No AI assistance used for code implementation or system design

---

**Total Time Spent:** 5 Hour 30 min  
**Submission Date:** 12th November 2025
