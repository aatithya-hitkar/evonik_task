# Operations Documentation

## Logging Fields

1. **input_query** - User's original question
2. **retrieved_recipe_ids** - IDs/titles of recipes returned by vector search
3. **final_answer** - Generated response sent to user
4. **response_latency** - Time taken to process query (seconds)
5. **token_cost** - Estimated cost based on OpenAI API usage

## Privacy Considerations

The system processes user queries through OpenAI's API, which means query data is sent to a third-party service. Recipe data is stored locally and not transmitted except as context for generation. Users should be informed that their cooking questions may be processed by OpenAI for response generation. No personal information beyond cooking queries is collected or stored.
