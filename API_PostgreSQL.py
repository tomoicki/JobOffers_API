from flask import Flask, request, render_template
from sqlalchemy import inspect
import pandas
from os import environ as env
from dotenv import load_dotenv
from utilities.PostgreSQL_connection_functions import connection2db

load_dotenv()
pandas.set_option('display.max_columns', None)
pandas.set_option('display.max_rows', None)
pandas.set_option('display.width', None)
pandas.set_option('display.max_colwidth', 100)
pandas.options.mode.chained_assignment = None

#  make connection with PostgreSQL
cnx = connection2db(env['PostgreSQL_host2'], env['PostgreSQL_port2'], env['PostgreSQL_user2'],
                    env['PostgreSQL_password2'], env['PostgreSQL_db_name2'])

app = Flask(__name__)


@app.route('/')
def welcome():
    return render_template('base.html', title='Welcome!')


@app.route('/interface', methods=['POST', 'GET'])
def interface():
    inspector = inspect(cnx)
    list_of_tables = inspector.get_table_names()
    table_name = request.args.get("table", False)
    if table_name:
        dataframe = pandas.read_sql_table(table_name, con=cnx)
        headers = dataframe.columns.to_list()
        print(headers)
        print(dataframe.values.tolist())
        return render_template('interface.html', tables=list_of_tables, headers=headers, dataframe=dataframe.values.tolist())
    else:
        return render_template('interface.html', tables=list_of_tables)


@app.route('/interface/showtable', methods=['POST', 'GET'])
def interface_showtable():
    inspector = inspect(cnx)
    list_of_tables = inspector.get_table_names()
    return render_template('interface_showtable.html', tables=list_of_tables)


@app.route('/raw', methods=['POST', 'GET'])
def raw():
    return render_template('raw.html', title='Raw version')


@app.route('/raw/showtable',  methods=['POST', 'GET'])
def raw_show_table():
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
            sql_txt = f"SELECT * FROM \"{table_name}\" WHERE \"{table_name}\".{key1}{operator1}%s"
            query = pandas.read_sql_query(sql_txt, con=cnx, params=(value1,)).to_dict("records")
            return {'all offers': [{f'{table_name}': line} for line in query]}
        elif table_name:
            query = pandas.read_sql_table(table_name, con=cnx).to_dict("records")
            return {'all offers': [{f'{table_name}': line} for line in query]}
        else:
            return {'message': 'something went wrong'}


if __name__ == '__main__':
    # app.run(debug=False, host='192.168.222.116')
    app.run(debug=False)
