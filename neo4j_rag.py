from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import argparse, os

def get_graph():
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD")
    )
    return graph

def get_cypher_chain(graph, verbose=False):
    prompt_template = """
        You are the QA LLM in a RAG movie recommendation system with access to a Neo4j graph database. In this system, 
        you must answers questions based on the provided context. Base your answer solely on the database results 
        provided. Do not make up information.

        CONTEXT:
        The user asked the question: {question}
        The query returned the following results from the database: {context}
    """
    qa_prompt = PromptTemplate(
        template=prompt_template,
        input_variables=["question", "context"]
    )

    cypher_chain = GraphCypherQAChain.from_llm(
        cypher_llm=ChatOpenAI(temperature=0, model_name='gpt-4'),
        qa_llm=ChatOpenAI(temperature=0),
        graph=graph,
        qa_prompt=qa_prompt,
        verbose=verbose,
        allow_dangerous_requests=True,
        return_only_outputs=False
    )
    return cypher_chain


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Specify hyperparameters for query similarity search.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose mode: Prints results from query similarity search to stdout.")
    args = parser.parse_args()

    while True:
        neo4j = get_graph()
        qa_chain = get_cypher_chain(neo4j, args.verbose)
        while True:
            query_text = input("Please enter your query: ")
            answer = qa_chain.invoke({'query': query_text})
            print(answer['result'])
            print()