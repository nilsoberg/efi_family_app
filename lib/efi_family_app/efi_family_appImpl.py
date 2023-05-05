# -*- coding: utf-8 -*-
#BEGIN_HEADER
import logging
import os

from installed_clients.KBaseReportClient import KBaseReport
from installed_clients.ReadsUtilsClient import ReadsUtils
from base import Core

from .est_util import EstJob


#END_HEADER


class efi_family_app:
    '''
    Module Name:
    efi_family_app

    Module Description:
    A KBase module: efi_family_app
    '''

    ######## WARNING FOR GEVENT USERS ####### noqa
    # Since asynchronous IO can lead to methods - even the same method -
    # interrupting each other, you must be *very* careful when using global
    # state. A method could easily clobber the state set by another while
    # the latter method is running.
    ######################################### noqa
    VERSION = "0.0.1"
    GIT_URL = ""
    GIT_COMMIT_HASH = ""

    #BEGIN_CLASS_HEADER
    #END_CLASS_HEADER

    # config contains contents of config file in a hash or None if it couldn't
    # be found
    def __init__(self, config):
        #BEGIN_CONSTRUCTOR
        self.callback_url = os.environ['SDK_CALLBACK_URL']
        self.shared_folder = config['scratch']
        logging.basicConfig(format='%(created)s %(levelname)s: %(message)s',
                            level=logging.INFO)
        #END_CONSTRUCTOR
        pass

    def run_efi_family_app(self, ctx, params):
        """
        This example function accepts any number of parameters and returns results in a KBaseReport
        :param params: instance of mapping from String to unspecified object
        :returns: instance of type "ReportResults" -> structure: parameter
           "report_name" of String, parameter "report_ref" of String
        """
        # ctx is the context object
        # return variables are: output
        #BEGIN run_efi_family_app

        config = dict(
            callback_url=self.callback_url,
            shared_folder=self.shared_folder,
            clients=dict(
                KBaseReport=KBaseReport,
            ),
        )

        #TODO: make this a config variable
        config['est_home'] = '/apps/EST'
        #create_args = {'family': params['family_name']}

        db_conf = params.get('efi_db_config')
        if db_conf != None:
            config['efi_db_config'] = db_conf

        # return the results

        job = EstJob(ctx, config)

        job.create_job(params)

        job.start_job()

        output = job.generate_report(params)

        #era = ExampleReadsApp(ctx, config=config)
        #output = era.do_analysis(params)

        #END run_efi_family_app

        # At some point might do deeper type checking...
        if not isinstance(output, dict):
            raise ValueError('Method run_efi_family_app return value ' +
                             'output is not type dict as required.')
        # return the results
        return [output]

    def status(self, ctx):
        #BEGIN_STATUS
        returnVal = {'state': "OK",
                     'message': "",
                     'version': self.VERSION,
                     'git_url': self.GIT_URL,
                     'git_commit_hash': self.GIT_COMMIT_HASH}
        #END_STATUS
        return [returnVal]
