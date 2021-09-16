from flask import Blueprint, request, render_template, flash, redirect, url_for, session
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
import pandas
from os import environ as env
from dotenv import load_dotenv
from database.PostgreSQL_tables_declaration import *
from database.PostgreSQL_data_insert import update_tables
import numpy
from psycopg2.extensions import register_adapter
import psycopg2.errors
from database.PostrgeSQL_create_connection import postgre_session, postgre_connection

register_adapter(numpy.int64, psycopg2._psycopg.AsIs)
load_dotenv()
admin = Blueprint('admin', __name__)


@admin.route('/admin', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin.html', title='Login as admin')
    elif request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        if name != env['admin'] or password != env['password']:
            flash('Please check your login details and try again.')
            return redirect(url_for('admin.admin_login'))
        return redirect(url_for('admin.admin_panel'))


@admin.route('/admin_panel', methods=['GET', 'POST'])
def admin_panel():
    sqlalchemy_session = postgre_session()
    operators = ['=', '>', '<', '>=', '<=', '<>', 'LIKE']
    inspector = inspect(postgre_connection)
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
                update_tables(job_offer_df, postgre_session)
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
