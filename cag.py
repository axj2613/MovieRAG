from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import CSVLoader
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationChain
from langchain.schema import SystemMessage
import argparse
import warnings

def load_documents(path):
    print("Loading documents...")
    document_loader = CSVLoader(file_path=path)
    documents = document_loader.load()
    context_text = "\n\n".join([doc.page_content for doc in documents])
    return context_text

def load_model(context_text, verbose_flag):
    print("Loading model...")
    model = ChatOpenAI()
    system_message = f"""
    You are the LLM generator in a CAG movie recommendation system. In this system, you must answers questions based
    on the provided context. Use the context to answer the question, and if the answer is not in the context, find
    the closest answer available from the context. Do not make up information.
    
    Context:
    {context_text}
    """

    # Create memory to maintain conversation context
    print("Creating memory...")
    memory = ConversationBufferMemory(return_messages=True)
    memory.chat_memory.add_message(SystemMessage(content=system_message))
    conversation_chain = ConversationChain(
        llm=model,
        memory=memory,
        verbose=verbose_flag,
    )
    return conversation_chain

def answer_question(conversation_model, question):
    response = conversation_model.predict(input=question)
    return response

if __name__ == '__main__':
    warnings.filterwarnings("ignore", message=".*LangChain.*")

    parser = argparse.ArgumentParser(description="Specify if you want the model to be verbose.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose mode: Prints results from query similarity search to stdout.")
    args = parser.parse_args()
    context = load_documents("data/curated/cag/movie_curated.csv")
    conversation = load_model(context, args.verbose)
    while True:
        print()
        question_prompt = input("Enter Prompt: ")
        answer = answer_question(conversation, question_prompt)
        print("Answer:", answer)