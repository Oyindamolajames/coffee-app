from crypt import methods
from functools import wraps
import os
from select import EPOLL_CLOEXEC
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, check_permissions, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()


# ROUTES
'''
@ TODO: implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''


@app.route("/drinks", methods=['GET'])
def get_drinks():
    try:
        drinks = Drink.query.all()
    except BaseException:
        abort(400)
    finally:        
        return jsonify({
            'success': True,
            'drinks': [drink.short() for drink in drinks]
        }), 200


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail", methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drink_detail(payload):
    drinks = Drink.query.all()

    return jsonify({
        'success': True,
        'drinks': [drink.long() for drink in drinks] 
    }), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks", methods=["POST"])
@requires_auth('post:drinks')
def add_drinks(payload):
    req = request.get_json()

    if 'title' and 'recipe' not in req:
        abort(400)
    try:
        title = req['title']
        recipe = json.dumps(req['recipe'])
        drink = Drink(title=title, recipe=recipe)
        print(title)
        print(recipe)
        drink.insert()
    except :
        abort(422)
    finally:
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
            }), 200    
        
           



'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks/<int:id>", methods=["PATCH"])
@requires_auth('patch:drinks')
def update_drinks(payload, id):
    req = request.get_json()
    drink = Drink.query.get(id)
    if drink is None:
        abort(404)
    try:
        if 'title' in req:
            drink.title = req['title']

        if 'recipe' in req:
            drink.recipe = json.dumps(req['recipe'])

        drink.update()  
        print(drink)  
    except BaseException:
        abort(400)

    finally:
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        }), 200


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks/<int:id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drinks(payload, id):
    drink = Drink.query.get(id)
    if not drink:
        abort (404)
    try:
        drink.delete()
    except BaseException:
        abort(400)
    finally:
        return jsonify({
            'success': True,
            'delete': id 
        }), 200



# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def resource_not_found(error):
    jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(401)
def unathorized(error):
    jsonify({
        "success": False,
        "error": 401,
        "message": "resource not found"
    }), 401

@app.errorhandler(400)
def bad_request(error):
    jsonify({
        'success': True,
        'error': 400,
        'message': 'Bad request'
    }), 400    

@app.errorhandler(AuthError)
def process_auth_error(error):
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response    