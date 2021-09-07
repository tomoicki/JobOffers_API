from flask import Flask, request, render_template, flash, redirect, url_for, session
from sqlalchemy import inspect, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
import pandas
from os import environ as env
from dotenv import load_dotenv
from utilities.PostgreSQL_connection_functions import connection2db
from utilities.PostgreSQL_tables_declaration import *
from utilities.PostgreSQL_data_insert import update_tables
import numpy as np
from psycopg2.extensions import register_adapter, AsIs
import psycopg2.errors

register_adapter(np.int64, psycopg2._psycopg.AsIs)

load_dotenv()
pandas.set_option('display.max_columns', None)
pandas.set_option('display.max_rows', None)
pandas.set_option('display.width', None)
pandas.set_option('display.max_colwidth', 100)
pandas.options.mode.chained_assignment = None
#  make connection with PostgreSQL
cnx = connection2db(env['PostgreSQL_host2'], env['PostgreSQL_port2'], env['PostgreSQL_user2'],
                    env['PostgreSQL_password2'], env['PostgreSQL_db_name2'])
Session = sessionmaker(bind=cnx)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'would like not to have this but apparently i have to'


@app.route('/')
def welcome():
    return render_template('base.html', title='Welcome!')


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin.html', title='Login as admin')
    elif request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        if name != env['admin'] or password != env['password']:
            flash('Please check your login details and try again.')
            return redirect(url_for('admin_login'))
        return redirect(url_for('admin_panel'))


@app.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    sqlalchemy_session = Session()
    operators = ['=', '>', '<', '>=', '<=', '<>', 'LIKE']
    inspector = inspect(cnx)
    list_of_tables = inspector.get_table_names()
    modify_tables = [item for item in list_of_tables if 'association' not in item]
    other_tables = [item for item in modify_tables if item != 'JobOffer']
    title = request.form.get('title', False)
    other_table_value = request.form.get('other_table_value', False)
    other_table_optional = request.form.get('other_table_optional', False)
    get_record_column = request.form.get('get_record_column', session.get('get_record_column'))
    modify_record_value = request.form.get('modify_record_value', False)
    delete_button = request.form.get('delete_record_button', False)
    if request.method == 'GET':
        return render_template('admin_panel.html', title="Admin panel", other_tables=other_tables,
                               modify_tables=modify_tables, operators=operators)
    elif request.method == 'POST':
        if title:
            job_offer_record = {'title': request.form.get('title'), 'location': request.form.get('location').split(','),
                                'company': request.form.get('company'),
                                'company_size': request.form.get('company_size'),
                                'experience': request.form.get('experience').split(','),
                                'employment_type': request.form.get('employment_type').split(','),
                                'b2b_min': 0, 'b2b_max': 0, 'permanent_min': 0,
                                'permanent_max': 0, 'mandate_min': 0, 'mandate_max': 0,
                                'skills_must': request.form.get('skill_must').split(','),
                                'skills_nice': request.form.get('skill_nice').split(','),
                                'expired': 'false', 'expired_at': '', 'scraped_at': '',
                                'jobsite': request.form.get('jobsite'), 'offer_url': request.form.get('offer_url')}
            keys, values = list(job_offer_record.keys()), list(job_offer_record.values())
            try:
                job_offer_df = pandas.DataFrame([values], columns=keys)
                update_tables(job_offer_df, Session)
                flash('Offer successfully added.', category='job_offer')
            except:
                flash("Couldn't add new job offer.")
        if other_table_value:
            table = request.form.get('other_table')
            table_as_schema = find_table(table)
            try:
                if other_table_optional:
                    record = table_as_schema(other_table_value, other_table_optional)
                else:
                    record = table_as_schema(other_table_value)
                sqlalchemy_session.add(record)
                sqlalchemy_session.commit()
                flash(f'Record to {table} successfully added.', category='other_table')
            except:
                flash("Couldn't add new record.")
        if get_record_column:
            table_name = request.form.get('get_record_table', session.get('table_name'))
            table_as_schema = find_table(table_name)
            operator1 = request.form.get('get_record_operator', session.get('operator1'))
            get_record_value = request.form.get('get_record_value', session.get('get_record_value'))
            stmt = text(f"\"{table_name}\".{get_record_column} {operator1} \'{get_record_value}\'")
            record = sqlalchemy_session.query(table_as_schema).filter(stmt).first()
            if record is not None:
                record_dict = record.__dict__
                record_dict = {key: value for key, value in record_dict.items() if 'instance' not in key}
                record_column_to_change = list(record_dict.keys())
                record_column_to_change = [item for item in record_column_to_change if 'id' not in item]
                session['get_record_column'] = get_record_column
                session['get_record_value'] = get_record_value
                session['table_name'] = table_name
                session['operator1'] = operator1
                if modify_record_value:
                    modify_record__column_to_change = request.form.get('modify_record__column_to_change')
                    execute = table_as_schema.__table__.update().where(
                        table_as_schema.id == record.__dict__['id']).values(
                        {modify_record__column_to_change: modify_record_value})
                    sqlalchemy_session.execute(execute)
                    sqlalchemy_session.commit()
                    flash('Record successfully modified.', category='record_changed')
                if delete_button is not False:
                    try:
                        execute = table_as_schema.__table__.delete().where(table_as_schema.id == record.__dict__['id'])
                        sqlalchemy_session.execute(execute)
                        sqlalchemy_session.commit()
                        flash('Record successfully deleted.', category='record_deleted')
                    except IntegrityError:
                        flash('Foreign key violation. Cannot delete.', category='cannot_delete')
                return render_template('admin_panel.html', other_tables=other_tables, modify_tables=modify_tables,
                                       operators=operators, record_dict=record_dict, record_column_to_change=record_column_to_change,
                                       table_as_schema=table_as_schema, record=record)
            else:
                flash("Couldn't find record.", category='no_record')
        return render_template('admin_panel.html', other_tables=other_tables, modify_tables=modify_tables,
                               operators=operators)


@app.route('/showtable')
def showtable():
    old_values = []
    operators = ['=', '>', '<', '>=', '<=', '<>', 'LIKE']
    inspector = inspect(cnx)
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
            dataframe = pandas.read_sql(sql_txt, con=cnx, params=(value1, value2, value3,))
            headers = dataframe.columns.to_list()
            return render_template('interface.html', title='Interface', tables=list_of_tables, headers=headers,
                                   dataframe=dataframe.values.tolist(), operators=operators, old_dict=old_dict)
        elif key1 and operator1 and value1 and value2 and key2 and operator2 and value2:
            select_txt = f"SELECT {columns} FROM \"{table_name}\""
            where_txt = f" WHERE \"{table_name}\".{key1} {operator1}%s"
            and1_txt = f" and \"{table_name}\".{key2} {operator2}%s"
            sql_txt = select_txt + where_txt + and1_txt
            dataframe = pandas.read_sql(sql_txt, con=cnx, params=(value1, value2,))
            headers = dataframe.columns.to_list()
            return render_template('interface.html', title='Interface', tables=list_of_tables, headers=headers,
                                   dataframe=dataframe.values.tolist(), operators=operators, old_dict=old_dict)
        elif key1 and operator1 and value1:
            select_txt = f"SELECT {columns} FROM \"{table_name}\""
            where_txt = f" WHERE \"{table_name}\".{key1} {operator1}%s"
            sql_txt = select_txt + where_txt
            dataframe = pandas.read_sql(sql_txt, con=cnx, params=(value1,))
            headers = dataframe.columns.to_list()
            return render_template('interface.html', title='Interface', tables=list_of_tables, headers=headers,
                                   dataframe=dataframe.values.tolist(), operators=operators, old_dict=old_dict)
        elif len(columns) >= 2:
            columns = columns.split(',')
            dataframe = pandas.read_sql_table(table_name, con=cnx, columns=columns)
            headers = dataframe.columns.to_list()
            return render_template('interface.html', title='Interface', tables=list_of_tables, headers=headers,
                                   dataframe=dataframe.values.tolist(), operators=operators, old_dict=old_dict)
        else:
            dataframe = pandas.read_sql_table(table_name, con=cnx)
            headers = dataframe.columns.to_list()
            return render_template('interface.html', title='Interface', tables=list_of_tables, headers=headers,
                                   dataframe=dataframe.values.tolist(), operators=operators, old_dict=old_dict)
    else:
        old_dict = dict(zip(old_keys, old_values))
        return render_template('interface.html', title='Interface', tables=list_of_tables,
                               operators=operators, old_dict=old_dict)


@app.route('/raw')
def raw():
    return render_template('raw.html', title='Raw version')


@app.route('/raw/showtable')
def raw_showtable():
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
            where_txt = f" WHERE \"{table_name}\".{key1} {operator1}%s"
            and1_txt = f" and \"{table_name}\".{key2} {operator2}%s"
            and2_txt = f" and \"{table_name}\".{key3} {operator3}%s"
            sql_txt = select_txt + where_txt + and1_txt + and2_txt
            query = pandas.read_sql(sql_txt, con=cnx, params=(value1, value2, value3,)).to_dict("records")
            return {'all offers': [{f'{table_name}': line} for line in query]}
        elif columns and key1 and operator1 and value1 and value2 and key2 and operator2 and value2:
            select_txt = f"SELECT {columns} FROM \"{table_name}\""
            where_txt = f" WHERE \"{table_name}\".{key1} {operator1}%s"
            and1_txt = f" and \"{table_name}\".{key2} {operator2}%s"
            sql_txt = select_txt + where_txt + and1_txt
            query = pandas.read_sql(sql_txt, con=cnx, params=(value1, value2,)).to_dict("records")
            return {'all offers': [{f'{table_name}': line} for line in query]}
        elif columns and key1 and operator1 and value1:
            select_txt = f"SELECT {columns} FROM \"{table_name}\""
            where_txt = f" WHERE \"{table_name}\".{key1} {operator1}%s"
            sql_txt = select_txt + where_txt
            query = pandas.read_sql(sql_txt, con=cnx, params=(value1,)).to_dict("records")
            return {'all offers': [{f'{table_name}': line} for line in query]}
        elif columns:
            columns = columns.split(',')
            query = pandas.read_sql_table(table_name, con=cnx, columns=columns).to_dict("records")
            return {'all offers': [{f'{table_name}': line} for line in query]}
        elif key1 and operator1 and value1:
            sql_txt = f"SELECT * FROM \"{table_name}\" WHERE \"{table_name}\".{key1} {operator1}%s"
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
