"""
Configure PyMySQL as a drop-in replacement for MySQLdb.

This module installs PyMySQL under the MySQLdb name so that frameworks
(such as Django) that expect the MySQLdb library can work with PyMySQL
without any further configuration.
"""

import pymysql
pymysql.install_as_MySQLdb()
