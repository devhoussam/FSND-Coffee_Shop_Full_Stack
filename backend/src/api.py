# ----------------------------------------------------------------------------#
# Imports 😇😇😇😇😇😇😇😇
# ----------------------------------------------------------------------------#

import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

#----------------------------------------------------------------------------#
# Application Getting Started 😇😇😇😇😇😇😇😇
#----------------------------------------------------------------------------#

app = Flask(__name__)
setup_db(app)
CORS(app)

# ----------------------------------------------------------------------------#
# @TODO IS DONE 100% 😇
# uncomment the following line to initialize the datbase
# !! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
# !! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
# ----------------------------------------------------------------------------#

db_drop_and_create_all()

#----------------------------------------------------------------------------#
# ROUTES 😇😇😇😇
#----------------------------------------------------------------------------#

# ----------------------------------------------------------------------------#
# @TODO IS DONE 100% 😇
# implement endpoint GET /drinks
# it should be a public endpoint
# it should contain only the drink.short() data representation
# returns status code 200 and json {"success": True, "drinks": drinks}
# where drinks is the list of drinks
# or appropriate status code indicating reason for failure
# ----------------------------------------------------------------------------#


@app.route('/drinks', methods=['GET'])
def take_all_drinks():
    try:
        available_drinks = Drink.query.all()
        drinks = [drink.short() for drink in available_drinks]

        if drinks is None:
            abort(404)

        return jsonify({
            'success': True,
            'drinks': available_drinks
        }), 200

    except Exception as error:
        print(error)  # Display and Show Errors in Shell GUI
        abort(404)


# ----------------------------------------------------------------------------#
# @TODO IS DONE 100% 😇
# implement endpoint GET /drinks-detail
# it should require the 'get:drinks-detail' permission
# it should contain the drink.long() data representation
# returns status code 200 and json {"success": True, "drinks": drinks}
# where drinks is the list of drinks
# or appropriate status code indicating reason for failure
# ----------------------------------------------------------------------------#

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(payload):
    try:
        drinks_dtl = Drink.query.order_by(Drink.id).all()
        drinks = [drink.long() for drink in drinks_dtl]

        if drinks is None:
            abort(404)

        return jsonify({
            'success': True,
            'drinks': drinks_dtl
        }), 200

    except Exception as error:
        print(error)  # Display and Show Errors in Shell GUI
        abort(404)

# ----------------------------------------------------------------------------#
# @TODO IS DONE 100% 😇
# implement endpoint POST /drinks
# it should create a new row in the drinks table
# it should require the 'post:drinks' permission
# it should contain the drink.long() data representation
# returns status code 200 and json {"success": True, "drinks": drink}
# where drink an array containing only the newly created drink
# or appropriate status code indicating reason for failure
# ----------------------------------------------------------------------------#


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drinks(payload):
    try:
        # Get body from request
        body = request.get_json()
        if body is None:
            abort(
                400, {
                    'message': 'request does not contain a valid JSON body.'})

        new_title = body.get('title')
        new_recipe = body.get('recipe')

        new_drink = Drink(title=new_title, recipe=json.dumps(new_recipe))
        new_drink = Drink.query.filter_by(id=new_drink.id).first()
        new_drink.insert()

        return jsonify({
            "success": True,
            "drinks": [new_drink.long()]
        }), 200

    except Exception as error:
        print(error)  # Display and Show Errors in Shell GUI
        abort(422)

# ----------------------------------------------------------------------------#
# @TODO IS DONE 100% 😇
# implement endpoint PATCH /drinks/<id>
# where <id> is the existing model id
# it should respond with a 404 error if <id> is not found
# it should update the corresponding row for <id>
# it should require the 'patch:drinks' permission
# it should contain the drink.long() data representation
# returns status code 200 and json {"success": True, "drinks": drink}
# where drink an array containing only the updated drink
# or appropriate status code indicating reason for failure
# ----------------------------------------------------------------------------#


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(payload, drink_id):
    try:
        # Get body from request
        body = request.get_json()
        update_title = body.get('title', None)
        update_recipe = body.get('recipe', None)

        if body is None:
            abort(
                400, {
                    'message': 'request does not contain a valid JSON body.'})

        updated_drinks = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if update_title:
            updated_drinks.title = update_title

        if update_recipe:
            updated_drinks.recipe = update_recipe

        updated_drinks.update()

        return jsonify({
            "success": True,
            "drinks": [updated_drinks.long()]
        }), 200

    except Exception as error:
        print(error)  # Display and Show Errors in Shell GUI
        abort(404)

# ----------------------------------------------------------------------------#
# @TODO IS DONE 100% 😇
# implement endpoint DELETE /drinks/<id>
# where <id> is the existing model id
# it should respond with a 404 error if <id> is not found
# it should delete the corresponding row for <id>
# it should require the 'delete:drinks' permission
# returns status code 200 and json {"success": True, "delete": id}
# where id is the id of the deleted record
# or appropriate status code indicating reason for failure
# ----------------------------------------------------------------------------#


@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drinks(payload, drink_id):
    try:

        if drink_id is None:
            abort(422, {'message': 'Oops! Please provide valid drink id'})

        delete_drink = Drink.query.filter(Drink.id == drink_id).one_or_none()

        if delete_drink is None:
            abort(
                404, {
                    'message': 'Drink with id {} not found in database.'.format(drink_id)})

        delete_drink.delete()

        return jsonify({
            "success": True,
            "delete": drink_id
        }), 200

    except Exception as error:
        print(error)  # Display and Show Errors in Shell GUI
        abort(404)


#----------------------------------------------------------------------------#
# Error Handling 😇😇😇😇
#----------------------------------------------------------------------------#

@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Oops! Bad Request"
    }), 400


@app.errorhandler(401)
def authentication_error(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": 'Oops! Unauthorized'
    }), 401


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "Oops! Resource Not Found"
    }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "Oops! unprocessable"
    }), 422

# ----------------------------------------------------------------------------#
# @TODO IS DONE 100% 😇
# implement error handler for AuthError
# error handler should conform to general task above
# ----------------------------------------------------------------------------#


@app.errorhandler(AuthError)
def handle_auth_error(ex):
    response = jsonify(ex.error)
    response.status_code = ex.status_code
    return response
