import os
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pymongo import MongoClient, ASCENDING

# Load environment variables
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "movieDB")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "ratings")

# Curated dataset of movies across Action, Comedy, Drama, Sci-Fi, Romance, Horror, Animation, Thriller
# Featuring Indian Cinema (Kannada, Hindi, Tamil, Telugu) and Global Blockbusters (up to 2026)
MOVIES_CATALOG = [
    # Action
    {"movie_title": "Kantara: Chapter 1", "genre": "Action", "release_year": 2025, "base_quality": 4.9},
    {"movie_title": "Toxic: A Fairy Tale for Grown-ups", "genre": "Action", "release_year": 2025, "base_quality": 4.8},
    {"movie_title": "Game Changer", "genre": "Action", "release_year": 2025, "base_quality": 4.6},
    {"movie_title": "War 2", "genre": "Action", "release_year": 2025, "base_quality": 4.7},
    {"movie_title": "Coolie", "genre": "Action", "release_year": 2025, "base_quality": 4.7},
    {"movie_title": "Avengers: Doomsday", "genre": "Action", "release_year": 2026, "base_quality": 4.9},
    {"movie_title": "Pushpa 2: The Rule", "genre": "Action", "release_year": 2024, "base_quality": 4.8},
    {"movie_title": "Kalki 2898 AD", "genre": "Action", "release_year": 2024, "base_quality": 4.7},
    {"movie_title": "K.G.F: Chapter 2", "genre": "Action", "release_year": 2022, "base_quality": 4.8},
    {"movie_title": "Kantara", "genre": "Action", "release_year": 2022, "base_quality": 4.8},
    {"movie_title": "Salaar: Part 1 - Ceasefire", "genre": "Action", "release_year": 2023, "base_quality": 4.5},
    {"movie_title": "Jawan", "genre": "Action", "release_year": 2023, "base_quality": 4.6},
    {"movie_title": "RRR", "genre": "Action", "release_year": 2022, "base_quality": 4.8},

    # Drama
    {"movie_title": "Chhaava", "genre": "Drama", "release_year": 2025, "base_quality": 4.8},
    {"movie_title": "Ramayana: Part 1", "genre": "Drama", "release_year": 2026, "base_quality": 4.9},
    {"movie_title": "12th Fail", "genre": "Drama", "release_year": 2023, "base_quality": 4.9},
    {"movie_title": "777 Charlie", "genre": "Drama", "release_year": 2022, "base_quality": 4.8},
    {"movie_title": "Sapta Sagarada Ello - Side A", "genre": "Drama", "release_year": 2023, "base_quality": 4.7},
    {"movie_title": "Oppenheimer", "genre": "Drama", "release_year": 2023, "base_quality": 4.8},
    {"movie_title": "3 Idiots", "genre": "Drama", "release_year": 2009, "base_quality": 4.9},

    # Comedy
    {"movie_title": "Housefull 5", "genre": "Comedy", "release_year": 2025, "base_quality": 4.3},
    {"movie_title": "Stree 2", "genre": "Comedy", "release_year": 2024, "base_quality": 4.7},
    {"movie_title": "Tillu Square", "genre": "Comedy", "release_year": 2024, "base_quality": 4.5},
    {"movie_title": "Kirik Party", "genre": "Comedy", "release_year": 2016, "base_quality": 4.5},
    {"movie_title": "Hera Pheri", "genre": "Comedy", "release_year": 2000, "base_quality": 4.8},
    {"movie_title": "Deadpool & Wolverine", "genre": "Comedy", "release_year": 2024, "base_quality": 4.6},

    # Sci-Fi
    {"movie_title": "Avatar: Fire and Ash", "genre": "Sci-Fi", "release_year": 2025, "base_quality": 4.9},
    {"movie_title": "Superman", "genre": "Sci-Fi", "release_year": 2025, "base_quality": 4.7},
    {"movie_title": "Dune: Part Two", "genre": "Sci-Fi", "release_year": 2024, "base_quality": 4.8},
    {"movie_title": "Interstellar", "genre": "Sci-Fi", "release_year": 2014, "base_quality": 4.8},
    {"movie_title": "Lucia", "genre": "Sci-Fi", "release_year": 2013, "base_quality": 4.6},

    # Romance
    {"movie_title": "Sitaare Zameen Par", "genre": "Romance", "release_year": 2025, "base_quality": 4.7},
    {"movie_title": "Sita Ramam", "genre": "Romance", "release_year": 2022, "base_quality": 4.7},
    {"movie_title": "Hi Nanna", "genre": "Romance", "release_year": 2023, "base_quality": 4.6},
    {"movie_title": "96", "genre": "Romance", "release_year": 2018, "base_quality": 4.7},
    {"movie_title": "La La Land", "genre": "Romance", "release_year": 2016, "base_quality": 4.5},

    # Horror
    {"movie_title": "Bramayugam", "genre": "Horror", "release_year": 2024, "base_quality": 4.7},
    {"movie_title": "Tumbbad", "genre": "Horror", "release_year": 2018, "base_quality": 4.8},
    {"movie_title": "Bhool Bhulaiyaa 3", "genre": "Horror", "release_year": 2024, "base_quality": 4.3},
    {"movie_title": "The Conjuring", "genre": "Horror", "release_year": 2013, "base_quality": 4.2},

    # Thriller
    {"movie_title": "Spirit", "genre": "Thriller", "release_year": 2025, "base_quality": 4.8},
    {"movie_title": "Maharaja", "genre": "Thriller", "release_year": 2024, "base_quality": 4.8},
    {"movie_title": "Drishyam 2", "genre": "Thriller", "release_year": 2022, "base_quality": 4.7},
    {"movie_title": "Andhadhun", "genre": "Thriller", "release_year": 2018, "base_quality": 4.8},

    # Animation
    {"movie_title": "Spider-Man: Beyond the Spider-Verse", "genre": "Animation", "release_year": 2026, "base_quality": 4.9},
    {"movie_title": "Inside Out 2", "genre": "Animation", "release_year": 2024, "base_quality": 4.6},
    {"movie_title": "Spirited Away", "genre": "Animation", "release_year": 2001, "base_quality": 4.8}
]

RATING_VALUES = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]

def generate_rating(base_quality):
    """Generates a realistic rating centered around base quality with variation."""
    weights = []
    for r in RATING_VALUES:
        diff = abs(r - base_quality)
        w = max(0.05, 1.0 - (diff * 0.4))
        weights.append(w)
    return random.choices(RATING_VALUES, weights=weights, k=1)[0]

def generate_dataset(num_records=550):
    """Generates unique (user_id, movie_title) rating documents."""
    user_pool = [f"USER_{i:03d}" for i in range(101, 191)]  # 90 unique users
    records = []
    seen = set()

    start_date = datetime(2023, 1, 1)
    end_date = datetime(2024, 10, 1)
    total_seconds = int((end_date - start_date).total_seconds())

    attempts = 0
    max_attempts = num_records * 10

    while len(records) < num_records and attempts < max_attempts:
        attempts += 1
        user_id = random.choice(user_pool)
        movie = random.choice(MOVIES_CATALOG)

        key = (user_id, movie["movie_title"])
        if key in seen:
            continue

        seen.add(key)
        rating_val = generate_rating(movie["base_quality"])

        # Random rating timestamp
        random_sec = random.randint(0, total_seconds)
        dt = start_date + timedelta(seconds=random_sec)
        rating_date_str = dt.strftime("%Y-%m-%dT%H:%M:%SZ")

        doc = {
            "user_id": user_id,
            "movie_title": movie["movie_title"],
            "genre": movie["genre"],
            "release_year": int(movie["release_year"]),
            "rating": float(rating_val),
            "rating_date": rating_date_str
        }
        records.append(doc)

    return records

def seed_database():
    print(f"Connecting to MongoDB at {MONGO_URI}...")
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)

    try:
        # Check server connection
        client.admin.command('ping')
        print("Connected to MongoDB successfully!")
    except Exception as e:
        print(f"\n[ERROR] Could not connect to MongoDB server: {e}")
        print("Please ensure MongoDB service is running locally on port 27017 or check your MONGO_URI in .env")
        return False

    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]

    # Clear existing data for fresh seed
    print(f"Clearing existing collection '{COLLECTION_NAME}' in database '{DATABASE_NAME}'...")
    collection.delete_many({})

    # Create indexes for optimized query performance
    print("Creating MongoDB indexes...")
    collection.create_index([("movie_title", ASCENDING)])
    collection.create_index([("genre", ASCENDING)])
    collection.create_index([("rating", ASCENDING)])
    # Compound unique index to prevent duplicate user reviews for the same movie
    collection.create_index(
        [("user_id", ASCENDING), ("movie_title", ASCENDING)],
        unique=True
    )

    # Generate records
    print("Generating synthetic movie rating dataset...")
    records = generate_dataset(550)

    # Insert into MongoDB
    print(f"Inserting {len(records)} rating records into MongoDB...")
    result = collection.insert_many(records)

    print("\n" + "="*50)
    print("SEEDING COMPLETED SUCCESSFULLY!")
    print("="*50)
    print(f"Database Name       : {DATABASE_NAME}")
    print(f"Collection Name     : {COLLECTION_NAME}")
    print(f"Inserted Documents  : {len(result.inserted_ids)}")
    print(f"Distinct Movies     : {len(collection.distinct('movie_title'))}")
    print(f"Distinct Users      : {len(collection.distinct('user_id'))}")
    print(f"Distinct Genres     : {len(collection.distinct('genre'))}")
    print("="*50 + "\n")

    return True

if __name__ == "__main__":
    seed_database()
