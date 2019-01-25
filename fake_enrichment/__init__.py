# -*- coding: utf-8 -*-

"""Top-level package for fake_enrichment."""

__author__ = """Chris Churas"""
__email__ = 'churas.camera@gmail.com'
__version__ = '0.0.1'

import random
import os
import uuid
import flask
from flask import Flask, jsonify, request
from flask_restplus import reqparse, abort, Api, Resource, fields, marshal


desc = """Fake enrichment service
 
 **NOTE:** This service is experimental. The interface is subject to change.
 
 See https://docs.google.com/document/d/1EsQL-qu-HPgUJlCfrWAJPTHRoQZjvfpC4h6wC9QD3Ac/edit# for details and to report issues.
""" # noqa


random.seed(os.urandom(16))
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



FAKE_CX = [{'numberVerification': [{'longNumber': 281474976710655}]}, {'metaData': [{'consistencyGroup': 1, 'elementCount': 1, 'lastUpdate': 1504297829644, 'name': 'ndexStatus', 'properties': [], 'version': '1.0'}, {'consistencyGroup': 1, 'elementCount': 1, 'lastUpdate': 1504297829657, 'name': 'provenanceHistory', 'properties': [], 'version': '1.0'}, {'consistencyGroup': 1, 'elementCount': 2, 'idCounter': 5, 'name': 'nodes'}, {'consistencyGroup': 1, 'elementCount': 1, 'idCounter': 5, 'name': 'edges'}, {'consistencyGroup': 1, 'elementCount': 1, 'idCounter': 5, 'name': 'supports'}, {'consistencyGroup': 1, 'elementCount': 1, 'idCounter': 5, 'name': 'citations'}, {'consistencyGroup': 1, 'elementCount': 9, 'idCounter': 5, 'name': 'edgeAttributes'}, {'consistencyGroup': 1, 'elementCount': 1, 'idCounter': 5, 'name': 'edgeSupports'}, {'consistencyGroup': 1, 'elementCount': 2, 'idCounter': 5, 'name': 'networkAttributes'}, {'consistencyGroup': 1, 'elementCount': 4, 'idCounter': 5, 'name': 'nodeAttributes'}]}, {'ndexStatus': [{'externalId': '653a65b2-8f54-11e7-a10d-0ac135e8bacf', 'creationTime': 1504297829644, 'modificationTime': 1504297829644, 'visibility': 'PRIVATE', 'published': False, 'nodeCount': 2, 'edgeCount': 1, 'owner': 'bgyori', 'ndexServerURI': 'http://public.ndexbio.org', 'readOnly': False}]}, {'provenanceHistory': [{'entity': {'uri': 'http://public.ndexbio.org/v2/network/653a65b2-8f54-11e7-a10d-0ac135e8bacf/summary', 'creationEvent': {'startedAtTime': 1504297829644, 'endedAtTime': 1504297829644, 'eventType': 'Program Upload in CX', 'inputs': None, 'properties': [{'name': 'user', 'value': 'Benjamin Gyori'}, {'name': 'user name', 'value': 'bgyori'}]}, 'properties': [{'name': 'edge count', 'value': '1'}, {'name': 'node count', 'value': '2'}, {'name': 'dc:title', 'value': 'indra_assembled'}]}}]}, {'nodes': [{'@id': 0, 'n': 'MEK'}, {'@id': 1, 'n': 'ERK'}]}, {'edges': [{'@id': 2, 's': 0, 't': 1, 'i': 'Phosphorylation'}]}, {'supports': [{'text': 'MEK phosphorylates ERK', 'citation': None, '@id': 4, 'attributes': []}]}, {'citations': [{'@id': 3, 'dc:title': None, 'dc:contributor': None, 'dc:identifier': 'pmid:19760502', 'dc:type': None, 'dc:description': None, 'attributes': []}]}, {'edgeAttributes': [{'po': 2, 'n': 'INDRA statement', 'v': 'Phosphorylation(MEK(), ERK())'}, {'po': 2, 'n': 'INDRA json', 'v': '{"type": "Phosphorylation", "enz": {"name": "MEK", "db_refs": {"BE": "MEK", "TEXT": "MEK"}, "sbo_definition": "http://identifiers.org/sbo/SBO:0000460"}, "sub": {"name": "ERK", "db_refs": {"BE": "ERK", "TEXT": "ERK"}, "sbo_definition": "http://identifiers.org/sbo/SBO:0000015"}, "evidence": [{"source_api": "reach", "pmid": "19760502", "text": "MEK phosphorylates ERK", "annotations": {"found_by": "Phosphorylation_syntax_1a_verb"}, "epistemics": {"section_type": null, "direct": true}}], "id": "364e57c7-9768-43ea-8ce8-cfd65212aff0", "sbo_definition": "http://identifiers.org/sbo/SBO:0000216"}'}, {'po': 2, 'n': 'type', 'v': 'Modification'}, {'po': 2, 'n': 'polarity', 'v': 'positive'}, {'po': 2, 'n': 'ndex:citation', 'v': ['pmid:19760502'], 'd': 'list_of_string'}, {'po': 2, 'n': 'Belief score', 'v': '1.00'}, {'po': 2, 'n': 'Text', 'v': 'MEK phosphorylates ERK'}, {'po': 2, 'n': 'indra', 'v': ''}, {'po': 2, 'n': 'supportType', 'v': 'literature'}]}, {'edgeSupports': [{'po': [2], 'supports': [4]}]}, {'networkAttributes': [{'n': 'name', 'v': 'indra_assembled'}, {'n': 'description', 'v': ''}]}, {'nodeAttributes': [{'po': 0, 'n': 'type', 'v': 'proteinfamily'}, {'po': 0, 'n': 'BE', 'v': 'http://sorger.med.harvard.edu/indra/entities/MEK'}, {'po': 1, 'n': 'type', 'v': 'proteinfamily'}, {'po': 1, 'n': 'BE', 'v': 'http://sorger.med.harvard.edu/indra/entities/ERK'}]}, {'status': [{'error': '', 'success': True}]}]

@api.doc('Runs enrichment query')
@ns.route('/', strict_slashes=False)
class RunEnrichmentQuery(Resource):
    """
    Submits enrichment query
    """

    resource_fields = api.model('EnrichmentQuery', {
        'genelist': fields.List(fields.String, description='List of genes',
                                example=['brca1'], required=True),
        'databaselist': fields.List(fields.String,
                                    description='List of databases',
                                    example=['signor', 'pid'], default=['signor'])
    })

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
            if random.choice['success', 'fail'] is 'fail':
                raise Exception('something failed')

            res = str(uuid.uuid4())

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


class BaseStatus(object):
    """
    Represents server status, which upon creation will randomly flip around in states
    """
    status = 'submitted'
    message = ''
    progress = 50
    walltime = 1000

    def __init__(self, id):
        """Constructor
        """
        if id is not None:
            self.message = 'id => ' + id + ' '

        self.status = random.choice(['submitted', 'processing', 'complete', 'failed'])
        if self.status is 'complete' or self.status is 'failed':
            self.progress = 100
            self.walltime = random.randint(0, 100000)
            self.message = self.message + random.choice(['okay', 'some warning', 'have a nice day'])
            return

        if self.status is 'submitted':
            self.progress = 0
            self.walltime = 0
            return

        if self.status is 'processing':
            self.progress = random.randint(0, 99)
            self.walltime = 0
            self.message = self.message + random.choice(['hi', 'how', ''])
            return


@ns.route('/<string:id>/status', strict_slashes=False)
class GetTaskStatus(Resource):
    """Class doc here"""

    task_status_resp = api.model('EnrichmentQueryStatus', BASE_STATUS)

    @api.response(200, 'Success', task_status_resp)
    @api.response(410, 'Task not found')
    @api.response(500, 'Internal server error')
    def get(self, id):
        """
        Gets status of enrichment query
        """
        bs = BaseStatus(id)
        s_code = 200
        if bs.status is 'failed':
            s_code = 500

        return marshal(bs, GetTaskStatus.task_status_resp), s_code


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


class SingleResult(object):
    """
    Single result
    """
    networkuuid = ''
    databaseuuid = ''
    databasename = ''
    pvalue = 0
    hitgenes = ['']

    def __init__(self):
        """
        Constructor
        """
        self.networkuuid = str(uuid.uuid4())
        self.databaseuuid = str(uuid.uuid4())
        self.databasename = random.choice(['signor', 'pid', 'wikipathways'])
        self.pvalue = random.random()
        self.hitgenes = ['hi']


class FullResult(BaseStatus):
    """
    Full result
    """

    results = []
    number_of_hits = 0
    start = 0
    size = 0

    def __init__(self, id, start, size):
        BaseStatus.__init__(self, id)

        self.start = start
        self.size = size
        if self.status is 'failed' or self.status is 'processing' or self.status is 'submitted':
            return

        # processing is completed so lets randomly generate results
        self.number_of_hits = random.randint(0, 100)
        if self.number_of_hits is 0:
            return

        for x in range(self.number_of_hits - 1):
            self.results.append(SingleResult())


@ns.route('/<string:id>', strict_slashes=False)
class GetEnrichmentQueryResult(Resource):
    """More class doc here"""

    fulltask_status_resp = api.model('EnrichmentQueryResults', FULL_STATUS)

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
        params = GetEnrichmentQueryResult.get_params.parse_args(request, strict=True)
        fs = FullResult(id, params['start'], params['size'])
        s_code = 200
        if fs.status is 'failed':
            s_code = 500

        return marshal(fs, GetEnrichmentQueryResult.fulltask_status_resp), s_code

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
        resp.status_code = random.choice[200, 400, 500]
        return resp


@ns.route('/<string:id>/overlaynetwork', strict_slashes=False)
class GetEnrichmentResultAsCX(Resource):
    """Gets result of query overlayed on network as CX
    """



    get_params = reqparse.RequestParser()
    get_params.add_argument('databaseid', type=str, location='args',
                            help='UUID of database', required=True)
    get_params.add_argument('networkid', type=str, location='args',
                            help='UUID of network ', required=True)

    @api.response(200, 'Successful response from server and response will be CX')
    @api.response(410, 'Task not found')
    @api.response(500, 'Internal server error')
    @api.expect(get_params)
    def get(self, id):
        """
        Gets result of enrichment from a specific database and network as CX

        NOTE: For incomplete/failed jobs only Status, message, progress, and walltime will
        be returned in JSON
        """
        s_code = random.choice([200, 410, 500])

        if s_code is not 200:
            resp = flask.make_response()
            resp.status_code = s_code
            return resp

        resp = jsonify(FAKE_CX)
        resp.status_code = 200
        return resp


@ns.route('/database', strict_slashes=False)
class GetEnrichmentDatabases(Resource):

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

        resp = jsonify({'error': 'error'})
        resp.status_code = 200
        return resp
