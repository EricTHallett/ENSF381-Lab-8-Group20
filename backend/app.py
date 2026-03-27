from copy import deepcopy
from pathlib import Path

import joblib
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

SEEDED_USERS = {
    "1": {"id": "1", "first_name": "Ava", "user_group": 11},
    "2": {"id": "2", "first_name": "Ben", "user_group": 22},
    "3": {"id": "3", "first_name": "Chloe", "user_group": 33},
    "4": {"id": "4", "first_name": "Diego", "user_group": 44},
    "5": {"id": "5", "first_name": "Ella", "user_group": 55},
}

MODEL_PATH = Path(__file__).resolve().parent / "src" / "random_forest_model.pkl"
PREDICTION_COLUMNS = [
    "city",
    "province",
    "latitude",
    "longitude",
    "lease_term",
    "type",
    "beds",
    "baths",
    "sq_feet",
    "furnishing",
    "smoking",
    "cats",
    "dogs",
]

app = Flask(__name__)
# For this lab, allow cross-origin requests from the React dev server.
# This broad setup keeps local development simple and is not standard
# production practice.
CORS(app)
users = deepcopy(SEEDED_USERS)


# TODO: Define these Flask routes with @app.route():
# - GET /users
#   Return 200 on success. The frontend still expects a JSON array,
#   so return list(users.values()) instead of the dict directly.
@app.route("/users", methods=['GET'])
def usersGet():
    return jsonify(list(users.values())), 200


# - POST /users
#   Return 201 for a successful create, 400 for invalid input,
#   and 409 if the id already exists. Since users is a dict keyed by
#   id, use the id as the lookup key when checking for duplicates.
@app.route("/users", methods=['POST'])
def create_user():
    data = request.get_json()
    user_id = data.get('id')

    if not user_id or 'first_name' not in data or 'user_group' not in data or data.get("first_name") == "" or data.get("user_group") == 0 or user_id == 0:
        return jsonify({"message": "Invalid Input"}), 400
    if user_id in users:
        return jsonify({"message": f"User {user_id} already exists."}), 409
    
    users[user_id] = {
        'id': user_id,
        "first_name": data["first_name"],
        "user_group": data['user_group']
    }

    return jsonify(users[user_id]), 201



# - PUT /users/<user_id>
#   Return 200 for a successful update, 400 for invalid input,
#   and 404 if the user does not exist. Update the matching record
#   with users[user_id] = {...} after confirming the key exists.
@app.route('/users/<user_id>', methods=['PUT'])
def update(user_id):
    data = request.get_json()
    print(data)
    

    if not user_id or 'first_name' not in data or 'user_group' not in data or data.get("first_name") == "" or data.get("user_group") == 0 or user_id == 0:
        return jsonify({"message": "Invalid Input"}), 400

        
    if user_id not in users:
        return jsonify({"message": f"User {user_id} was not found."}), 404

    users[user_id] = {
        'id': user_id,
        "first_name": data["first_name"],
        "user_group": data['user_group'],
        "message": f"Update the user with a user id of is successful: {user_id}"
    }

    return jsonify(users[user_id]), 200

# - DELETE /users/<user_id>
#   Return 200 for a successful delete and 404 if the user does not
#   exist. Delete with del users[user_id] after confirming the key
#   exists.
@app.route('/users/<user_id>', methods=["DELETE"])
def delete(user_id):
    if user_id not in users:
        return jsonify({"message": f"User {user_id} was not found."}), 404
    
    del users[user_id]
    return jsonify({"message": f"User {user_id} was lt."}), 200



#   Exercise2
# - POST /predict_house_price
@app.route('/predict_house_price', methods=['POST'])
def predict_house_price():
    try:
        data = request.get_json()

        pets = bool(data.get('pets'))
        cats = pets
        dogs = pets

        model = joblib.load(MODEL_PATH)

        sample_data = [
            data['city'],
            data['province'],
            float(data['latitude']),
            float(data['longitude']),
            data['lease_term'],
            data['type'],
            float(data['beds']),
            float(data['baths']),
            float(data['sq_feet']),
            data['furnishing'],
            data['smoking'],
            cats,
            dogs,
        ]

        sample_df = pd.DataFrame([sample_data], columns=PREDICTION_COLUMNS)

        predicted_price = model.predict(sample_df)[0]

        return jsonify({"predicted_price": predicted_price}), 200
    
    except KeyError as e:
        return jsonify({"message": f"Missing required field: {str(e)}"}), 400
    except ValueError as e:
        return jsonify({"message": f"Invalid value: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"message": f"An error occurred: {str(e)}"}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5050)
