# MovieRAG

## Overview

MovieRAG is a Retrieval-Augmented Generation application that uses an external movie data source (IMDb) to provide context-aware
responses to movie recommendation requests. It combines a ChromaDB based retriever with an OpenAI generator. The retriever
fetches relevant vector-embedded movie data (based on user prompt) and provides it to the generator with the original 
user’s query. The generator uses this additional context to generate an accurate and relevant response.

Update: This application now also supports CAG capabilities on a smaller dataset.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Features](#features)

## Installation

Ensure you have the necessary dependencies installed by running:

```
pip install -r requirements.txt 
```

## Usage

### Curate Dataset (Optional)
Raw IMDb structured data has already been curated for word embedding based RAG usage. This curated data has been stored 
as `data/curated/movie_curated.csv`. This step can be skipped if the existing curated data is satisfactory.
#### 1. Download Raw Data
Download the following four [IMDb Non-Commercial Datasets](https://datasets.imdbws.com/) and move them to the `data/raw`
directory:
1. `name.basics.tsv`
2. `title.basics.tsv`
3. `title.principals.tsv`
4. `title.ratings.tsv`

#### 2. Execute Data Curator
The data curator will use the .tsv data in `data/raw` to create a curated .csv movie data set in `data/curated`, 
formatted and structured to allow for useful word embeddings. With default settings, this application takes approximately
2 minutes to run to completion on my computer.
```
python data_curator.py [-h] [-r RATING] [-v VOTE] [-c]
```
* -h, --help: Show the help message and exit.
* -r RATING, --rating RATING: Minimum rating required for a movie to be included in the curated dataset.
Type: float | Default: 7.0 
* -v VOTE, --vote VOTE: Minimum number of votes required for a movie to qualify.
Type: int | Default: 1000
* -c, --cag: Store curated data in the `data/curated/cag` folder (as opposed to the default `data/curated/rag` folder)

### Export OpenAI API key

To authenticate your API reference with OpenAI, [create an API key](https://platform.openai.com/api-keys) and [set 
environment variable](https://help.openai.com/en/articles/5112595-best-practices-for-api-key-safety) `OPENAI_API_KEY`.

### Running MovieRAG

To execute the MovieRAG application, run:

```
python chroma_rag.py [-h] [-v] [-k K]
```
* -h, --help: Show help message and exit.
* -v, --verbose: Enable verbose mode to print results from the query similarity search.
* -k K: Specify the number of documents to return from the query similarity search (default: 3).

### Running MovieCAG

To execute the MovieCAG application, run:

```
python cag.py [-h] [-v]
```
* -h, --help: Show help message and exit.
* -v, --verbose: Enable verbose mode to print the entire input fed into the chat model.

## Features
* #### Retrieval-Augmented Generation (RAG)
    Combines ChromaDB-based document retrieval with OpenAI's GPT to generate context-aware movie recommendations.
* #### Cache-Augmented Generation (CAG)
    Provides a cache memory to OpenAI's GPT to generate context-aware movie recommendations.
* #### Context-Enriched Responses
    Enhances natural language queries using semantically relevant data pulled from a curated IMDb dataset.
* #### Custom Curated Dataset
    Includes a script to process raw IMDb .tsv data into a clean .csv format optimized for word embeddings and vector search.
* ##### Flexible Query Parameters
    Easily configure the number of context documents returned with -k, or enable debug mode with -d for insight into retrieval results.
* #### Modular Design for Experimentation
    Clean separation between data curation, retrieval, and generation logic for easier experimentation and extension.