# -*- coding: utf-8 -*-

"""Top-level package for fake_enrichment."""

__author__ = """Chris Churas"""
__email__ = 'churas.camera@gmail.com'
__version__ = '0.0.1'

import uuid
import flask
from flask import Flask, jsonify
from flask_restplus import reqparse, abort, Api, Resource, fields


desc = """Fake enrichment service
 
 **NOTE:** This service is experimental. The interface is subject to change.
 
 See https://docs.google.com/document/d/1EsQL-qu-HPgUJlCfrWAJPTHRoQZjvfpC4h6wC9QD3Ac/edit# for details and to report issues.
""" # noqa

ENRICH_REST_SETTINGS_ENV = 'ENRICH_REST_SETTINGS'
# global api object
app = Flask(__name__)

JOB_PATH_KEY = 'JOB_PATH'
WAIT_COUNT_KEY = 'WAIT_COUNT'
SLEEP_TIME_KEY = 'SLEEP_TIME'

app.config[JOB_PATH_KEY] = '/tmp'
app.config[WAIT_COUNT_KEY] = 60
app.config[SLEEP_TIME_KEY] = 10

app.config.from_envvar(ENRICH_REST_SETTINGS_ENV, silent=True)

LOCATION = 'Location'



ENRICH_NS = 'enrichment'


api = Api(app, version=str(__version__),
          title='Fake Enrichment ',
          description=desc, example='put example here')

# need to clear out the default namespace
api.namespaces.clear()

ns = api.namespace(ENRICH_NS,
                   description='Fake Enrichment Service')

app.config.SWAGGER_UI_DOC_EXPANSION = 'list'

uuid_counter = 1


def get_uuid():
    """
    Generates UUID and returns as string. With one caveat,
    if app.config[USE_SEQUENTIAL_UUID] is set and True
    then uuid_counter is returned and incremented
    :return: uuid as string
    """
    return str(uuid.uuid4())


resource_fields = api.model('EnrichmentQuery', {
    'genelist': fields.List(fields.String, description='List of genes',
                            example=['brca1'], required=True),
    'databaselist': fields.List(fields.String,
                                description='List of databases',
                                example=['signor', 'pid'], default=['signor'])
})


@api.doc('Runs enrichment query')
@ns.route('/', strict_slashes=False)
class TaskBasedRestApp(Resource):
    @api.doc('Runs enrichment query',
             responses={
                 202: 'The task was successfully submitted to the service. '
                      'Visit the URL'
                      ' specified in **Location** field in HEADERS to '
                      'status and results',
                 500: 'Internal server error'
             })
    @api.header(LOCATION, 'URL endpoint to poll for result of task for '
                          'successful call')
    @api.expect(resource_fields)
    def post(self):
        """
        Submits enrichment query

        """
        app.logger.debug("Post received")

        try:

            res = 'uhhhhdosomethingheretogetid'

            resp = flask.make_response()
            resp.headers[LOCATION] = ENRICH_NS + '/' + res
            resp.status_code = 202
            return resp
        except OSError as e:
            app.logger.exception('Error creating task due to OSError' + str(e))
            abort(500, 'Unable to create task ' + str(e))
        except Exception as ea:
            app.logger.exception('Error creating task due to Exception ' +
                                 str(ea))
            abort(500, 'Unable to create task ' + str(ea))


BASE_STATUS = {'status': fields.String(description='One of the following <submitted | processing | complete | failed>',
                                       example='complete'),
               'message': fields.String(description='Any message about query, such as an error message'),
               'progress': fields.Integer(description='% completion, will be a value in range of 0-100',
                                          example=100),
               'walltime': fields.Integer(description='Time in milliseconds query took to run',
                                          example=341)}

task_status_resp = api.model('EnrichmentQueryStatus', BASE_STATUS)


@ns.route('/<string:id>/status', strict_slashes=False)
class GetTaskStatus(Resource):
    """Class doc here"""
    @api.response(200, 'Success', task_status_resp)
    @api.response(410, 'Task not found')
    @api.response(500, 'Internal server error')
    def get(self, id):
        """
        Gets status of enrichment query
        """
        resp = jsonify({'error': 'error'})

        resp.status_code = 500
        return resp


FULL_STATUS = BASE_STATUS
FULL_STATUS['number_of_hits'] = fields.Integer(description='number of hits being # of networks total')
FULL_STATUS['start'] = fields.Integer(description='Value of start parameter passed in')
FULL_STATUS['size'] = fields.Integer(description='Value of size passed in')

result = api.model('EnrichmentQueryResult', {
    'networkuuid': fields.String(description='uuid of network'),
    'databaseuuid': fields.String(description='uuid of database'),
    'databasename': fields.String(description='name of database'),
    'pvalue': fields.Float(description='pvalue of enrichment'),
    'hitgenes': fields.List(fields.String(description='Gene that hit'))
})
FULL_STATUS['results'] = fields.List(fields.Nested(result))

fulltask_status_resp = api.model('EnrichmentQueryResults', FULL_STATUS)


@ns.route('/<string:id>', strict_slashes=False)
class GetTask(Resource):
    """More class doc here"""

    get_params = reqparse.RequestParser()
    get_params.add_argument('start', type=int, location='args',
                            help='Starting index of result, should be an integer 0 or larger',
                            default=0)
    get_params.add_argument('size', type=int, location='args',
                            help='Number of results to return, 0 for all', default=0)

    @api.response(200, 'Successful response from server', fulltask_status_resp)
    @api.response(410, 'Task not found')
    @api.response(500, 'Internal server error')
    @api.expect(get_params)
    def get(self, id):
        """
        Gets result of enrichment

        NOTE: For incomplete/failed jobs only Status, message, progress, and walltime will
        be returned in JSON
        """
        resp = jsonify({'error': 'error'})

        resp.status_code = 500
        return resp

    @api.doc('Creates request to delete query',
             responses={
                 200: 'Delete request successfully received',
                 400: 'Invalid delete request',
                 500: 'Internal server error'
             })
    def delete(self, id):
        """
        Deletes task associated with {id} passed in
        """
        resp = flask.make_response()
        try:
            raise NotImplementedError('Not implemented this')
        except Exception:
            app.logger.exception('Caught exception creating delete token')
        resp.status_code = 500
        return resp


@ns.route('/<string:id>/overlaynetwork', strict_slashes=False)
class GetTask(Resource):
    """More class doc here"""

    get_params = reqparse.RequestParser()
    get_params.add_argument('databaseid', type=str, location='args',
                            help='UUID of database', required=True)
    get_params.add_argument('networkid', type=int, location='args',
                            help='UUID of network ', required=True)

    @api.response(200, 'Successful response from server', fulltask_status_resp)
    @api.response(410, 'Task not found')
    @api.response(500, 'Internal server error')
    @api.expect(get_params)
    def get(self, id):
        """
        Gets result of enrichment

        NOTE: For incomplete/failed jobs only Status, message, progress, and walltime will
        be returned in JSON
        """
        resp = jsonify({'error': 'error'})

        resp.status_code = 500
        return resp


@ns.route('/database', strict_slashes=False)
class GetTask(Resource):

    @api.doc('Gets ',
             responses={
                 200: 'Success',
                 410: 'Task not found',
                 500: 'Internal server error'
             })
    def get(self):
        """
        Gets list of databases that can be queried for enrichment

        &nbsp;&nbsp;

        ```Bash
        {[
            {
                “uuid”: <uuid of network>,
                “description”: <description of database>,
                “name”: <name of networkset or database>,
                “number_of_networks”: <number of networks>,
             },
        ]}
        ```
        """
        resp = jsonify({'error': 'error'})

        resp.status_code = 500
        return resp


@ns.route('/status', strict_slashes=False)
class SystemStatus(Resource):

    OK_STATUS = 'ok'

    @api.doc('Gets status',
             responses={
                 200: 'Success',
                 500: 'Internal server error'
             })
    def get(self):
        """
        Gets status of service

        ```Bash
        {
          "status" : "ok|error",
          "rest_version": "1.0",
          "percent_disk_full": "45"
        }
        ```
        """
        try:
            pc_disk_full = 50
        except Exception:
            app.logger.exception('Caught exception checking disk space')
            pc_disk_full = -1

        resp = jsonify({'error': 'error',})
        resp.status_code = 200
        return resp
