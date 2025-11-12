import os
from openai import OpenAI
from dotenv import load_dotenv
from vector_store import RecipeVectorStore

load_dotenv()

class RAGRecipeChat:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.vector_store = RecipeVectorStore()
        
    def setup(self):
        if self.vector_store.load_index():
            print("Recipe database ready")
            return True
        else:
            print("Building recipe database...")
            self.vector_store.load_recipes('recipe_data.json')
            self.vector_store.build_index()
            self.vector_store.save_index()
            print("Recipe database ready")
            return True
    
    def create_context(self, results):
        if not results:
            return "No relevant recipes found."
            
        context = "Here are the relevant recipes from my database:\n\n"
        
        for i, result in enumerate(results, 1):
            recipe = result['recipe']
            context += f"Recipe {i}: {recipe['title']}\n"
            context += f"Cuisine: {recipe['cuisine_type']}\n"
            context += f"Serves: {recipe['serves']}\n"
            
            context += "Ingredients:\n"
            for ingredient in recipe['ingredients']:
                context += f"- {ingredient}\n"
                
            context += "Instructions:\n"
            for j, step in enumerate(recipe['instructions'], 1):
                context += f"{j}. {step}\n"
                
            if 'garnish_serving' in recipe:
                context += f"Serving: {recipe['garnish_serving']}\n"
                
            context += "\n---\n\n"
            
        return context
    
    def generate_response(self, query, context):
        system_prompt = """You are a helpful cooking assistant. Answer cooking questions based only on the provided recipe context.

Requirements:
- Use only information from the provided recipes
- Always cite which recipes you reference
- If the recipes don't contain relevant information, say "I don't have information about that in my recipe collection"
- Keep responses practical and helpful
- Focus only on cooking and recipe topics"""

        user_prompt = f"""Context:
{context}

User Question: {query}

Based on the recipe information above, answer the user's question. Remember to cite which recipes you're referencing."""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_completion_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {e}"
    
    def ask(self, query):
        results = self.vector_store.search(query, k=3)
        context = self.create_context(results)
        response = self.generate_response(query, context)
        return response

def main():
    chat = RAGRecipeChat()
    
    if not chat.setup():
        print("Failed to setup recipe database")
        return
    
    print("RAG Recipe Assistant ready!")
    print("Ask me anything about cooking and recipes.")
    
    while True:
        try:
            question = input("\nYou: ").strip()
            
            if question.lower() in ['quit', 'exit', 'bye']:
                break
                
            if not question:
                continue
                
            print("\nAssistant: ", end="")
            answer = chat.ask(question)
            print(answer)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    main()
