from langchain_neo4j import GraphCypherQAChain, Neo4jGraph
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
import logging
import argparse, os

logging.getLogger("neo4j").setLevel(logging.ERROR)

def get_graph():
    graph = Neo4jGraph(
        url=os.getenv("NEO4J_URI"),
        username=os.getenv("NEO4J_USERNAME"),
        password=os.getenv("NEO4J_PASSWORD")
    )
    return graph

def get_cypher_chain(graph, verbose=False):
    qa_prompt_template = """
        You are the QA LLM in a RAG movie recommendation system with access to a Neo4j graph database. Your task is to answer user questions about movies based EXCLUSIVELY on the context provided from database query results.

        The graph database contains:
        - Person nodes with name properties
        - Movie nodes with name, originalTitle, isAdult, and runtimeMinutes properties
        - Genre nodes with name properties
        - Year nodes with year properties
        - Relationships between Person and Movie (ACTED, DIRECTED, WROTE, etc.)
        - FROM relationships between Movie and Genre
        - RELEASED relationships between Movie and Year
    
        IMPORTANT INSTRUCTIONS:
        1. Base your answer SOLELY on the database results provided in the context
        2. Include specific movies, people, genres, years, and other details from the context in your answer
        3. If the context contains multiple results, summarize them appropriately
        4. Do not make up or infer information not present in the context
        5. If the context is insufficient to answer the question, clearly state this
        6. Format your answers in a clear, readable way
        7. When listing movies or other entities from the context, be comprehensive
    
        CONTEXT:
        User question: {question}
        Database results: {context}
    
        Your response should directly answer the user's question using ONLY the information found in the database results.
    """
    qa_prompt = PromptTemplate(
        template=qa_prompt_template,
        input_variables=["question", "context"]
    )

    cypher_prompt_template = """
    You are a Cypher query generator for a Neo4j graph database in a movie recommendation system. The graph data model 
    is as follows:
    Person, Movie, Genre, and Year are nodes. Person has a "name" string type property. Movie has "name" and 
    "originalTitle" string type properties, an "isAdult" boolean type property, and a "runtimeMinutes" integer type 
    property. Genre has a "name" string type property. Year has a "year" integer type property. Person has ACTED, 
    DIRECTED, WROTE, PRODUCED, COMPOSED, CINEMATOGRAPHED, EDITED, DESIGNED PRODUCTION, SELF, DIRECTED CASTING, ARCHIVED 
    FOOTAGE, or ARCHIVED SOUND relationships with Movie, while Movie has a FROM relationship with Genre and a RELEASED 
    relationship with Year. All these relationships are one-to-one so each Person node holds a singular person, each 
    Movie node holds a single movie, a Genre node holds a single genre, and a Year node holds a single year. Treat 
    each word describing genre as an independent singular genre. A movie is considered appropriate for all ages or family 
    audiences if its boolean value isAdult is 0.

    Your task is to convert user questions into Cypher queries that will extract the relevant information from the graph database.

    When the user asks for movie recommendations similar to a specific movie, you should generate a query that:
    1. Identifies the reference movie by name
    2. Finds other movies that share connections through:
       - Common cast and crew (Person nodes with relationships to both movies)
       - Similar genres (Genre nodes connected to both movies)
       - Release years within a reasonable range (e.g., ±5 years)
    3. Calculates a similarity score based on the number of shared connections
    4. Returns the most similar movies ranked by this score

    User question: {question}

    Generate a Cypher query that answers this question. Make sure to:
    1. Use appropriate node and relationship labels as defined in the schema
    2. Format the query clearly with proper syntax
    3. Consider all relevant constraints and relationships
    4. Return only the information needed to answer the question
    5. For similarity queries, use a weighted scoring system that prioritizes shared Person connections, Genre matches, and Year proximity

    Cypher query:
    """

    cypher_prompt = PromptTemplate(
        template=cypher_prompt_template,
        input_variables=["question"]
    )

    cypher_chain = GraphCypherQAChain.from_llm(
        cypher_llm=ChatOpenAI(temperature=0.2, model_name='gpt-4'),
        qa_llm=ChatOpenAI(temperature=0),
        graph=graph,
        qa_prompt=qa_prompt,
        cypher_prompt=cypher_prompt,
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
            print()
            print()
            print(answer['result'])
            print()