import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from vector_store import RecipeVectorStore

load_dotenv()

class ToolRAGRecipeChat:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.vector_store = RecipeVectorStore()
        self.tools = [
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
        ]
        
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
    
    def search_recipes(self, query, k=3):
        """Tool function to search for relevant recipes"""
        results = self.vector_store.search(query, k=k)
        
        if not results:
            return {"recipes": [], "message": "No relevant recipes found."}
            
        formatted_recipes = []
        for i, result in enumerate(results, 1):
            recipe = result['recipe']
            formatted_recipe = {
                "recipe_number": i,
                "title": recipe['title'],
                "cuisine_type": recipe['cuisine_type'],
                "serves": recipe['serves'],
                "ingredients": recipe['ingredients'],
                "instructions": recipe['instructions'],
                "score": result['score']
            }
            
            if 'garnish_serving' in recipe:
                formatted_recipe['garnish_serving'] = recipe['garnish_serving']
                
            formatted_recipes.append(formatted_recipe)
            
        return {
            "recipes": formatted_recipes,
            "total_found": len(formatted_recipes)
        }
    
    def execute_tool_call(self, tool_call):
        """Execute the tool call and return results"""
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        if function_name == "search_recipes":
            return self.search_recipes(
                query=function_args.get("query"),
                k=function_args.get("k", 3)
            )
        else:
            return {"error": f"Unknown function: {function_name}"}
    
    def ask(self, query):
        system_prompt = """You are a helpful cooking assistant. You have access to a recipe database through the search_recipes function.

When users ask cooking or recipe-related questions:
1. Use the search_recipes function to find relevant recipes
2. Answer based only on the retrieved recipe information
3. Always cite which recipes you reference (by recipe number and title)
4. If no relevant recipes are found, say "I don't have information about that in my recipe collection"
5. Keep responses practical and helpful
6. Focus only on cooking and recipe topics

For non-cooking questions, politely redirect to cooking topics."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": query}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                tools=self.tools,
                tool_choice="auto",
                temperature=0.7,
                max_completion_tokens=2000
            )
            
            response_message = response.choices[0].message
            
            if response_message.tool_calls:
                messages.append(response_message)
                
                for tool_call in response_message.tool_calls:
                    tool_result = self.execute_tool_call(tool_call)
                    
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": tool_call.function.name,
                        "content": json.dumps(tool_result)
                    })
                
                final_response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.7,
                    max_completion_tokens=500
                )
                
                return final_response.choices[0].message.content
            else:
                return response_message.content
                
        except Exception as e:
            return f"Error generating response: {e}"

def main():
    chat = ToolRAGRecipeChat()
    
    if not chat.setup():
        print("Failed to setup recipe database")
        return
    
    print("Tool-based RAG Recipe Assistant ready!")
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
