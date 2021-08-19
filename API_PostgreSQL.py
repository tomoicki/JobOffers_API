from flask import Flask, request, jsonify
from sqlalchemy import inspect
import pandas
from os import environ as env
from dotenv import load_dotenv
from utilities.PostgreSQL_connection_functions import connection2db

load_dotenv()


app = Flask(__name__)


@app.route('/')
def info():
    readme = f"""
    You can get data about job offers scraped from https://nofluffjobs.com/pl/.
    The data is stored on remote PostgreSQL database.
    To get the data you have to insert correct link into your browser address bar.
    To get whole data from selected Table you have to use:
    /showtable?table=table_name
    replace table_name with real Table name that is stored in DB.
    To get currently stored Tables go to:
    /tablelist
    For example to get data from table 'All' your link would look:
    /showtable?table=All
    to narrow it down and get only one column from table you need to add ?column=column_name
    For example to only get data from column 'job_name' in 'All' your link needs to be:
    /showtable?table=All&column=job_name
    Alternatively, you can request info from specific row from table, to do this replace 'column' with 'row' 
    and give int value as row number. Example:
    /showtable?table=All&row=5
    Finally, to get just the value of table[row][column] add both &row= and &column= . Example:
    /showtable?table=All&column=job_name&row=4
    /showtable?table=All&row=4&column=job_name
    Order of &column and &row doesn't matter, both above queries will give same response.
    """
    information = readme
    return jsonify(information)


@app.route('/tablelist')
def tablelist():
    cnx = connection2db(env['PostgreSQL_host'], env['PostgreSQL_port'], env['PostgreSQL_user'],
                        env['PostgreSQL_password'], env['PostgreSQL_db_name'])
    inspector = inspect(cnx)
    tables = dict(zip([i for i in range(len(inspector.get_table_names()))],
                      [item for item in inspector.get_table_names()]))
    return tables


@app.route('/showtable')
def table():
    cnx = connection2db(env['PostgreSQL_host'], env['PostgreSQL_port'], env['PostgreSQL_user'],
                        env['PostgreSQL_password'], env['PostgreSQL_db_name'])
    inspector = inspect(cnx)
    out = dict(zip([i for i in range(len(inspector.get_table_names()))],
                   [item for item in inspector.get_table_names()]))
    name = request.args.get('name', None)
    column = request.args.get('column', None)
    row = request.args.get('row', None)
    if name:
        df = pandas.read_sql(name, cnx)
        if column is None and row is None:
            out = df.to_dict("records")
        elif column is None and row is not None:
            out = df.loc[int(row), :].to_json(orient='index')
        elif column is not None and row is None:
            out = df[column].to_json(orient='index')
        else:
            out = df.loc[int(row), column]
    return out


if __name__ == '__main__':
    # app.run(debug=False, host='192.168.222.116')
    app.run(debug=False)


