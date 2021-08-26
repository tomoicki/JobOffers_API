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
    <div>To get the data, you have to insert correct link into your browser address bar.</div>
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
    <div>You can also use Query-like functionality "SELECT * FROM table_name WHERE key1 operator1 value1"</div>
    <div>For example to execute "SELECT * FROM JobOffer WHERE b2b_min > 0" your link would need to look like:</div>
    <div>/showtable?table=JobOffer&key1=b2b_min&operator1=>&value1=0</div>
    <div>For example to execute "SELECT * FROM JobOffer WHERE expired = true" your link would need to look like:</div>
    <div>/showtable?table=JobOffer&key1=expired&operator1==&value1=true</div>
    <div>You can also add columns=column_name for query to be "SELECT column_name" instead of "SELECT *"</div>
    <div>Example for query "SELECT title FROM JobOffer WHERE expired = true"</div>
    <div>/showtable?table=JobOffer&columns=title&key1=expired&operator1==&value1=true</div>
    <div>Unfortunately, in query with WHERE you can only provide 1 column_name or * for all columns</div>
    <div>WHERE query can take up to three sets of key,operator,value.</div>
    <div>For example to get only title of those job offers that have b2b_min>0 and permanent_min>0 and mandate_min>0</div>
    <div>which translates into "SELECT title FROM JobOffer WHERE b2b_min>0 and permanent_min>0 and mandate_min>0"</div>
    <div>your link would look:</div>
    <div>/showtable?table=JobOffer&columns=title&key1=b2b_min&operator1=>&value1=0&key2=permanent_min&operator2=>&value2=0&key3=mandate_min&operator3=>&value3=0</div>
    <div>Alternatively, to get all columns replace title with *</div>
    <div>/showtable?table=JobOffer&columns=*&key1=b2b_min&operator1=>&value1=0&key2=permanent_min&operator2=>&value2=0&key3=mandate_min&operator3=>&value3=0</div>
    <div>Order of all & parameters doesnt matter.</div>
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
        key1 = request.args.get("key1", False)
        operator1 = request.args.get("operator1", False)
        value1 = request.args.get("value1", False)
        key2 = request.args.get("key2", False)
        operator2 = request.args.get("operator2", False)
        value2 = request.args.get("value2", False)
        key3 = request.args.get("key3", False)
        operator3 = request.args.get("operator3", False)
        value3 = request.args.get("value3", False)
        if columns and key1 and operator1 and value2 and key2 and operator2 and value2 and key3 and operator3 and value3:
            select_txt = f"SELECT {columns} FROM \"{table_name}\""
            where_txt = f" WHERE \"{table_name}\".{key1}{operator1}%s"
            and1_txt = f" and \"{table_name}\".{key2}{operator2}%s"
            and2_txt = f" and \"{table_name}\".{key3}{operator3}%s"
            sql_txt = select_txt + where_txt + and1_txt + and2_txt
            query = pandas.read_sql(sql_txt, con=cnx, params=(value1, value2, value3,)).to_dict("records")
            return {'all offers': [{f'{table_name}': line} for line in query]}
        elif columns and key1 and operator1 and value1 and value2 and key2 and operator2 and value2:
            select_txt = f"SELECT {columns} FROM \"{table_name}\""
            where_txt = f" WHERE \"{table_name}\".{key1}{operator1}%s"
            and1_txt = f" and \"{table_name}\".{key2}{operator2}%s"
            sql_txt = select_txt + where_txt + and1_txt
            query = pandas.read_sql(sql_txt, con=cnx, params=(value1, value2,)).to_dict("records")
            return {'all offers': [{f'{table_name}': line} for line in query]}
        elif columns and key1 and operator1 and value1:
            select_txt = f"SELECT {columns} FROM \"{table_name}\""
            where_txt = f" WHERE \"{table_name}\".{key1}{operator1}%s"
            sql_txt = select_txt + where_txt
            query = pandas.read_sql(sql_txt, con=cnx, params=(value1,)).to_dict("records")
            return {'all offers': [{f'{table_name}': line} for line in query]}
        elif columns:
            columns = columns.split(',')
            query = pandas.read_sql_table(table_name, con=cnx, columns=columns).to_dict("records")
            return {'all offers': [{f'{table_name}': line} for line in query]}
        elif key1 and operator1 and value1:
            print("just key, operator, value")
            sql_txt = f"SELECT * FROM \"{table_name}\" WHERE \"{table_name}\".{key1}{operator1}%s"
            query = pandas.read_sql_query(sql_txt, con=cnx, params=(value1,)).to_dict("records")
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


