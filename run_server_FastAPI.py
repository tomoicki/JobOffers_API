from fastapi import FastAPI
from sqlalchemy import inspect
import uvicorn
import pandas
from utilities.functions import connection2db
from utilities.db_creds import host, port, user, password, db_name
from typing import Optional


app = FastAPI()


@app.get('/')
def info():
    readme = f"""
    You can get data about job offers scraped from https://nofluffjobs.com/pl/.
    The data is stored on remote PostgreSQL database.
    To get the data you have to insert correct link into your browser address bar.
    To get currently stored Tables go to:
    /showtable
    To get whole data from selected Table you have to use:
    /showtable?name=table_name
    replace table_name with real Table name that is stored in DB.
    For example to get data from table 'All' your link would look:
    /showtable?name=All
    to narrow it down and get only one column from table you need to add ?column=column_name
    For example to only get data from column 'job_name' in 'All' your link needs to be:
    /showtable?name=All&column=job_name
    Alternatively, you can request info from specific row from table, to do this replace 'column' with 'row' 
    and give int value as row number. Example:
    /showtable?name=All&row=5
    Finally, to get just the value of table[row][column] add both &row= and &column= . Example:
    /showtable?name=All&column=job_name&row=4
    /showtable?name=All&row=4&column=job_name
    Order of &column and &row doesn't matter, both above queries will give same response.
    """
    return readme


@app.get('/showtable')
def table(name: Optional[str] = None, row: Optional[int] = None, column: Optional[str] = None):
    cnx = connection2db(host, port, user, password, db_name)
    inspector = inspect(cnx)
    out = dict(zip([i for i in range(len(inspector.get_table_names()))],
                   [item for item in inspector.get_table_names()]))
    if name:
        df = pandas.read_sql(name, cnx)
        out = df.to_json(orient='index')
        if column is None and row is None:
            out = df.to_json(orient='index')
        elif column is None and row is not None:
            out = df.loc[row, :].to_json(orient='index')
        elif column is not None and row is None:
            out = df[column].to_json(orient='index')
        else:
            out = df.loc[row, column]
    return out


if __name__ == '__main__':
    # app.run(debug=False, host='192.168.222.116')
    uvicorn.run(app, port=8000)
