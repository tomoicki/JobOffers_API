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
cnx = connection2db(env['PostgreSQL_host2'], env['PostgreSQL_port2'], env['PostgreSQL_user2'],
                    env['PostgreSQL_password2'], env['PostgreSQL_db_name2'])
#  create session
Session = sessionmaker(bind=cnx)
s = Session()
# textual_sql = text('SELECT * FROM "JobOffer"')
# for user_obj in s.execute(textual_sql):
#     print(user_obj)

app = Flask(__name__)


@app.route('/')
def info():
    readme = f"""
    <div>You can get data about job offers scraped from nofluffjobs.com and justjoin.it.</div>
    <div>The data is stored on remote PostgreSQL database.</div>
    <div>To get the data you have to insert correct link into your browser address bar.</div>
    <div>To get currently stored Tables go to:</div>
    <div>/showtable</div>
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


@app.route('/showtable')
def show_table():
    table_name = request.args.get("table", False)
    table_as_schema = find_table(table_name)
    if not table_name:
        inspector = inspect(cnx)
        return {"tablelist": inspector.get_table_names()}
    else:
        column = request.args.get("column", False)
        row = request.args.get("row", False)
        if not column and not row:
            query = s.query(table_as_schema).all()
            for item in query:
                print(item)
                print(item.__dict__)
            result = [{'job offer': offer.__dict__} for offer in query]
            return {'all offers': result}
        elif not row:
            textual_sql = "SELECT %s FROM %s"
            res = cnx.execute(textual_sql, column, table_name)
            print(res)
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


