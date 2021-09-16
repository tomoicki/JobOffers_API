from flask import Blueprint, request, render_template
from sqlalchemy import inspect
import pandas
from JobOffers_API.database.PostrgeSQL_create_connection import postgre_connection

raw = Blueprint('raw', __name__)


@raw.route('/raw')
def raw_info():
    return render_template('raw.html', title='Raw version')


@raw.route('/raw/showtable')
def raw_showtable():
    table_name = request.args.get("table", False)
    if not table_name:
        inspector = inspect(postgre_connection)
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
            where_txt = f" WHERE \"{table_name}\".{key1} {operator1}%s"
            and1_txt = f" and \"{table_name}\".{key2} {operator2}%s"
            and2_txt = f" and \"{table_name}\".{key3} {operator3}%s"
            sql_txt = select_txt + where_txt + and1_txt + and2_txt
            query = pandas.read_sql(sql_txt, con=postgre_connection, params=(value1, value2, value3,)).to_dict("records")
            return {'all offers': [{f'{table_name}': line} for line in query]}
        elif columns and key1 and operator1 and value1 and value2 and key2 and operator2 and value2:
            select_txt = f"SELECT {columns} FROM \"{table_name}\""
            where_txt = f" WHERE \"{table_name}\".{key1} {operator1}%s"
            and1_txt = f" and \"{table_name}\".{key2} {operator2}%s"
            sql_txt = select_txt + where_txt + and1_txt
            query = pandas.read_sql(sql_txt, con=postgre_connection, params=(value1, value2,)).to_dict("records")
            return {'all offers': [{f'{table_name}': line} for line in query]}
        elif columns and key1 and operator1 and value1:
            select_txt = f"SELECT {columns} FROM \"{table_name}\""
            where_txt = f" WHERE \"{table_name}\".{key1} {operator1}%s"
            sql_txt = select_txt + where_txt
            query = pandas.read_sql(sql_txt, con=postgre_connection, params=(value1,)).to_dict("records")
            return {'all offers': [{f'{table_name}': line} for line in query]}
        elif columns:
            columns = columns.split(',')
            query = pandas.read_sql_table(table_name, con=postgre_connection, columns=columns).to_dict("records")
            return {'all offers': [{f'{table_name}': line} for line in query]}
        elif key1 and operator1 and value1:
            sql_txt = f"SELECT * FROM \"{table_name}\" WHERE \"{table_name}\".{key1} {operator1}%s"
            query = pandas.read_sql_query(sql_txt, con=postgre_connection, params=(value1,)).to_dict("records")
            return {'all offers': [{f'{table_name}': line} for line in query]}
        elif table_name:
            query = pandas.read_sql_table(table_name, con=postgre_connection).to_dict("records")
            return {'all offers': [{f'{table_name}': line} for line in query]}
        else:
            return {'message': 'something went wrong'}
