import json
import os
import pickle
import numpy as np
import faiss
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class RecipeVectorStore:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.index = None
        self.recipes = []
        self.embeddings = None
        
    def load_recipes(self, json_path):
        with open(json_path, 'r') as f:
            data = json.load(f)
        self.recipes = data['recipes']
        print(f"Loaded {len(self.recipes)} recipes")
        
    def create_recipe_text(self, recipe):
        parts = [
            f"Title: {recipe['title']}",
            f"Cuisine: {recipe['cuisine_type']}",
            f"Serves: {recipe['serves']}",
            "Ingredients: " + ", ".join(recipe['ingredients']),
            "Instructions: " + " ".join(recipe['instructions'])
        ]
        
        if 'preparation' in recipe:
            parts.append("Preparation: " + " ".join(recipe['preparation']))
            
        if 'garnish_serving' in recipe:
            parts.append(f"Serving: {recipe['garnish_serving']}")
            
        return " ".join(parts)
    
    def get_embeddings(self, texts):
        print("Getting embeddings from OpenAI...")
        embeddings = []
        
        for i, text in enumerate(texts):
            try:
                response = self.client.embeddings.create(
                    model="text-embedding-3-small",
                    input=text
                )
                embeddings.append(response.data[0].embedding)
                print(f"Processed {i+1}/{len(texts)} recipes")
            except Exception as e:
                print(f"Error processing recipe {i}: {e}")
                embeddings.append([0.0] * 1536)
                
        return np.array(embeddings, dtype=np.float32)
    
    def build_index(self):
        if not self.recipes:
            print("No recipes loaded")
            return
            
        recipe_texts = [self.create_recipe_text(recipe) for recipe in self.recipes]
        self.embeddings = self.get_embeddings(recipe_texts)
        
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        
        faiss.normalize_L2(self.embeddings)
        self.index.add(self.embeddings)
        
        print(f"Built FAISS index with {self.index.ntotal} recipes")
    
    def save_index(self, index_path="recipe_embeddings.faiss", metadata_path="recipe_metadata.pkl"):
        if self.index is None:
            print("No index to save")
            return
            
        faiss.write_index(self.index, index_path)
        
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.recipes, f)
            
        print(f"Saved index to {index_path} and metadata to {metadata_path}")
    
    def load_index(self, index_path="recipe_embeddings.faiss", metadata_path="recipe_metadata.pkl"):
        if os.path.exists(index_path) and os.path.exists(metadata_path):
            self.index = faiss.read_index(index_path)
            
            with open(metadata_path, 'rb') as f:
                self.recipes = pickle.load(f)
                
            print(f"Loaded index with {self.index.ntotal} recipes")
            return True
        return False
    
    def search(self, query, k=3):
        if self.index is None:
            print("No index loaded")
            return []
            
        try:
            response = self.client.embeddings.create(
                model="text-embedding-3-small",
                input=query
            )
            query_embedding = np.array([response.data[0].embedding], dtype=np.float32)
            faiss.normalize_L2(query_embedding)
            
            scores, indices = self.index.search(query_embedding, k)
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.recipes):
                    results.append({
                        'recipe': self.recipes[idx],
                        'score': float(score)
                    })
                    
            return results
        except Exception as e:
            print(f"Search error: {e}")
            return []

def main():
    store = RecipeVectorStore()
    
    if store.load_index():
        print("Using existing index")
    else:
        print("Building new index...")
        store.load_recipes('recipe_data.json')
        store.build_index()
        store.save_index()
    
    while True:
        query = input("\nSearch recipes: ").strip()
        if query.lower() in ['quit', 'exit']:
            break
            
        results = store.search(query)
        for i, result in enumerate(results, 1):
            recipe = result['recipe']
            print(f"\n{i}. {recipe['title']} (score: {result['score']:.3f})")

if __name__ == "__main__":
    main()
