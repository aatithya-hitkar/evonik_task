import json
import time
from rag_query import RAGRecipeChat

def calculate_hit_at_k(retrieved_recipes, relevant_recipes, k=3):
    if not relevant_recipes:
        return 1.0 if not retrieved_recipes else 0.0
    
    retrieved_titles = [r['recipe']['title'] for r in retrieved_recipes[:k]]
    return 1.0 if any(title in relevant_recipes for title in retrieved_titles) else 0.0

def calculate_recall_at_k(retrieved_recipes, relevant_recipes, k=3):
    if not relevant_recipes:
        return 1.0 if not retrieved_recipes else 0.0
    
    retrieved_titles = [r['recipe']['title'] for r in retrieved_recipes[:k]]
    found = sum(1 for title in relevant_recipes if title in retrieved_titles)
    return found / len(relevant_recipes)

def run_evaluation():
    chat = RAGRecipeChat()
    chat.setup()
    
    with open('evaluation_dataset.json', 'r') as f:
        data = json.load(f)
    
    results = []
    hit_scores = []
    recall_scores = []
    
    for test_case in data['test_cases']:
        start_time = time.time()
        
        retrieved = chat.vector_store.search(test_case['question'], k=3)
        response = chat.ask(test_case['question'])
        
        latency = time.time() - start_time
        
        hit_score = calculate_hit_at_k(retrieved, test_case['relevant_recipes'])
        recall_score = calculate_recall_at_k(retrieved, test_case['relevant_recipes'])
        
        hit_scores.append(hit_score)
        recall_scores.append(recall_score)
        
        results.append({
            'id': test_case['id'],
            'question': test_case['question'],
            'retrieved_recipes': [r['recipe']['title'] for r in retrieved],
            'response': response,
            'hit_at_3': hit_score,
            'recall_at_3': recall_score,
            'latency': latency
        })
    
    avg_hit = sum(hit_scores) / len(hit_scores)
    avg_recall = sum(recall_scores) / len(recall_scores)
    
    print(f"Hit@3: {avg_hit:.3f}")
    print(f"Recall@3: {avg_recall:.3f}")
    
    with open('evaluation_results.json', 'w') as f:
        json.dump({
            'metrics': {
                'hit_at_3': avg_hit,
                'recall_at_3': avg_recall
            },
            'results': results
        }, f, indent=2)

if __name__ == "__main__":
    run_evaluation()
