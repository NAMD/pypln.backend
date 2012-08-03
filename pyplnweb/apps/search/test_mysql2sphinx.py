#!/usr/bin/env python

import unittest
from random import random
from textwrap import dedent
import MySQLdb
from mysql2sphinx import MySqlInspector, create_configuration_group


connection_data = {'host': 'localhost', 'user': 'root', 'passwd': 'r00t'}
database_name = 'test_mysql2sphinx'

class TestMySqlInspector(unittest.TestCase):
    def setUp(self):
        self.connection = MySQLdb.connect(**connection_data)
        self.connection.query('CREATE DATABASE IF NOT EXISTS ' + database_name)
        self.connection.select_db(database_name)
        self.cursor = self.connection.cursor()

    def tearDown(self):
        self.cursor.close()
        self.connection.query('DROP DATABASE IF EXISTS ' + database_name)
        self.connection.close()

    def test_get_tables(self):
        tables_created = []
        for i in range(int(random() * 10)):
            table_name = 'table_%d' % i
            self.cursor.execute('CREATE TABLE %s (id INT(11), name TEXT)' % table_name)
            tables_created.append(table_name)
        mysql_inspect = MySqlInspector(connection_data['host'],
                                       connection_data['user'],
                                       connection_data['passwd'])
        tables = mysql_inspect.get_tables(database_name)
        self.assertEquals(tables, tables_created)

    def test_get_columns(self):
        self.connection.query('''
                CREATE TABLE just_testing (
                    id INT(11) PRIMARY KEY,
                    name VARCHAR(50),
                    weight FLOAT,
                    description TEXT
                )''')
        mysql_inspect = MySqlInspector(connection_data['host'],
                                       connection_data['user'],
                                       connection_data['passwd'])
        columns_info = mysql_inspect.get_columns('just_testing', database_name)
        self.assertEquals(columns_info, [('id', 'int(11)', 'PRI'),
                                         ('name', 'varchar(50)', ''),
                                         ('weight', 'float', ''),
                                         ('description', 'text', '')])

class TestSphinxConfiguration(unittest.TestCase):
    def test_create_configuration_group(self):
        data = {'config1': 'value1', 'config2': 'value2', 'config3': 'value3'}
        output = create_configuration_group('source', 'testing', data)
        lines = output.split('\n')
        self.assertEquals(lines[0], 'source testing {')
        self.assertIn('        config1              = value1', lines)
        self.assertIn('        config2              = value2', lines)
        self.assertIn('        config3              = value3', lines)
        self.assertEquals(lines[-1], '}')
