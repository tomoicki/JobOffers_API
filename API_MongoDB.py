from flask import Flask
import pandas
from os import environ as env
from dotenv import load_dotenv
from database.MongoDB_connection_functions import connection_to_mongodb


load_dotenv()


app = Flask(__name__)


@app.route('/')
def get_users():
    #  create connection with MongoDB
    collection = connection_to_mongodb(env['mongoDB_host'], env['mongoDB_port'],
                                       env['mongoDB_db_name'], env['mongoDB_collection_name'])
    data = pandas.DataFrame(list(collection.find()))
    data.drop(columns=['_id'], inplace=True)
    data = data.to_dict("records")
    return {'data': data}


if __name__ == '__main__':
    app.run(debug=False)

