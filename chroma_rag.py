from langchain_community.document_loaders import DirectoryLoader, CSVLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
import shutil
import argparse

DATA_PATH = "data/curated/rag"
CHROMA_PATH = "chroma"

def load_documents():
    print("Loading documents...")
    document_loader = DirectoryLoader(
        path=DATA_PATH,
        glob="**/*.csv",
        loader_cls=CSVLoader,
    )
    return document_loader.load()


def save_to_chroma(documents: list[Document]):
    print("Saving embeddings to chromaDB...")
    Chroma.from_documents(documents, OpenAIEmbeddings(), persist_directory=CHROMA_PATH)

    print(f"Saved {len(documents)} chunks to {CHROMA_PATH}.")
    print()


def print_results(sim_search_results):
    print("Similarity search results for the entered query:")
    for doc, score in sim_search_results:
        print(doc.page_content)
        print("Similarity score:", score)
        print()


def query_rag(query, k_value=3, print_results_log=False):
    print("Processing query...")

    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    results = db.similarity_search_with_relevance_scores(query, k=k_value)
    if len(results) == 0:
        print(f"Unable to find matching results.")
    elif results[0][1] < 0.7:
        print(f"WARNING: Query has low similarity to stored embeddings ({results[0][1]})")

    if print_results_log:
        print_results(results)

    context_text = "\n\n".join([doc.page_content for doc, _ in results])

    prompt_template = """
            You are the LLM generator in a RAG movie recommendation system. In this system, you must answers questions based
            on the provided context. Use the context to answer the question, and if the answer is not in the context, find
            the closest answer available from the context. Do not make up information.

            Context: {context}
            Question: {question}
            """

    prompt_template = ChatPromptTemplate.from_template(prompt_template)
    prompt = prompt_template.format(context=context_text, question=query)

    model = ChatOpenAI()
    response = model.invoke(prompt)

    # source = [doc.metadata.get("source", None) for doc, _score in results]

    return response


if __name__ == "__main__":
    print(os.getenv("OPENAI_API_KEY"))
    if not os.getenv("OPENAI_API_KEY"):
        print("OpenAI API key not set.")
        exit(1)

    parser = argparse.ArgumentParser(description="Specify hyperparameters for query similarity search.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose mode: Prints results from query similarity search to stdout.")
    parser.add_argument("-k", type=int, default=3,
                        help="k (int): Number of Documents to return in query similarity search (default: 3)")
    args = parser.parse_args()

    if os.path.exists(CHROMA_PATH):
        response = input("ChromaDB already has stored embeddings in the given chroma directory. "
                           "Would you like to overwrite these embeddings? [y/n]: ")
        print()
        if response.lower() == "y":
            print("Deleting existing embeddings...")
            shutil.rmtree(CHROMA_PATH)
            load_dotenv()
            documents = load_documents()
            save_to_chroma(documents)
    else:
        load_dotenv()
        documents = load_documents()
        save_to_chroma(documents)

    while True:
        query_text = input("Please enter your query: ")

        response_text = query_rag(query_text, args.k, args.verbose)
        print(response_text.content)
        print()