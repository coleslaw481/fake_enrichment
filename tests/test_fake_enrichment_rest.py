#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `fake_enrichment` package."""


import os
import json
import unittest
import shutil
import tempfile
import re
import io
import uuid

from werkzeug.datastructures import FileStorage

import fake_enrichment


class TestNbgwas_rest(unittest.TestCase):
    """Tests for `fake_enrichment` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self._temp_dir = tempfile.mkdtemp()
        fake_enrichment.app.testing = True
        fake_enrichment.app.config[fake_enrichment.JOB_PATH_KEY] = self._temp_dir
        fake_enrichment.app.config[fake_enrichment.WAIT_COUNT_KEY] = 1
        fake_enrichment.app.config[fake_enrichment.SLEEP_TIME_KEY] = 0
        self._app = fake_enrichment.app.test_client()

    def tearDown(self):
        """Tear down test fixtures, if any."""
        shutil.rmtree(self._temp_dir)

    def test_baseurl(self):
        """Test something."""
        rv = self._app.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertTrue('Network Assisted' in str(rv.data))

    def test_get_submit_dir(self):
        spath = os.path.join(self._temp_dir, fake_enrichment.SUBMITTED_STATUS)
        self.assertEqual(fake_enrichment.get_submit_dir(), spath)

    def test_get_processing_dir(self):
        spath = os.path.join(self._temp_dir, fake_enrichment.PROCESSING_STATUS)
        self.assertEqual(fake_enrichment.get_processing_dir(), spath)

    def test_get_done_dir(self):
        spath = os.path.join(self._temp_dir, fake_enrichment.DONE_STATUS)
        self.assertEqual(fake_enrichment.get_done_dir(), spath)

    def test_create_task_snp_level_summary_param_not_set(self):

        try:
            # try with empty parameters
            fake_enrichment.create_task({'remoteip': '1.2.3.4'})
            self.fail('Expected exception')
        except Exception as e:
            self.assertEqual(str(e),
                             fake_enrichment.SNP_LEVEL_SUMMARY_PARAM +
                             ' is required')

    def test_create_task_ndex_param_not_set(self):

        try:
            # try with empty parameters
            pdict = {}
            pdict['remoteip'] = '1.2.3.4'
            pdict[fake_enrichment.ALPHA_PARAM] = 0.5
            pdict['protein_coding'] = 'hg19'
            snpfile = FileStorage(stream=io.BytesIO(b'hi there'),
                                  filename='yo.txt')
            pdict[fake_enrichment.SNP_LEVEL_SUMMARY_PARAM] = snpfile
            fake_enrichment.create_task(pdict)
            self.fail('Expected exception')
        except Exception as e:
            self.assertEqual(str(e),
                             fake_enrichment.NDEX_PARAM +
                             ' is required')

    def test_create_task_success(self):
        pdict = {}
        pdict['remoteip'] = '1.2.3.4'
        pdict[fake_enrichment.ALPHA_PARAM] = 0.5
        pdict['protein_coding'] = 'hg19'
        pdict[fake_enrichment.NDEX_PARAM] = 'c3946381-745a-4f15-810c-4c880079034f'
        snpfile = FileStorage(stream=io.BytesIO(b'hi there'),
                              filename='yo.txt')
        pdict[fake_enrichment.SNP_LEVEL_SUMMARY_PARAM] = snpfile
        res = fake_enrichment.create_task(pdict)
        self.assertTrue(res is not None)

        snp_path = os.path.join(fake_enrichment.get_submit_dir(),
                                pdict['remoteip'], res,
                                fake_enrichment.SNP_LEVEL_SUMMARY_PARAM)
        self.assertTrue(os.path.isfile(snp_path))

    def test_get_task_basedir_none(self):
        self.assertEqual(fake_enrichment.get_task('foo'), None)

    def test_get_task_basedir_not_a_directory(self):
        somefile = os.path.join(self._temp_dir, 'hi')
        open(somefile, 'a').close()
        self.assertEqual(fake_enrichment.get_task('foo', basedir=somefile), None)

    def test_get_task_for_none_uuid(self):
        self.assertEqual(fake_enrichment.get_task(None,
                                                  basedir=self._temp_dir), None)

    def test_get_task_for_nonexistantuuid(self):
        self.assertEqual(fake_enrichment.get_task(str(uuid.uuid4()),
                                                  basedir=self._temp_dir), None)

    def test_get_task_for_validuuid(self):
        somefile = os.path.join(self._temp_dir, '1')
        open(somefile, 'a').close()
        theuuid_dir = os.path.join(self._temp_dir, '1.2.3.4', '1234')
        os.makedirs(theuuid_dir, mode=0o755)

        someipfile = os.path.join(self._temp_dir, '1.2.3.4', '1')
        open(someipfile, 'a').close()
        self.assertEqual(fake_enrichment.get_task('1234',
                                                  basedir=self._temp_dir),
                         theuuid_dir)

    def test_wait_for_task_uuid_none(self):
        self.assertEqual(fake_enrichment.wait_for_task(None), None)

    def test_wait_for_task_uuid_not_found(self):
        self.assertEqual(fake_enrichment.wait_for_task('foo'), None)

    def test_wait_for_task_uuid_found(self):
        taskdir = os.path.join(self._temp_dir, 'done', '1.2.3.4', 'haha')
        os.makedirs(taskdir, mode=0o755)
        self.assertEqual(fake_enrichment.wait_for_task('haha'), taskdir)

    def test_delete(self):
        rv = self._app.delete(fake_enrichment.SNP_ANALYZER_NS + '/yoyo')
        self.assertEqual(rv.status_code, 200)
        delete_file = os.path.join(self._temp_dir, fake_enrichment.DELETE_REQUESTS,
                                   'yoyo')
        self.assertTrue(os.path.isfile(delete_file))

        # try with not set path
        rv = self._app.delete(fake_enrichment.SNP_ANALYZER_NS + '/')
        self.assertEqual(rv.status_code, 405)

        # try with path greater then 40 characters
        rv = self._app.delete(fake_enrichment.SNP_ANALYZER_NS + '/' + 'a' * 41)
        self.assertEqual(rv.status_code, 400)

        # try where we get os error
        xdir = os.path.join(self._temp_dir, fake_enrichment.DELETE_REQUESTS,
                            'hehe')
        os.makedirs(xdir, mode=0o755)
        rv = self._app.delete(fake_enrichment.SNP_ANALYZER_NS + '/hehe')
        self.assertEqual(rv.status_code, 500)

    def test_post_missing_required_parameter(self):
        pdict = {}
        pdict[fake_enrichment.ALPHA_PARAM] = 0.4,
        rv = self._app.post(fake_enrichment.SNP_ANALYZER_NS, data=pdict,
                            follow_redirects=True)
        self.assertEqual(rv.status_code, 500)

    def test_post_ndex_id_too_long(self):
        pdict = {}
        pdict[fake_enrichment.ALPHA_PARAM] = 0.4
        pdict[fake_enrichment.SNP_LEVEL_SUMMARY_PARAM] = (io.BytesIO(b'hi there'),
                                                      'yo.txt')
        pdict['protein_coding'] = 'hg19'
        pdict[fake_enrichment.NDEX_PARAM] = ('asdflkasdfkljasdfalskdfja;klsd' +
                                         'lskdjfas;ldjkfasd;flasdfdfsdfs' +
                                         'sdfasdfasdfasdfasdfasdf  asdfs' +
                                         'asdfasdfasdfasdfasdfasdfasdfas' +
                                         'asdfasdfasdfasdfasdfasdfasdfas')
        rv = self._app.post(fake_enrichment.SNP_ANALYZER_NS, data=pdict,
                            follow_redirects=True)
        self.assertEqual(rv.status_code, 500)
        self.assertEqual(rv.json['message'],
                         'Unable to create task ndex parameter value is too'
                         ' long to be an NDex UUID')

    def test_post_ndex(self):
        pdict = {}
        pdict[fake_enrichment.ALPHA_PARAM] = 0.5
        pdict[fake_enrichment.NDEX_PARAM] = 'someid'
        pdict['protein_coding'] = 'hg19'
        pdict[fake_enrichment.SNP_LEVEL_SUMMARY_PARAM] = (io.BytesIO(b'hi there'),
                                                      'yo.txt')
        pdict[fake_enrichment.SNP_LEVEL_SUMMARY_COL_LABEL_PARAM] = 'hi,how,are'
        rv = self._app.post(fake_enrichment.SNP_ANALYZER_NS, data=pdict,
                            follow_redirects=True)
        self.assertEqual(rv.status_code, 202)
        res = rv.headers['Location']
        self.assertTrue(res is not None)
        self.assertTrue(fake_enrichment.SNP_ANALYZER_NS in res)

        uuidstr = re.sub('^.*/', '', res)
        fake_enrichment.app.config[fake_enrichment.JOB_PATH_KEY] = self._temp_dir

        tpath = fake_enrichment.get_task(uuidstr,
                                         basedir=fake_enrichment.get_submit_dir())
        self.assertTrue(os.path.isdir(tpath))
        jsonfile = os.path.join(tpath, fake_enrichment.TASK_JSON)
        self.assertTrue(os.path.isfile(jsonfile))
        with open(jsonfile, 'r') as f:
            jdata = json.load(f)

        self.assertEqual(jdata[fake_enrichment.ALPHA_PARAM], 0.5)
        self.assertEqual(jdata[fake_enrichment.NDEX_PARAM], 'someid')
        self.assertEqual(jdata[fake_enrichment.SNP_LEVEL_SUMMARY_COL_LABEL_PARAM],
                         'hi,how,are')

    def test_get_id_none(self):
        rv = self._app.get(fake_enrichment.SNP_ANALYZER_NS)
        self.assertEqual(rv.status_code, 405)

    def test_get_id_not_found(self):
        done_dir = os.path.join(self._temp_dir,
                                fake_enrichment.DONE_STATUS)
        os.makedirs(done_dir, mode=0o755)
        rv = self._app.get(fake_enrichment.SNP_ANALYZER_NS + '/1234')
        data = json.loads(rv.data)
        self.assertEqual(data[fake_enrichment.STATUS_RESULT_KEY],
                         fake_enrichment.NOTFOUND_STATUS)
        self.assertEqual(data[fake_enrichment.PARAMETERS_KEY], None)
        self.assertEqual(rv.status_code, 410)

    def test_get_id_found_in_submitted_status(self):
        task_dir = os.path.join(self._temp_dir,
                                fake_enrichment.SUBMITTED_STATUS,
                                '45.67.54.33', 'qazxsw')
        os.makedirs(task_dir, mode=0o755)
        rv = self._app.get(fake_enrichment.SNP_ANALYZER_NS + '/qazxsw')
        data = json.loads(rv.data)
        self.assertEqual(data[fake_enrichment.PARAMETERS_KEY], None)
        self.assertEqual(data[fake_enrichment.STATUS_RESULT_KEY],
                         fake_enrichment.SUBMITTED_STATUS)
        self.assertEqual(rv.status_code, 200)

    def test_get_id_found_in_processing_status(self):
        task_dir = os.path.join(self._temp_dir,
                                fake_enrichment.PROCESSING_STATUS,
                                '45.67.54.33', 'qazxsw')
        os.makedirs(task_dir, mode=0o755)
        rv = self._app.get(fake_enrichment.SNP_ANALYZER_NS + '/qazxsw')
        data = json.loads(rv.data)
        self.assertEqual(data[fake_enrichment.PARAMETERS_KEY], None)
        self.assertEqual(data[fake_enrichment.STATUS_RESULT_KEY],
                         fake_enrichment.PROCESSING_STATUS)
        self.assertEqual(rv.status_code, 200)

    def test_get_id_found_in_done_status_no_result_file(self):
        task_dir = os.path.join(self._temp_dir,
                                fake_enrichment.DONE_STATUS,
                                '45.67.54.33', 'qazxsw')
        os.makedirs(task_dir, mode=0o755)
        rv = self._app.get(fake_enrichment.SNP_ANALYZER_NS + '/qazxsw')
        data = json.loads(rv.data)
        self.assertEqual(data[fake_enrichment.PARAMETERS_KEY], None)
        self.assertEqual(data[fake_enrichment.STATUS_RESULT_KEY],
                         fake_enrichment.ERROR_STATUS)
        self.assertEqual(rv.status_code, 500)

    def test_get_id_found_in_done_status_with_result_file_no_task_file(self):
        task_dir = os.path.join(self._temp_dir,
                                fake_enrichment.DONE_STATUS,
                                '45.67.54.33', 'qazxsw')
        os.makedirs(task_dir, mode=0o755)
        resfile = os.path.join(task_dir, fake_enrichment.RESULT)
        with open(resfile, 'w') as f:
            f.write('{ "hello": "there"}')
            f.flush()

        rv = self._app.get(fake_enrichment.SNP_ANALYZER_NS + '/qazxsw')
        data = json.loads(rv.data)
        self.assertEqual(data[fake_enrichment.STATUS_RESULT_KEY],
                         fake_enrichment.DONE_STATUS)
        self.assertEqual(data[fake_enrichment.PARAMETERS_KEY], None)
        self.assertEqual(data[fake_enrichment.RESULT_KEY]['hello'], 'there')
        self.assertEqual(rv.status_code, 200)

    def test_get_id_found_in_done_status_with_result_file_with_task_file(self):
        task_dir = os.path.join(self._temp_dir,
                                fake_enrichment.DONE_STATUS,
                                '45.67.54.33', 'qazxsw')
        os.makedirs(task_dir, mode=0o755)
        resfile = os.path.join(task_dir, fake_enrichment.RESULT)
        with open(resfile, 'w') as f:
            f.write('{ "hello": "there"}')
            f.flush()
        tfile = os.path.join(task_dir, fake_enrichment.TASK_JSON)
        with open(tfile, 'w') as f:
            f.write('{"task": "yo",')
            f.write(' "remoteip": "45.67.54.33"}')
            f.flush()

        rv = self._app.get(fake_enrichment.SNP_ANALYZER_NS + '/qazxsw')
        data = json.loads(rv.data)
        self.assertEqual(data[fake_enrichment.PARAMETERS_KEY]['task'], 'yo')
        self.assertTrue(fake_enrichment.REMOTEIP_PARAM not in data[fake_enrichment.PARAMETERS_KEY])
        self.assertEqual(data[fake_enrichment.STATUS_RESULT_KEY],
                         fake_enrichment.DONE_STATUS)

        self.assertEqual(data[fake_enrichment.RESULT_KEY]['hello'], 'there')
        self.assertEqual(rv.status_code, 200)

    def test_log_task_json_file_with_none(self):
        self.assertEqual(fake_enrichment.log_task_json_file(None), None)

    def test_get_status(self):
        rv = self._app.get(fake_enrichment.SNP_ANALYZER_NS + '/status')
        data = json.loads(rv.data)
        self.assertEqual(data[fake_enrichment.STATUS_RESULT_KEY],
                         fake_enrichment.SystemStatus.OK_STATUS)
        self.assertEqual(data[fake_enrichment.REST_VERSION_KEY],
                         fake_enrichment.__version__)
        self.assertTrue(data[fake_enrichment.DISKFULL_KEY] is not None)
        self.assertEqual(rv.status_code, 200)
