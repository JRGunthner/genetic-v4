from __future__ import print_function

import json
import sys
import threading
import traceback
from functools import wraps

import flask
import pika
from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

from budget_calculator.main import budget_calc
from hpl.engine.interpreter import hpl_interpreter
from encoder import encoder
from pcp_scheduler.src.exceptions import Exceptions
from pcp_scheduler.src.scheduler.scheduler_ag import generate_allocation
from services.calc_input_consumer import CalcInputConsumer
from simulator.hold_simulator import HoldSimulator
from simulator.serializer import Serializer
from utils.token import is_user_token_valid
from utils import environment

application = Flask("Services")
application.config['JWT_ALGORITHM'] = environment.VARIABLES["JWT_ALGORITHM"]
application.config['JWT_AUDIENCE'] = environment.VARIABLES["JWT_AUDIENCE"]
application.config['JWT_SECRET'] = environment.VARIABLES["JWT_SECRET"]
application.config['WHITELIST_HOST_ADDRESS'] = environment.VARIABLES["WHITELIST_HOST_ADDRESS"]
application.config['WHITELIST_HOST_PORT'] = environment.VARIABLES["WHITELIST_HOST_PORT"]
application.config['WHITELIST_PASSWORD'] = environment.VARIABLES["WHITELIST_PASSWORD"]
application.config['CORS_HEADERS'] = 'Content-Type'

cors = CORS(application, resources={r"/printsimul": {"origins": "*"}, r"/allocate": {"origins": "*"}})
amqp_url = environment.VARIABLES['AMQP_URL']
virtual_host = environment.VARIABLES['VIRTUAL_HOST']
virtual_passwd = environment.VARIABLES['VIRTUAL_PASSWD']
credentials = pika.PlainCredentials(virtual_host, virtual_passwd)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        if not is_user_token_valid(str(token).split(" ")[1]):
            return jsonify({'message': 'Token is invalid'}), 403

        return f(*args, **kwargs)

    return decorated


@application.route("/printsimul", methods=["POST"])
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
@token_required
def print_simulator():
    data = json.loads(request.data.decode('utf-8'))
    simulator = HoldSimulator(data["items"], data["machines"],
                                   data["constraints"], data["genetic_configurations"])
    returned = simulator.simulate()
    print(returned[0], file=sys.stderr)
    response = flask.jsonify(Serializer(returned[0],
                                        data["constraints"]["reuse_bins"],
                                        data["machines"][0]["margins"]).get_returned_obj())
    print(response, file=sys.stderr)
    return response


@application.route("/allocate", methods=["POST"])
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
@token_required
def allocate_planjobs():
    try:
        data = encoder.deserializer(request.data.decode('utf-8'))
    except Exception as e:
        response = {"reason": e.__class__.__name__, "informations": {"traceback": traceback.format_exc()}}
        return encoder.serializer(response), 400

    grid = data['grid']
    planjobs = data['planjobs']
    configs = data['configs']
    non_working_days = data.get("non_working_days", [])

    try:
        response = generate_allocation(grid, planjobs, configs, non_working_days)
        status_code = 200
    except Exceptions.InsufficientResourcesException as e1:
        response = {"reason": "InsufficientResourcesException", 'informations': e1.value}
        status_code = 400
    except Exceptions.InsufficientResourceCalendarException as e2:
        response = {"reason": "InsufficientResourceCalendarException", 'informations': e2.value}
        status_code = 400
    except Exceptions.LoadBalancerViolationException as e3:
        response = {"reason": "LoadBalancerViolationException", 'informations': e3.value}
        status_code = 400
    except Exception as e3:
        trace_ = {"traceback": traceback.format_exc()}
        reason = e3.__class__.__name__
        response = {"reason": reason, "informations": trace_}
        status_code = 500

    return encoder.serializer(response), status_code


@application.route("/hpl/calc", methods=["POST"])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
@token_required
def calc_hpl():
    data = json.loads(request.data.decode('utf-8'))
    response = hpl_interpreter(data)
    status_code = 200 if "error_code" not in response else 500
    return json.dumps(response), status_code


@application.route("/budget-calculator", methods=["POST"])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
@token_required
def budget_calculation():
    try:
        data = encoder.deserializer(request.data.decode('utf-8'))
    except Exception as e:
        response = {"reason": e.__class__.__name__, "informations": {"traceback": traceback.format_exc()}}
        return encoder.serializer(response), 400

    response = budget_calc(data)
    return encoder.serializer(response)


@application.route('/shutdown', methods=['POST'])
@token_required
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


@application.route('/validate-variables', methods=['POST'])
def validate_variables():
    response = {}
    try:
        data = encoder.deserializer(request.data.decode('utf-8'))
        data.validate_variables()
        response = data
    except Exception as e:
        response = {"reason": e.__class__.__name__, "informations": {"traceback": traceback.format_exc()}}
        return encoder.serializer(response), 400
    return encoder.serializer(response)


def shutdown_server():
    calc_consumer.stop()
    func = request.environ.get(environment.VARIABLES['SERVER_SHUTDOWN'])
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()


calc_consumer = CalcInputConsumer(amqp_url, virtual_host, credentials)
threading.Thread(target=calc_consumer.run).start()
