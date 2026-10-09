import os
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import DuplicateKeyError
from bson.objectid import ObjectId
from bson.errors import InvalidId
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("DATABASE_NAME", "movieDB")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "ratings")

mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)

def get_db_collection():
    """Returns the PyMongo collection object."""
    db = mongo_client[DATABASE_NAME]
    return db[COLLECTION_NAME]

def serialize_doc(doc):
    """Converts MongoDB document ObjectId to string for JSON serialization."""
    if not doc:
        return None
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc

# -----------------------------------------------------------------------------
# Web Page Routes
# -----------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ratings")
def ratings_page():
    return render_template("ratings.html")

@app.route("/analysis")
def analysis_page():
    return render_template("analysis.html")

# -----------------------------------------------------------------------------
# REST API Endpoints
# -----------------------------------------------------------------------------

@app.route("/api/dashboard", methods=["GET"])
def get_dashboard_summary():
    """Returns overview statistics and summary charts data for Dashboard."""
    try:
        col = get_db_collection()

        # 1. Total records
        total_records = col.count_documents({})

        if total_records == 0:
            return jsonify({
                "status": "success",
                "summary": {
                    "total_records": 0,
                    "distinct_movies": 0,
                    "distinct_users": 0,
                    "overall_avg_rating": 0.0
                },
                "top_movies": [],
                "genre_popularity": [],
                "rating_distribution": [],
                "insights": ["No rating records found in database. Please run seed_data.py to populate sample data."]
            })

        # 2. Distinct movies & users count
        distinct_movies = len(col.distinct("movie_title"))
        distinct_users = len(col.distinct("user_id"))

        # 3. Overall average rating using MongoDB Aggregation
        overall_avg_pipeline = [
            {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}}}
        ]
        avg_res = list(col.aggregate(overall_avg_pipeline))
        overall_avg = round(avg_res[0]["avg_rating"], 2) if avg_res else 0.0

        # 4. Top 5 Movies for dashboard preview
        top_5_pipeline = [
            {
                "$group": {
                    "_id": "$movie_title",
                    "avg_rating": {"$avg": "$rating"},
                    "count": {"$sum": 1},
                    "genre": {"$first": "$genre"}
                }
            },
            {"$match": {"count": {"$gte": 3}}},
            {"$sort": {"avg_rating": -1, "count": -1}},
            {"$limit": 5}
        ]
        top_movies_docs = list(col.aggregate(top_5_pipeline))
        top_movies = [
            {
                "movie_title": doc["_id"],
                "avg_rating": round(doc["avg_rating"], 2),
                "count": doc["count"],
                "genre": doc["genre"]
            } for doc in top_movies_docs
        ]

        # 5. Genre breakdown (Rating count per genre)
        genre_pipeline = [
            {
                "$group": {
                    "_id": "$genre",
                    "count": {"$sum": 1},
                    "avg_rating": {"$avg": "$rating"}
                }
            },
            {"$sort": {"count": -1}}
        ]
        genre_docs = list(col.aggregate(genre_pipeline))
        genre_popularity = [
            {
                "genre": doc["_id"],
                "count": doc["count"],
                "avg_rating": round(doc["avg_rating"], 2)
            } for doc in genre_docs
        ]

        # 6. Rating Distribution (0.5 to 5.0)
        dist_pipeline = [
            {"$group": {"_id": "$rating", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]
        dist_docs = list(col.aggregate(dist_pipeline))

        # Ensure all 10 rating levels exist
        rating_levels = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
        dist_map = {doc["_id"]: doc["count"] for doc in dist_docs}
        rating_distribution = [{"rating": r, "count": dist_map.get(r, 0)} for r in rating_levels]

        # Dynamic observations
        top_genre = genre_popularity[0]["genre"] if genre_popularity else "N/A"
        highest_rated_movie = top_movies[0]["movie_title"] if top_movies else "N/A"

        insights = [
            f"Database contains {total_records} ratings across {distinct_movies} distinct movies and {distinct_users} audience members.",
            f"The overall average rating across all movies is {overall_avg} out of 5.0 stars.",
            f"The most reviewed genre is '{top_genre}' with {genre_popularity[0]['count'] if genre_popularity else 0} rating submissions.",
            f"The highest rated movie (min 3 reviews) is '{highest_rated_movie}' with an average rating of {top_movies[0]['avg_rating'] if top_movies else 0} stars."
        ]

        return jsonify({
            "status": "success",
            "summary": {
                "total_records": total_records,
                "distinct_movies": distinct_movies,
                "distinct_users": distinct_users,
                "overall_avg_rating": overall_avg
            },
            "top_movies": top_movies,
            "genre_popularity": genre_popularity,
            "rating_distribution": rating_distribution,
            "insights": insights
        })

    except Exception as e:
        return jsonify({"status": "error", "message": f"Database error: {str(e)}"}), 500


@app.route("/api/ratings", methods=["GET"])
def get_ratings():
    """Retrieves list of rating documents with filtering, searching, sorting, and pagination."""
    try:
        col = get_db_collection()

        # Query Parameters
        search_term = request.args.get("search", "").strip()
        genre = request.args.get("genre", "").strip()
        min_rating = request.args.get("min_rating", type=float)
        max_rating = request.args.get("max_rating", type=float)
        sort_by = request.args.get("sort_by", "rating_date")
        order = request.args.get("order", "desc")
        page = max(1, request.args.get("page", 1, type=int))
        limit = max(1, min(100, request.args.get("limit", 10, type=int)))

        # Build MongoDB filter query
        query = {}
        if search_term:
            query["movie_title"] = {"$regex": search_term, "$options": "i"}
        if genre and genre != "All":
            query["genre"] = genre
        
        if min_rating is not None or max_rating is not None:
            rating_clause = {}
            if min_rating is not None:
                rating_clause["$gte"] = min_rating
            if max_rating is not None:
                rating_clause["$lte"] = max_rating
            query["rating"] = rating_clause

        # Allowed sorting fields
        valid_sort_fields = {"movie_title", "genre", "release_year", "rating", "rating_date", "user_id"}
        if sort_by not in valid_sort_fields:
            sort_by = "rating_date"

        sort_dir = DESCENDING if order.lower() == "desc" else ASCENDING

        # MongoDB find(), count_documents(), sort(), skip(), limit()
        total_matching = col.count_documents(query)
        total_pages = max(1, (total_matching + limit - 1) // limit)
        skip = (page - 1) * limit

        cursor = col.find(query).sort(sort_by, sort_dir).skip(skip).limit(limit)
        results = [serialize_doc(doc) for doc in cursor]

        genres_list = sorted(col.distinct("genre"))

        return jsonify({
            "status": "success",
            "data": results,
            "pagination": {
                "total_records": total_matching,
                "total_pages": total_pages,
                "current_page": page,
                "limit": limit
            },
            "available_genres": genres_list
        })

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/ratings", methods=["POST"])
def create_rating():
    """Creates a new rating document in MongoDB using insert_one()."""
    try:
        col = get_db_collection()
        data = request.get_json() or {}

        # Validations
        user_id = str(data.get("user_id", "")).strip().upper()
        movie_title = str(data.get("movie_title", "")).strip()
        genre = str(data.get("genre", "")).strip()
        
        try:
            release_year = int(data.get("release_year"))
            rating = float(data.get("rating"))
        except (ValueError, TypeError):
            return jsonify({"status": "error", "message": "Invalid numeric values for release_year or rating."}), 400

        if not user_id or not movie_title or not genre:
            return jsonify({"status": "error", "message": "User ID, Movie Title, and Genre are required."}), 400

        if release_year < 1888 or release_year > 2030:
            return jsonify({"status": "error", "message": "Release year must be between 1888 and 2030."}), 400

        if rating < 0.5 or rating > 5.0:
            return jsonify({"status": "error", "message": "Rating must be between 0.5 and 5.0 stars."}), 400

        # Construct MongoDB Document
        now_str = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        new_doc = {
            "user_id": user_id,
            "movie_title": movie_title,
            "genre": genre,
            "release_year": release_year,
            "rating": rating,
            "rating_date": now_str
        }

        # MongoDB insertOne()
        res = col.insert_one(new_doc)
        new_doc["_id"] = str(res.inserted_id)

        return jsonify({"status": "success", "message": "Movie rating created successfully!", "data": new_doc}), 201

    except DuplicateKeyError:
        return jsonify({"status": "error", "message": f"User '{data.get('user_id')}' has already rated '{data.get('movie_title')}'. Duplicate reviews are not allowed."}), 409
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/ratings/<rating_id>", methods=["PUT"])
def update_rating(rating_id):
    """Updates an existing rating document in MongoDB using update_one()."""
    try:
        col = get_db_collection()
        try:
            obj_id = ObjectId(rating_id)
        except InvalidId:
            return jsonify({"status": "error", "message": "Invalid MongoDB ObjectId format."}), 400

        data = request.get_json() or {}

        # Validation
        user_id = str(data.get("user_id", "")).strip().upper()
        movie_title = str(data.get("movie_title", "")).strip()
        genre = str(data.get("genre", "")).strip()

        try:
            release_year = int(data.get("release_year"))
            rating = float(data.get("rating"))
        except (ValueError, TypeError):
            return jsonify({"status": "error", "message": "Invalid numeric values for release_year or rating."}), 400

        if not user_id or not movie_title or not genre:
            return jsonify({"status": "error", "message": "User ID, Movie Title, and Genre are required."}), 400

        if rating < 0.5 or rating > 5.0:
            return jsonify({"status": "error", "message": "Rating must be between 0.5 and 5.0."}), 400

        update_fields = {
            "user_id": user_id,
            "movie_title": movie_title,
            "genre": genre,
            "release_year": release_year,
            "rating": rating,
            "rating_date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
        }

        # MongoDB updateOne()
        result = col.update_one({"_id": obj_id}, {"$set": update_fields})

        if result.matched_count == 0:
            return jsonify({"status": "error", "message": "Rating document not found."}), 404

        return jsonify({"status": "success", "message": "Rating updated successfully!"})

    except DuplicateKeyError:
        return jsonify({"status": "error", "message": "Updating would cause a duplicate rating record for this user and movie."}), 409
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/ratings/<rating_id>", methods=["DELETE"])
def delete_rating(rating_id):
    """Deletes a rating document from MongoDB using delete_one()."""
    try:
        col = get_db_collection()
        try:
            obj_id = ObjectId(rating_id)
        except InvalidId:
            return jsonify({"status": "error", "message": "Invalid MongoDB ObjectId format."}), 400

        # MongoDB deleteOne()
        result = col.delete_one({"_id": obj_id})

        if result.deleted_count == 0:
            return jsonify({"status": "error", "message": "Rating record not found."}), 404

        return jsonify({"status": "success", "message": "Rating record deleted successfully!"})

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# -----------------------------------------------------------------------------
# MongoDB Aggregation Analytics Endpoints
# -----------------------------------------------------------------------------

@app.route("/api/analysis/top-movies", methods=["GET"])
def get_top_movies():
    """MongoDB Aggregation Pipeline: Top Movies by Average Rating with threshold min votes."""
    try:
        col = get_db_collection()
        min_votes = max(1, request.args.get("min_votes", 3, type=int))
        limit = max(1, request.args.get("limit", 10, type=int))

        pipeline = [
            {
                "$group": {
                    "_id": "$movie_title",
                    "avg_rating": {"$avg": "$rating"},
                    "total_ratings": {"$sum": 1},
                    "genre": {"$first": "$genre"},
                    "release_year": {"$first": "$release_year"}
                }
            },
            {"$match": {"total_ratings": {"$gte": min_votes}}},
            {"$sort": {"avg_rating": -1, "total_ratings": -1}},
            {"$limit": limit}
        ]

        docs = list(col.aggregate(pipeline))
        results = [
            {
                "movie_title": d["_id"],
                "avg_rating": round(d["avg_rating"], 2),
                "total_ratings": d["total_ratings"],
                "genre": d["genre"],
                "release_year": d["release_year"]
            } for d in docs
        ]

        return jsonify({"status": "success", "data": results, "min_votes": min_votes})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/analysis/most-rated", methods=["GET"])
def get_most_rated_movies():
    """MongoDB Aggregation Pipeline: Most Reviewed Movies by Rating Count ($group, $sum, $sort, $limit)."""
    try:
        col = get_db_collection()
        limit = max(1, request.args.get("limit", 10, type=int))

        pipeline = [
            {
                "$group": {
                    "_id": "$movie_title",
                    "total_ratings": {"$sum": 1},
                    "avg_rating": {"$avg": "$rating"},
                    "genre": {"$first": "$genre"},
                    "release_year": {"$first": "$release_year"}
                }
            },
            {"$sort": {"total_ratings": -1, "avg_rating": -1}},
            {"$limit": limit}
        ]

        docs = list(col.aggregate(pipeline))
        results = [
            {
                "movie_title": d["_id"],
                "total_ratings": d["total_ratings"],
                "avg_rating": round(d["avg_rating"], 2),
                "genre": d["genre"],
                "release_year": d["release_year"]
            } for d in docs
        ]

        return jsonify({"status": "success", "data": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/analysis/genres", methods=["GET"])
def get_genre_analysis():
    """MongoDB Aggregation Pipeline: Genre Performance ($group, $avg, $sum, $addToSet)."""
    try:
        col = get_db_collection()

        pipeline = [
            {
                "$group": {
                    "_id": "$genre",
                    "avg_rating": {"$avg": "$rating"},
                    "total_ratings": {"$sum": 1},
                    "distinct_movies_set": {"$addToSet": "$movie_title"}
                }
            },
            {
                "$project": {
                    "genre": "$_id",
                    "avg_rating": {"$round": ["$avg_rating", 2]},
                    "total_ratings": 1,
                    "distinct_movies_count": {"$size": "$distinct_movies_set"}
                }
            },
            {"$sort": {"avg_rating": -1}}
        ]

        results = list(col.aggregate(pipeline))
        for r in results:
            r.pop("_id", None)

        return jsonify({"status": "success", "data": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/analysis/rating-distribution", methods=["GET"])
def get_rating_distribution():
    """MongoDB Aggregation Pipeline: Rating Breakdown across 0.5-5.0 Scale."""
    try:
        col = get_db_collection()

        pipeline = [
            {"$group": {"_id": "$rating", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}}
        ]

        docs = list(col.aggregate(pipeline))
        rating_levels = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
        dist_map = {d["_id"]: d["count"] for d in docs}

        data = [{"rating": r, "count": dist_map.get(r, 0)} for r in rating_levels]

        return jsonify({"status": "success", "data": data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/analysis/year-stats", methods=["GET"])
def get_year_stats():
    """MongoDB Aggregation Pipeline: Release Year Movie Rating Stats."""
    try:
        col = get_db_collection()

        pipeline = [
            {
                "$group": {
                    "_id": "$release_year",
                    "avg_rating": {"$avg": "$rating"},
                    "total_ratings": {"$sum": 1},
                    "distinct_movies": {"$addToSet": "$movie_title"}
                }
            },
            {
                "$project": {
                    "release_year": "$_id",
                    "avg_rating": {"$round": ["$avg_rating", 2]},
                    "total_ratings": 1,
                    "movie_count": {"$size": "$distinct_movies"}
                }
            },
            {"$sort": {"release_year": 1}}
        ]

        results = list(col.aggregate(pipeline))
        for r in results:
            r.pop("_id", None)

        return jsonify({"status": "success", "data": results})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route("/api/analysis/insights", methods=["GET"])
def get_dynamic_insights():
    """Generates real-time, automated analytical insights from MongoDB data."""
    try:
        col = get_db_collection()
        total_records = col.count_documents({})

        if total_records == 0:
            return jsonify({"status": "success", "insights": ["No ratings stored in database."]})

        # Most reviewed genre
        most_reviewed_genre_doc = list(col.aggregate([
            {"$group": {"_id": "$genre", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ]))
        top_genre = most_reviewed_genre_doc[0]["_id"] if most_reviewed_genre_doc else "N/A"
        top_genre_count = most_reviewed_genre_doc[0]["count"] if most_reviewed_genre_doc else 0

        # Genre with highest average rating
        highest_avg_genre_doc = list(col.aggregate([
            {"$group": {"_id": "$genre", "avg_rating": {"$avg": "$rating"}}},
            {"$sort": {"avg_rating": -1}},
            {"$limit": 1}
        ]))
        best_genre = highest_avg_genre_doc[0]["_id"] if highest_avg_genre_doc else "N/A"
        best_genre_avg = round(highest_avg_genre_doc[0]["avg_rating"], 2) if highest_avg_genre_doc else 0.0

        # Top movie with min 5 ratings
        top_movie_doc = list(col.aggregate([
            {
                "$group": {
                    "_id": "$movie_title",
                    "avg_rating": {"$avg": "$rating"},
                    "count": {"$sum": 1}
                }
            },
            {"$match": {"count": {"$gte": 5}}},
            {"$sort": {"avg_rating": -1}},
            {"$limit": 1}
        ]))
        best_movie = top_movie_doc[0]["_id"] if top_movie_doc else "N/A"
        best_movie_rating = round(top_movie_doc[0]["avg_rating"], 2) if top_movie_doc else 0.0

        # Most rated movie
        most_rated_movie_doc = list(col.aggregate([
            {"$group": {"_id": "$movie_title", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 1}
        ]))
        most_rated_movie = most_rated_movie_doc[0]["_id"] if most_rated_movie_doc else "N/A"
        most_rated_movie_count = most_rated_movie_doc[0]["count"] if most_rated_movie_doc else 0

        # Overall average
        overall_doc = list(col.aggregate([
            {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}}}
        ]))
        overall_avg = round(overall_doc[0]["avg_rating"], 2) if overall_doc else 0.0

        insights = [
            f"The genre with the most rating submissions is '{top_genre}' with a total of {top_genre_count} reviews.",
            f"The genre with the highest audience satisfaction is '{best_genre}' with an average rating of {best_genre_avg}/5.0.",
            f"The top-performing movie (min. 5 reviews) is '{best_movie}' rated at {best_movie_rating} stars on average.",
            f"The most reviewed movie in the dataset is '{most_rated_movie}' with {most_rated_movie_count} total user ratings.",
            f"The overall database average rating across all recorded reviews stands at {overall_avg} out of 5.0 stars."
        ]

        return jsonify({"status": "success", "insights": insights})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("FLASK_PORT", 5000))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    print(f"Starting Movie Rating Analysis Flask app on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
