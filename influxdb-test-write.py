# Author : Tony Cheng <tonycheng@cloudcube.com.tw>
# Version : 0.0.4
# Copyright(C) 2017 CloudCube Inc., All rights reserved

import random
import datetime
import argparse
import time
import influxdb
import pdb

from influxdb import InfluxDBClient
from influxdb.exceptions import InfluxDBServerError

db_host = '192.168.141.140'
db_port = 8086
db_user = ''
db_password = ''
db_name = 'tony1'

sleep_time = 0
hold_time = 3

def connect_db(host, port, user, password, dbname):
    try:
        client = InfluxDBClient(host, port, user, password)
        database = client.get_list_database()
        ''' client.get_list_database()
            e.g. [{u'name': u'_internal'}, {u'name': u'monasca'}]
            <type 'list'>
        '''
        db_exist = False
        for current_dbname in database:
            item = current_dbname
            if dbname in (item[u'name']):
                print("Database: %s is exist, switch database to %s") % (dbname, dbname)
                db_exist = True
                client.switch_database(dbname)
                print("DB connected")
                return client
        if not db_exist:
            print("DB is not exist, trying to create database.....")
            client.create_database(dbname)
            print("DB %s created, trying to switch database") % dbname
            client.switch_database(dbname)
            return client
    except influxdb.client.InfluxDBClientError as e:
        raise Exception(str(e))

def write_db(client):
    result = random.randrange(0, 101)
    item = random.choice (['swim', 'bike', 'run'])
    athletes = random.choice (['tony', 'lucy', 'baby'])
    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    json_body = [
    {
        "measurement": "triathlon",
        "tags": {
            "age": "40",
            "athletes": athletes,
            "item": item,
            "sn": sn
        },
        "time": timestamp,
        "fields": {
            "result": result
        }
    }
    ]
    print("Write points: {0}".format(json_body))

    try:
        client.write_points(json_body)
    except InfluxDBServerError as e_influxdbserver_err:
        #pdb.set_trace()
        if '503' in e_influxdbserver_err.message:
            time.sleep(hold_time)
            print("Caught '503 Service Unavailable' exception, need to wait and retry again.....")
            client.write_points(json_body)

def check_db_result(client):
    db_count_stmt = 'SELECT COUNT(result) FROM /./'
    points_count_raw = client.query(db_count_stmt)
    points_count_result = points_count_raw.raw['series'][0]['values'][0][1]
    print("Acutal write points: {0}".format(points_count_result))

def parser():
    parser = argparse.ArgumentParser(
        description='testing insert code to play with InfluxDB')
    #subparsers = parser.add_subparsers()
    parser.add_argument('--host', type=str, required=False, default=db_host,
                        help='hostname of InfluxDB http API')
    parser.add_argument('--port', type=int, required=False, default=db_port,
                        help='port of InfluxDB http API')
    parser.add_argument('--user', type=str, required=False, default=db_user,
                        help='user of InfluxDB http API')
    parser.add_argument('--password', type=str, required=False, default=db_password,
                        help='password of InfluxDB http API')
    parser.add_argument('--dbname', type=str, required=False, default=db_name,
                        help='DB name of InfluxDB http API')
    return parser.parse_args()


if __name__ == '__main__':
    sn = 0
    args = parser()
    if True:
        client = connect_db(host=args.host, port=args.port, user=args.user, password=args.password, dbname=args.dbname)
        print "Start : %s" % time.ctime()
        try:
            while True:
                sn+=1
                write_db(client)
                time.sleep(sleep_time)
        except KeyboardInterrupt:
            print("End : %s") % time.ctime()
            print("Total write points: %i") % sn
            check_db_result(client)
