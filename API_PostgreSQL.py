from flask import Flask, request
from sqlalchemy import inspect
from sqlalchemy.orm import sessionmaker
import pandas
from os import environ as env
from dotenv import load_dotenv
from utilities.PostgreSQL_connection_functions import connection2db


load_dotenv()

#  make connection with PostgreSQL
cnx = connection2db(env['PostgreSQL_host2'], env['PostgreSQL_port2'], env['PostgreSQL_user2'],
                    env['PostgreSQL_password2'], env['PostgreSQL_db_name2'])
#  create session
Session = sessionmaker(bind=cnx)
s = Session()


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
    <div>to narrow it down and get only certain columns from table you need to add ?columns=column_name1,column_name2,column_name3</div>
    <div>For example to only get data from column 'title' in 'JobOffer' your link needs to be:</div>
    <div>/showtable?table=JobOffer&columns=title</div>
    <div>to get data from columns 'id' and 'title' in 'JobOffer' your link needs to be:</div>
    <div>/showtable?table=JobOffer&columns=id,title</div>
    <div>You can also use Query-like functionality "SELECT * FROM table_name WHERE key operator value</div>
    <div>For example to execute "SELECT * FROM JobOffer WHERE b2b_min > 0" your link would need to look like:</div>
    <div>/showtable?table=JobOffer&key=b2b_min&operator=>&value=0</div>
    <div>For example to execute "SELECT * FROM JobOffer WHERE expired = true" your link would need to look like:</div>
    <div>/showtable?table=JobOffer&key=expired&operator==&value=true</div>
    <div>Finally, to get just the value of table[row][column] add both &row= and &column= . Example:</div>
    <div>/showtable?table=JobOffer&column=title&row=4</div>
    <div>/showtable?table=JobOffer&row=4&column=title</div>
    <div>Order of &column and &row doesn't matter, both above queries will give same response.</div>
    """
    return readme


@app.route('/showtable')
def show_table():
    table_name = request.args.get("table", False)
    if not table_name:
        inspector = inspect(cnx)
        return {"tablelist": inspector.get_table_names()}
    else:
        columns = request.args.get("columns", False)
        key = request.args.get("key", False)
        operator = request.args.get("operator", False)
        value = request.args.get("value", False)
        if columns:
            columns = columns.split(',')
            query = pandas.read_sql_table(table_name, con=cnx, columns=columns).to_dict("records")
            return {'all offers': [{f'{table_name}': line} for line in query]}
        elif key and operator and value:
            sql_txt = f"SELECT * FROM \"{table_name}\" WHERE \"{table_name}\".{key}{operator}%s"
            query = pandas.read_sql_query(sql_txt, con=cnx, params=(value,)).to_dict("records")
            return {'all offers': [{f'{table_name}': line} for line in query]}
        else:
            query = pandas.read_sql_table(table_name, con=cnx).to_dict("records")
            return {'all offers': [{f'{table_name}': line} for line in query]}


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


