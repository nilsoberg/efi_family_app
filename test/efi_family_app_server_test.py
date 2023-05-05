# -*- coding: utf-8 -*-
import os
import time
import unittest
import collections.abc
from configparser import ConfigParser

from efi_family_app.efi_family_appImpl import efi_family_app
from efi_family_app.efi_family_appServer import MethodContext
from efi_family_app.authclient import KBaseAuth as _KBaseAuth

from installed_clients.WorkspaceClient import Workspace


class efi_family_appTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        token = os.environ.get("KB_AUTH_TOKEN", None)
        config_file = os.environ.get("KB_DEPLOYMENT_CONFIG", None)
        cls.cfg = {}
        config = ConfigParser()
        config.read(config_file)
        for nameval in config.items("efi_family_app"):
            cls.cfg[nameval[0]] = nameval[1]
        # Getting username from Auth profile for token
        authServiceUrl = cls.cfg["auth-service-url"]
        auth_client = _KBaseAuth(authServiceUrl)
        user_id = auth_client.get_user(token)
        # WARNING: don't call any logging methods on the context object,
        # it'll result in a NoneType error
        cls.ctx = MethodContext(None)
        cls.ctx.update(
            {
                "token": token,
                "user_id": user_id,
                "provenance": [
                    {
                        "service": "efi_family_app",
                        "method": "please_never_use_it_in_production",
                        "method_params": [],
                    }
                ],
                "authenticated": 1,
            }
        )
        cls.wsURL = cls.cfg["workspace-url"]
        cls.wsClient = Workspace(cls.wsURL)
        cls.serviceImpl = efi_family_app(cls.cfg)
        cls.scratch = cls.cfg["scratch"]
        cls.callback_url = os.environ["SDK_CALLBACK_URL"]
        suffix = int(time.time() * 1000)
        cls.wsName = "test_ContigFilter_" + str(suffix)
        ret = cls.wsClient.create_workspace({"workspace": cls.wsName})  # noqa

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, "wsName"):
            cls.wsClient.delete_workspace({"workspace": cls.wsName})
            print("Test workspace was deleted")

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    # @unittest.skip("Skip test for debugging")
    def test_your_method(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods

        db_conf = "/apps/EFIShared/testing_db_conf.sh"
        test_family = "PF05544"
        ret = self.serviceImpl.run_efi_family_app(
            self.ctx,
            {
                "workspace_name": self.wsName,
                "reads_ref": "70257/2/1",
                "output_name": "EfiFamilyApp",
                "option_family": {"fam_family_name": test_family, "fam_use_uniref": "none"},
                "efi_db_config": db_conf,
                #"est": args,
            },
        )

        print("Show STDOUT\n")

        self.assertTrue(ret != None, "No report returned")
        self.assertTrue(isinstance(ret, list), "Report should be a list")
        self.assertTrue(len(ret) > 0, "Report must have at least one element")

        shared_dir = ret[0]["shared_folder"]
        self.assertTrue(os.path.exists(shared_dir), "Shared directory " + shared_dir + " does not exist.")

        job_dir = os.path.join(shared_dir, "job_temp", "output")
        report_dir = os.path.join(shared_dir, "reports")
        comp_results_file = os.path.join(job_dir, "1.out")
        output_image = os.path.join(report_dir, "length_histogram_uniprot.png")

        self.assertTrue(os.path.exists(job_dir), "Job output directory " + job_dir + " does not exist.")
        self.assertTrue(os.path.exists(report_dir), "Report output directory " + job_dir + " does not exist.")
        self.assertTrue(os.path.isfile(comp_results_file), "Computation failed; results file " + comp_results_file + " does not exist.")
        self.assertTrue(os.path.isfile(output_image), "No output image " + output_image + " was found in report dir")

        # next steps:
        # - download report
        # - assert that the report has expected contents

        return True

