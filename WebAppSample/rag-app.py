import os
from dotenv import load_dotenv
from openai import AzureOpenAI

def main():
    os.system("cls" if os.name == "nt" else "clear")

    # Get environment variables
    load_dotenv()

    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_endpoint = os.getenv("OPENAI_ENDPOINT")
    chat_deployment_name = os.getenv("CHAT_DEPLOYMENT_NAME")
    embedding_deployment_name = os.getenv("EMBEDDING_DEPLOYMENT_NAME")
    search_endpoint = os.getenv("SEARCH_ENDPOINT")
    search_api_key = os.getenv("SEARCH_API_KEY")
    search_index_name = os.getenv("SEARCH_INDEX_NAME")
    
    # initialize Azure OpenAI client
    chat_client = AzureOpenAI(
        api_key=openai_api_key,
        azure_endpoint=openai_endpoint,
        api_version="2025-04-14",
    )

    #initialize prompt with system message
    prompt = [
        {
            "role": "system",
            "content": "You are a travel assistant that provides information on travel service"
        }
    ]

    while True:
        input_text = input("Enter your question (or 'exit' to quit): ")
        if input_text.lower() == 'exit':
            print("Exiting the application.")
            break
        elif input_text.strip() == "":
            print("Please enter a valid question.")
            continue

        prompt.append(
            {
                "role": "user",
                "content": input_text
            }
        )

        # Additional parameters to apply RAG pattern using the AI Search index
        rag_params = {
            "data_source":{
                "type":"azure_search",
                "parameters":{
                    "endpoint": search_endpoint,
                    "index_name": search_index_name,
                    "authentication": {
                        "type": "api_key",
                        "api_key": search_api_key,
                    },
                    "query_type": "vector",
                    "embedding_dependency_name":
                    {
                        "type": "deployment_name",
                        "deployment_name": embedding_deployment_name       
                    }
                },
            }
        }

        response = chat_client.chat.completions.create(
            model=chat_deployment_name,
            messages=prompt,
            extra_body=rag_params
        )

        completion = response.choices[0].message.content
        print(f"AI: {completion}")

        prompt.append(
            {
                "role": "assistant",
                "content": completion
            }
        )


if __name__ == "__main__":
    main()