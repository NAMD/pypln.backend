#!/usr/bin/env python

import MySQLdb
from textwrap import dedent


class MySqlInspector(object):
    """This class inspects MySQL databases, returning the name of its tables
    and the name, type and key options of columns from a desired table.

    Example::

        inspector = MySqlInspector('localhost', 'root', '')
        for table in inspector.get_tables('mydb'):
            print 'Rows of table %s:' % table
            for row_info in inspector.get_columns(table):
                print '  name: %s, type: %s, key: %s' % row_info

    """
    def _select_database(self, database_name):
        if database_name is not None:
            self.connection.select_db(database_name)
            self.database_name = database_name

    def __init__(self, hostname, username, password, database_name=None):
        """This method initializes the object with data about MySQL connection.
        ``database_name`` is optional."""
        self.hostname = hostname
        self.username = username
        self.password = password
        self.connection = MySQLdb.connect(host=hostname, user=username,
                                          passwd=password)
        self.cursor = self.connection.cursor()
        self._select_database(database_name)

    def get_tables(self, database_name=None):
        """This method returns a list of the tables of a given database.
        If ``database_name`` is not specified it'll use the last database used
        (in ``get_tables`` or ``get_columns``)."""
        self._select_database(database_name)
        self.cursor.execute('SHOW TABLES')
        table_names = self.cursor.fetchall()
        return [row[0] for row in table_names]

    def get_columns(self, table_name, database_name=None):
        """This method return information about columns of a table from a given
        database.
        If ``database_name`` is not specified it'll use the last database used
        (in ``get_tables`` or ``get_columns``).
        The information returned is a list of tuples in which each tuple is in
        form of: ``(row_name, row_type, key_options)``, for example::
            ('id',  'int(11)', 'PRI')
        """
        self._select_database(database_name)
        self.cursor.execute('DESCRIBE ' + table_name)
        return [(info[0], info[1], info[3]) for info in self.cursor.fetchall()]


def create_configuration_group(command, name, info):
    info_formatted = '\n'.join(['        %-20s = %s' % (key, value) \
                                for key, value in info.iteritems()])
    return '%s %s {\n%s\n}' % (command, name, info_formatted)

