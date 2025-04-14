import argparse

import pandas as pd

def filter_movies(file_path):
    basics_df = pd.read_csv(file_path, delimiter='\t', low_memory=False)
    print("Filtering movies...")

    movie_df = basics_df[basics_df['titleType'] == "movie"]
    print("Total entries:", len(basics_df), "\nMovie entries:", len(movie_df))
    print()
    return movie_df


def filter_by_ratings(file_path, movie_df, min_votes=1000, min_rating=7.0):
    ratings_df = pd.read_csv(file_path, delimiter='\t')
    print("Filtering movies by ratings and popularity...")

    movie_ratings_df = ratings_df[ratings_df['tconst'].isin(movie_df['tconst'])]
    # Popular movies must have a rating of over 7.0 based on more than 1000 votes
    popular_movies_df = movie_ratings_df[(movie_ratings_df['numVotes'] > min_votes) & (movie_ratings_df['averageRating'] > min_rating)]
    print("Movie ratings:", len(movie_ratings_df), "\nFiltered popular movie ratings:", len(popular_movies_df))

    # popular_movies_df.to_csv("data/curated/title.ratings.csv", index=False)
    # print("Curated movie ratings saved!")
    print()

    return popular_movies_df['tconst'].tolist()


def filter_title_basics(basics_df, movies_list):
    print("Filtering movie titles from the basics dataset...")
    filtered_basics_df = basics_df[basics_df['tconst'].isin(movies_list)]
    filtered_basics_df.loc[:, 'genres'] = filtered_basics_df['genres'].str.replace(',', ' ')
    print("Total entries:", len(basics_df), "\nFiltered length:", len(filtered_basics_df))

    trimmed_basics_df = filtered_basics_df.drop(columns=['tconst', 'titleType', 'endYear'])

    # trimmed_basics_df.to_csv("data/curated/title.basics.csv", index=False)
    # print("Curated title basics saved!")
    print()

    return filtered_basics_df


def subset_cast_crew(principals_df):
    actors_df = principals_df[principals_df['category'].isin(['actor', 'actress'])]
    directors_df = principals_df[principals_df['category'] == 'director']
    writers_df = principals_df[principals_df['category'] == 'writer']

    actors_grouped = actors_df.groupby('tconst').head(2)
    directors_grouped = directors_df.groupby('tconst').head(1)
    writers_grouped = writers_df.groupby('tconst').head(1)

    concat_df = pd.concat([actors_grouped, directors_grouped, writers_grouped]).sort_index()
    print("Total entries:", len(principals_df), "\nSubset length:", len(concat_df))
    return concat_df


def filter_title_principals(file_path, movies_list, movies_df, people_df, folder):
    principals_df = pd.read_csv(file_path, delimiter='\t')
    print("Filtering movie titles from the principals dataset...")
    filtered_principals_df = principals_df[principals_df['tconst'].isin(movies_list)]

    filtered_principals_df = subset_cast_crew(filtered_principals_df)


    merged_movies_df = filtered_principals_df.merge(movies_df[['tconst', 'originalTitle']], on='tconst', how='left')
    merged_names_df = merged_movies_df.merge(people_df[['nconst', 'primaryName']], on='nconst', how='left')

    grouped_names_df = merged_names_df.groupby(['originalTitle', 'category'])['primaryName'].apply(lambda x: ' '.join(str(name) for name in x if pd.notnull(name)))
    grouped_names_df = grouped_names_df.reset_index()
    pivot_df = grouped_names_df.pivot(index='originalTitle', columns='category', values='primaryName')
    pivot_df = pivot_df.reset_index()

    result_df = pivot_df.merge(movies_df[['originalTitle', 'isAdult', 'startYear', 'runtimeMinutes', 'genres']], on='originalTitle', how='left')

    # result_df.to_csv("data/curated/title.principals.csv", index=False)
    result_df.to_csv("data/curated/" + folder + "/movie_curated.csv", index=False)
    print("Curated title principals saved!")
    print()

    return merged_names_df['nconst'].tolist()


def get_name_basics(file_path):
    return pd.read_csv(file_path, delimiter='\t')


def filter_names(names_df, people_list):
    print("Filtering names of relevant actors, directors and writers...")
    filtered_names_df = names_df[names_df['nconst'].isin(people_list)]
    filtered_names_df.loc[:, 'primaryProfession'] = filtered_names_df['primaryProfession'].str.replace(',', ' ')
    filtered_names_df.loc[:, 'knownForTitles'] = filtered_names_df['knownForTitles'].str.replace(',', ' ')
    print("Total entries:", len(names_df), "\nFiltered length:", len(filtered_names_df))

    filtered_names_df.to_csv("data/curated/name.basics.csv", index=False)
    print("Curated names saved!")
    print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Specify minimum vote and rating requirements for qualification.")
    parser.add_argument("-r", "--rating", type=float, default=7.0,
                        help="Rating (float): Min. rating requirement for a movie to qualify into the curated dataset (default: 7.0)")
    parser.add_argument("-v", "--vote", type=int, default=1000,
                        help="Vote (int): Min. vote requirement for a movie to qualify into the curated dataset (default: 1000)")
    parser.add_argument("-c", "--cag", action="store_true",
                        help="Enable CAG mode: Saves data in the CAG data folder (default: RAG)")
    args = parser.parse_args()

    use = "cag" if args.cag else "rag"

    movie_basics_df = filter_movies("data/raw/title.basics.tsv")
    popular_movies = filter_by_ratings("data/raw/title.ratings.tsv", movie_basics_df, args.vote, args.rating)
    movie_basics_df = filter_title_basics(movie_basics_df, popular_movies)
    name_basics_df = get_name_basics("data/raw/name.basics.tsv")
    relevant_people = filter_title_principals("data/raw/title.principals.tsv", popular_movies, movie_basics_df, name_basics_df, use)
    # filter_names(name_basics_df, relevant_people)