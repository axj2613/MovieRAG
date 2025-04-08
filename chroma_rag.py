from langchain_community.document_loaders import DirectoryLoader, DataFrameLoader, CSVLoader
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.schema import Document
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

import pandas as pd
import os
import shutil

DATA_PATH = "data/curated"
CHROMA_PATH = "chroma"

def sample_tsv_loader(file_path):
    df = pd.read_csv(file_path)
    df['content'] = df[df.columns].astype(str).agg(' '.join, axis=1)
    return DataFrameLoader(df, page_content_column="content")


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


def query_rag(query):
    print("Processing query...")

    embedding_function = OpenAIEmbeddings()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)
    results = db.similarity_search_with_relevance_scores(query, k=3)
    if len(results) == 0:
        print(f"Unable to find matching results.")
    elif results[0][1] < 0.7:
        print(f"WARNING: Query has low similarity to stored embeddings ({results[0][1]})")

    context_text = "\n\n - -\n\n".join([doc.page_content for doc, _score in results])
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
    if os.path.exists(CHROMA_PATH):
        response = input("ChromaDB already has stored embeddings in the given chroma directory. "
                           "Would you like to overwrite these embeddings? [y/n]: ")
        if response.lower() == "y":
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

        response_text = query_rag(query_text)
        print("Response:", response_text.content)
        print()