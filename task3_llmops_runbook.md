# Task 3 — LLMOps Production Runbook

## Production Deployment Architecture

### Components & Data Flow
```
GitHub → CodePipeline → ECS Fargate Container → S3 (recipes/FAISS) → OpenAI API
         ↓                    ↓                    ↓
    Auto Deploy         Bearer Token Auth     Langfuse Tracking
         ↓                    ↓                    ↓
    CloudWatch Logs ← Application Metrics ← Cost/Performance Data
```

**Core AWS Services:**
- **ECS Fargate**: Containerized RAG API service with auto-scaling
- **S3**: Recipe data storage (`recipe_data.json`) + FAISS index files
- **AWS Secrets Manager**: OpenAI API keys + Bearer tokens + Langfuse keys
- **CloudWatch**: Application logs, metrics, and alerting
- **Langfuse**: LLM observability, cost tracking, prompt management

## Secrets Management & PII Handling

**Secrets Storage:**
- OpenAI API key, Bearer authentication tokens, Langfuse API keys stored in AWS Secrets Manager
- Monthly rotation schedule for API keys with zero-downtime updates
- Environment-specific secret isolation (dev/staging/prod)

## Monitoring Dashboards & KPIs

### 1. Quality Dashboard (Langfuse + CloudWatch)
- Response accuracy scores, retrieval hit@3 metrics, user satisfaction ratings
- Prompt performance comparison, A/B test results, quality degradation alerts

### 2. Latency Dashboard (Langfuse + CloudWatch)
- End-to-end API response time (<2s target), OpenAI API latency, ECS container startup time
- P95/P99 latency percentiles, timeout error rates, geographic response times

### 3. Cost Dashboard (Langfuse + AWS Cost Explorer)
- OpenAI token usage trends, daily/monthly spend tracking, cost per query analysis
- ECS compute costs, S3 storage costs, budget alerts at 80% threshold

## Evaluation in Production & Rollback

**Eval-in-Prod:** Blue/green ECS service deployment with 10% canary traffic testing using weighted target groups and automated quality metrics validation.

**Rollback Plan:** Instant ECS service rollback to previous task definition revision via AWS CLI with health check validation and traffic switching.

## Versioning & Configuration Governance

**Governance:** Git-tagged releases with semantic versioning, Langfuse prompt versioning with experiment tracking, infrastructure-as-code using Terraform with peer review process.

---

## Optional Bonus — Tool Calling Interface

### Function Definition
```json
{
  "name": "search_corpus",
  "description": "Search recipe database for cooking-related queries",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "User's cooking question or recipe search term"
      },
      "top_k": {
        "type": "integer",
        "description": "Number of top recipes to retrieve",
        "default": 5,
        "minimum": 1,
        "maximum": 10
      }
    },
    "required": ["query"]
  }
}
```

### Example Interaction
```json
// Request
{
  "function": "search_corpus",
  "arguments": {
    "query": "vegetarian pasta recipes",
    "top_k": 3
  }
}

// Response
{
  "recipes": [
    {"title": "Creamy Mushroom Pasta", "score": 0.89},
    {"title": "Spinach Pesto Linguine", "score": 0.84},
    {"title": "Tomato Basil Penne", "score": 0.78}
  ],
  "generated_response": "Here are 3 vegetarian pasta recipes from my collection..."
}
```

---

## LLM Usage Appendix

| When | Tool | Model & Version | Key Params | System Prompt? | Exact Prompt Used | Why It Helped | Tool/API Calls? |
|------|------|----------------|------------|----------------|-------------------|---------------|-----------------|
| Architecture Design | Claude 3.5 Sonnet | claude-3-5-sonnet-20241022 | temp=0.7 | Yes - Technical architect | "Design a production LLMOps architecture for RAG system using AWS ECS, focusing on scalability and cost optimization" | Provided comprehensive AWS service recommendations and best practices | None |
| Monitoring Strategy | Claude 3.5 Sonnet | claude-3-5-sonnet-20241022 | temp=0.3 | Yes - DevOps expert | "Define 3 key dashboards for monitoring LLM applications in production: quality, latency, and cost metrics" | Structured monitoring approach with specific KPIs and alerting thresholds | None |
