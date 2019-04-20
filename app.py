#!/usr/bin/env python3

import flask
from werkzeug.contrib.cache import MemcachedCache

from constants import TICKETS_GRAPH
from db_utils import db_conn
from http_utils import resp
from serializers import tickets_serializer
from validators import validate_fields

app = flask.Flask(__name__)
app.config.from_object('config')
cache = MemcachedCache([app.config['MEMCACHE_SERVER']])


@app.errorhandler(400)
def page_not_found(e):
    return resp(400, {})


@app.errorhandler(404)
def page_not_found(e):
    return resp(400, {})


@app.errorhandler(405)
def page_not_found(e):
    return resp(405, {})


@app.route('/')
def root():
    return flask.redirect('/api/1.0/tickets')


@app.route('/api/1.0/tickets/', methods=['PUT'])
def put_ticket():
    (json, errors) = validate_fields(['theme', 'text', 'email'])
    if errors:
        return resp(400, {"errors": errors})

    connection = db_conn(app)
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO tickets (theme, text, email) VALUES ('{}', '{}', '{}')".format(
                json['theme'],
                json['text'],
                json['email']
            )
            cursor.execute(sql)
        connection.commit()
    finally:
        connection.close()

    cache.delete('tickets')
    return resp(200, {"ticket_id": cursor.lastrowid})


@app.route('/api/1.0/tickets/', methods=['GET'])
def get_themes():
    tickets = cache.get('tickets')
    if tickets is None:
        connection = db_conn(app)
        try:
            with connection.cursor() as cursor:
                sql = """
                    SELECT t.id as 't.id', t.theme as 't.theme', t.text as 't.text', t.email as 't.email', 
                    t.state as 't.state', t.created_at as 't.created_at', t.updated_at as 't.updated_at',
                    c.id as 'c.id', c.ticket_id as 'c.ticket_id', c.text as 'c.text', c.email as 'c.email', 
                    c.created_at as 'c.created_at', c.updated_at as 'c.updated_at'
                    FROM tickets AS t 
                    LEFT JOIN comments AS c 
                    ON t.id = c.ticket_id
                    ORDER BY t.created_at DESC, c.created_at DESC
                """
                cursor.execute(sql)
            connection.commit()
            result = cursor.fetchall()
        finally:
            connection.close()

        tickets = tickets_serializer(result)
        cache.set('tickets', tickets, timeout=5 * 60)

    return resp(200, {"tickets": tickets})


@app.route('/api/1.0/tickets/<id>/', methods=['POST'])
def post_ticket(id):
    (json, errors) = validate_fields(['state'])
    if errors:
        return resp(400, {"errors": errors})

    status_code = 400
    response = {"msg": "Can't change this ticket to {} state".format(json['state'])}
    connection = db_conn(app)
    try:
        with connection.cursor() as cursor:
            sql = "SELECT id, state FROM tickets WHERE id = {}".format(id)
            cursor.execute(sql)
        connection.commit()

        current_ticket = cursor.fetchone()
        if json['state'] in TICKETS_GRAPH[current_ticket['state']]:
            with connection.cursor() as cursor:
                sql = "UPDATE tickets SET state = '{}' WHERE id = {}".format(
                    json['state'],
                    id
                )
                cursor.execute(sql)
                connection.commit()

            status_code = 200
            response = {"ticket_id": id}
    finally:
        connection.close()

    cache.delete('tickets')
    return resp(status_code, response)


@app.route('/api/1.0/comments/', methods=['PUT'])
def put_comment():
    (json, errors) = validate_fields(['ticket_id', 'text', 'email'])
    if errors:
        return resp(400, {"errors": errors})
    connection = db_conn(app)
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO comments (ticket_id, text, email) VALUES ('{}', '{}', '{}')".format(
                json['ticket_id'],
                json['text'],
                json['email']
            )
            cursor.execute(sql)
        connection.commit()
    finally:
        connection.close()

    cache.delete('tickets')
    return resp(200, {"comment_id": cursor.lastrowid})


if __name__ == '__main__':
    app.debug = True
    app.run(host=app.config['UWSGI_HOST'])
