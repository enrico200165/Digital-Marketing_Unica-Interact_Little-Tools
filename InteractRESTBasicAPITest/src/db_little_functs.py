#!/usr/bin/env python

import pyodbc
import time
import globals as g

def generateSQLForAudID(audIDVal):
    s = g.params_db.db_query_whole_row+";"
    s = s.format(audIDVal)
    return s


def generateSQLForAudIDAttr(attributeName, audIDVal):
    s = g.params_db.db_query_attr+";"
    s = s.format(attributeName, audIDVal)
    return s


def dbGetAudIDRows(AudienceID, sleepMillisecs = 0, verbose = False):
    ''' https://github.com/mkleehammer/pyodbc/wiki/Row '''
    connStr = "DRIVER={SQL Server};"\
              + "Server={};".format(g.params_db.db_server)\
              + "Database={};".format(g.params_db.db_name) \
              + "UID={};".format(g.params_db.db_user) \
              + "PWD={};".format(g.params_db.db_pwd) \
              + "Trusted_Connection=yes;"
    conn = pyodbc.connect(connStr)

    cursor = conn.cursor()
    queryString = generateSQLForAudIDAttr(AudienceID)
    time.sleep(sleepMillisecs/1000)
    cursor.execute(queryString)

    columns = [column[0] for column in cursor.description]
    # print(columns)
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    if verbose:
        for row in results:
            print('row = %r' % (row,))

    return results


def dbGetAudIDRow(AudienceID, sleepMillisecs = 0, verbose = False):
    ''' https://github.com/mkleehammer/pyodbc/wiki/Row '''
    connStr = "DRIVER={SQL Server};" \
              + "Server={};".format(g.params_db.db_server) \
              + "Database={};".format(g.params_db.db_name) \
              + "UID={};".format(g.params_db.db_user) \
              + "PWD={};".format(g.params_db.db_pwd) \
              + "Trusted_Connection=yes;"
    conn = pyodbc.connect(connStr)

    cursor = conn.cursor()
    queryString = generateSQLForAudID(AudienceID)
    time.sleep(sleepMillisecs/1000)
    cursor.execute(queryString)

    columns = [column[0] for column in cursor.description]
    # print(columns)
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))

    if verbose:
        for row in results:
            print('row = %r' % (row,))
    if len(results) == 1:
        return results[0]
    else:
        return None


def dbGetProfileCol(AudienceID, attribute, sleepMillisecs = 0, verbose = False):
    ''' https://github.com/mkleehammer/pyodbc/wiki/Row '''

    connStr = "DRIVER={SQL Server};" \
              + "Server={};".format(g.params_db.db_server) \
              + "Database={};".format(g.params_db.db_name) \
              + "UID={};".format(g.params_db.db_user) \
              + "PWD={};".format(g.params_db.db_pwd) \
              + "Trusted_Connection=yes;"
    conn = pyodbc.connect(connStr)

    cursor = conn.cursor()
    queryString = generateSQLForAudIDAttr(attribute, AudienceID)
    time.sleep(sleepMillisecs/1000)
    try:
        ret = cursor.execute(queryString)
    except Exception as e:
        g.log.error("query failed")
        return None

    columns = [column[0] for column in cursor.description]
    # print(columns)
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))

    if verbose:
        for row in results:
            print('row = %r' % (row,))
    if len(results) == 1:
        return results[0]
    else:
        return None
