from flask import Flask, request, jsonify
from sqlalchemy import inspect, select, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import table
import pandas
from os import environ as env
from dotenv import load_dotenv
from utilities.PostgreSQL_connection_functions import connection2db
from utilities.tables_declaration import *


load_dotenv()

#  make connection with PostgreSQL
cnx = connection2db(env['PostgreSQL_host'], env['PostgreSQL_port'], env['PostgreSQL_user'],
                    env['PostgreSQL_password'], env['PostgreSQL_db_name'])
#  create session
Session = sessionmaker(bind=cnx)
s = Session()
textual_sql = text('SELECT * FROM "JobOffer"')
for user_obj in s.execute(textual_sql).scalars():
    print(user_obj)

app = Flask(__name__)


@app.route('/')
def info():
    readme = f"""
    <div>You can get data about job offers scraped from nofluffjobs.com and justjoin.it.</div>
    <div>The data is stored on remote PostgreSQL database.</div>
    <div>To get the data you have to insert correct link into your browser address bar.</div>
    <div>To get currently stored Tables go to:</div>
    <div>/tablelist</div>
    <div>To get whole data from selected Table you have to use:</div>
    <div>/showtable?table=table_name</div>
    <div>replace table_name with real Table name that is stored in DB.</div>
    <div>For example to get data from table 'JobOffer' your link would look:</div>
    <div>/showtable?table=JobOffer</div>
    <div>to narrow it down and get only one column from table you need to add ?column=column_name</div>
    <div>For example to only get data from column 'title' in 'JobOffer' your link needs to be:</div>
    <div>/showtable?table=JobOffer&column=title</div>
    <div>Alternatively, you can request info from specific row from table, to do this replace 'column' with 'row' </div>
    <div>and give int value as row number. Example:</div>
    <div>/showtable?table=JobOffer&row=5</div>
    <div>Finally, to get just the value of table[row][column] add both &row= and &column= . Example:</div>
    <div>/showtable?table=JobOffer&column=title&row=4</div>
    <div>/showtable?table=JobOffer&row=4&column=title</div>
    <div>Order of &column and &row doesn't matter, both above queries will give same response.</div>
    """
    return readme


@app.route('/tablelist')
def tablelist():
    inspector = inspect(cnx)
    # tables = dict(zip([i for i in range(len(inspector.get_table_names()))],
    #                   [item for item in inspector.get_table_names()]))
    return {"tablelist": inspector.get_table_names()}


@app.route('/showtable')
def show_table():
    table_name = request.args.get('table', None)
    query = s.query(find_table(table_name)).all()
    result = [{'job offer': offer.title} for offer in query]
    return {'all offers': result}
    # column = request.args.get('column', None)
    # row = request.args.get('row', None)
    # if tablee:
    #     df = pandas.read_sql(tablee, cnx)
    #     if column is None and row is None:
    #         out = df.to_dict("records")
    #     elif column is None and row is not None:
    #         out = df.loc[int(row), :].to_json(orient='index')
    #     elif column is not None and row is None:
    #         out = df[column].to_json(orient='index')
    #     else:
    #         out = df.loc[int(row), column]
    # return out


if __name__ == '__main__':
    # app.run(debug=False, host='192.168.222.116')
    app.run(debug=False)


