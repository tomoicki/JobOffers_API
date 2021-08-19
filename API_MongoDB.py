from flask import Flask
from bson.json_util import dumps
from os import environ as env
from dotenv import load_dotenv
from utilities.MongoDB_connection_functions import connection_to_mongodb


load_dotenv()


app = Flask(__name__)


@app.route('/')
def get_users():
    #  create connection with MongoDB
    collection = connection_to_mongodb(env['mongoDB_host'], env['mongoDB_port'],
                                       env['mongoDB_db_name'], env['mongoDB_collection_name'])
    retrieved_users = dumps(collection.find())
    return retrieved_users


if __name__ == '__main__':
    app.run(debug=False)

