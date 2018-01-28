"""SQLite related functionality."""

import sqlite3
import os
from sqlite3 import Error
from PFT import dict as d
from PFT import classes as c


def create_connection(database):
    """Connect to database."""
    try:
        conn = sqlite3.Connection(database)
        print('Connected to:', database)
        return conn
    except Error as e:
        print(e)

    return None


def check_empty_db(conn):
    """Check if connected database is empty (no tables) and return bool."""
    cur = conn.cursor()
    cur.execute('SELECT * FROM sqlite_master')

    num = cur.fetchall()

    if not num:
        print('Database is Empty. Preparing Database...')
        return True
    else:
        print('Welsome back, setup already complete!')
        return False


def create_table(conn, create_table_sql):
    """Create new table using SQL."""
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(e)


def create_acct(conn, acct):
    """Create new account entry in accounts table."""
    try:
        info = (acct.type, acct.name, acct.amt)
        cur = conn.cursor()
        cur.execute(d.sql_cmd['createAcct'], info)
        pool = create_env_object(conn, 'Income Pool')
        pool.amt += acct.amt
        cur.execute(d.sql_cmd['updateEnv'], (pool.amt, 'Income Pool'))
    except Error as e:
        print(e)


def create_acct_object(conn, name):
    """Create an account object with details from table entry."""
    sql = "{}'{}'".format(d.sql_cmd['selectAcctName'], name)
    cur = conn.cursor()
    cur.execute(sql)
    t, n, a = cur.fetchone()
    acct = c.account(t, n, a)
    return acct


def create_grp(conn, name):
    """Create a new group in grops table."""
    cur = conn.cursor()
    try:
        cur.execute(d.sql_cmd['createGrp'], name)
    except Error as e:
        print(e)


def create_env(conn, env):
    """Create new envelope entry in envelopes table."""
    try:
        info = (env.group, env.name, env.amt)
        cur = conn.cursor()
        cur.execute(d.sql_cmd['createEnv'], info)
    except Error as e:
        print(e, 'env')


def create_env_object(conn, name):
    """Create an envelope object with details from table entry."""
    sql = "{}'{}'".format(d.sql_cmd['selectEnvName'], name)
    cur = conn.cursor()
    cur.execute(sql)
    g, n, a = cur.fetchone()
    if type(a) is not int:
        a = 0
    env = c.envelope(g, n, a)
    return env


def create_transfer(conn, t):
    try:
        info = (t.date, t.type, t.memo, t.amt,
                '', '', t.tIn.name, t.tOut.name)
        cur = conn.cursor()
        cur.execute(d.sql_cmd['createTrans'], info)
    except Error as e:
        print(e, 'trans')


def fund_env(conn, name, amt):
    pool = create_env_object(conn, 'Income Pool')
    env = create_env_object(conn, name)
    t = pool.envTransfer(env, amt)
    cur = conn.cursor()
    create_transfer(conn, t)
    cur.execute(d.sql_cmd['updateEnv'], (pool.amt, pool.name))
    cur.execute(d.sql_cmd['updateEnv'], (env.amt, env.name))
