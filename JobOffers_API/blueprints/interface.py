from flask import Blueprint, request, render_template
from sqlalchemy import inspect
import pandas
from JobOffers_API.database.PostrgeSQL_create_connection import postgre_connection

interface = Blueprint('interface', __name__)


@interface.route('/showtable')
def showtable():
    old_values = []
    operators = ['=', '>', '<', '>=', '<=', '<>', 'LIKE']
    inspector = inspect(postgre_connection)
    list_of_tables = inspector.get_table_names()
    table_name = request.args.get("table", False)
    old_keys = ['columns', 'key1', 'operator1', 'value1', 'key2', 'operator2', 'value2', 'key3', 'operator3', 'value3']
    if table_name:
        columns = request.args.get("columns", '*')
        key1 = request.args.get("key1", False)
        operator1 = request.args.get("operator1", False)
        value1 = request.args.get("value1", False)
        key2 = request.args.get("key2", False)
        operator2 = request.args.get("operator2", False)
        value2 = request.args.get("value2", False)
        key3 = request.args.get("key3", False)
        operator3 = request.args.get("operator3", False)
        value3 = request.args.get("value3", False)
        old_values.extend([columns, key1, operator1, value1, key2, operator2, value2, key3, operator3, value3])
        old_dict = dict(zip(old_keys, old_values))
        if len(columns) == 0:
            columns = '*'
        if key1 and operator1 and value2 and key2 and operator2 and value2 and key3 and operator3 and value3:
            select_txt = f"SELECT {columns} FROM \"{table_name}\""
            where_txt = f" WHERE \"{table_name}\".{key1} {operator1}%s"
            and1_txt = f" and \"{table_name}\".{key2} {operator2}%s"
            and2_txt = f" and \"{table_name}\".{key3} {operator3}%s"
            sql_txt = select_txt + where_txt + and1_txt + and2_txt
            dataframe = pandas.read_sql(sql_txt, con=postgre_connection, params=(value1, value2, value3,))
            headers = dataframe.columns.to_list()
            return render_template('interface.html', title='Interface', tables=list_of_tables, headers=headers,
                                   dataframe=dataframe.values.tolist(), operators=operators, old_dict=old_dict)
        elif key1 and operator1 and value1 and value2 and key2 and operator2 and value2:
            select_txt = f"SELECT {columns} FROM \"{table_name}\""
            where_txt = f" WHERE \"{table_name}\".{key1} {operator1}%s"
            and1_txt = f" and \"{table_name}\".{key2} {operator2}%s"
            sql_txt = select_txt + where_txt + and1_txt
            dataframe = pandas.read_sql(sql_txt, con=postgre_connection, params=(value1, value2,))
            headers = dataframe.columns.to_list()
            return render_template('interface.html', title='Interface', tables=list_of_tables, headers=headers,
                                   dataframe=dataframe.values.tolist(), operators=operators, old_dict=old_dict)
        elif key1 and operator1 and value1:
            select_txt = f"SELECT {columns} FROM \"{table_name}\""
            where_txt = f" WHERE \"{table_name}\".{key1} {operator1}%s"
            sql_txt = select_txt + where_txt
            dataframe = pandas.read_sql(sql_txt, con=postgre_connection, params=(value1,))
            headers = dataframe.columns.to_list()
            return render_template('interface.html', title='Interface', tables=list_of_tables, headers=headers,
                                   dataframe=dataframe.values.tolist(), operators=operators, old_dict=old_dict)
        elif len(columns) >= 2:
            columns = columns.split(',')
            dataframe = pandas.read_sql_table(table_name, con=postgre_connection, columns=columns)
            headers = dataframe.columns.to_list()
            return render_template('interface.html', title='Interface', tables=list_of_tables, headers=headers,
                                   dataframe=dataframe.values.tolist(), operators=operators, old_dict=old_dict)
        else:
            dataframe = pandas.read_sql_table(table_name, con=postgre_connection)
            headers = dataframe.columns.to_list()
            return render_template('interface.html', title='Interface', tables=list_of_tables, headers=headers,
                                   dataframe=dataframe.values.tolist(), operators=operators, old_dict=old_dict)
    else:
        old_dict = dict(zip(old_keys, old_values))
        return render_template('interface.html', title='Interface', tables=list_of_tables,
                               operators=operators, old_dict=old_dict)
