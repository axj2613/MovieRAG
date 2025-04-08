# MovieRAG

## Overview

MovieRAG is a Retrieval-Augmented Generation application that uses an external movie data source (IMDb) to provide context-aware
responses to movie recommendation requests. It combines a ChromaDB based retriever with an OpenAI generator. The retriever
fetches relevant vector-embedded movie data (based on user prompt) and provides it to the generator with the original 
user’s query. The generator uses this additional context to generate an accurate and relevant response.

## Installation

Ensure you have the necessary dependencies installed by running:

```
pip install -r requirements.txt 
```

## Usage

### Running MovieRAG

To execute the MovieRAG application, run:

```
python chroma_rag.py
```