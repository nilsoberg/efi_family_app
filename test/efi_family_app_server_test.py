# -*- coding: utf-8 -*-
import os
import time
import unittest
import collections.abc
import re
import shutil
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
    def test_est_generate(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods

        print("### TESTING EST GENERATE WITH FRAGMENTS\n")
        test_params = {"exclude_fragments": False}
        self.run_est_job_types(test_params)

        print("### TESTING EST WITHOUT FRAGMENTS\n")
        test_params = {"exclude_fragments": True}
        self.run_est_job_types(test_params)

    # NOTE: According to Python unittest naming rules test method names should start from 'test'. # noqa
    # @unittest.skip("Skip test for debugging")
    def test_est_analysis(self):
        # Prepare test objects in workspace if needed using
        # self.getWsClient().save_objects({'workspace': self.getWsName(),
        #                                  'objects': []})
        #
        # Run your method by
        # ret = self.getImpl().your_method(self.getContext(), parameters...)
        #
        # Check returned data with
        # self.assertEqual(ret[...], ...) or other unittest methods

        print("### TESTING EST ANALYSIS WITH FRAGMENTS\n")
        test_params = {"exclude_fragments": False}
        self.run_est_analysis(test_params)

        print("### TESTING EST ANALYSIS WITHOUT FRAGMENTS\n")
        test_params = {"exclude_fragments": True}
        self.run_est_analysis(test_params)

    def run_est_analysis(self, test_params):

        #TODO: load an example output dataset and create an SSN from it

        return True


    # This function will eventually take in all of the parameters that we will use as input to the
    # various options.  It is provided so that the same code can be run with options toggled
    # to different values for testing of functionality.
    # All of the code inside here will call it's own asserts to check if the various tests were successful.
    def run_est_job_types(self, test_params):

        exclude_fragments = test_params["exclude_fragments"]

        data_dir = self.get_data_dir_path()
        num_seq_file = data_dir + "/expected_seq.txt"
        num_seq_data = {}
        if os.path.isfile(num_seq_file):
            with open(num_seq_file) as fh:
                line = fh.readline()
                while line and num_seq_F == 0 and num_seq_NF == 0:
                    mx = reg.search("^num_expected_no_fragments\t([^\t]+)\t(\d+)\s*$", line)
                    if mx != None and exclude_fragments:
                        num_seq_data[mx.group(1)] = mx.group(2)
                    else:
                        mx = reg.search("^num_expected_fragments\t([^\t]+)\t(\d+)\s*$", line)
                        if mx != None:
                            num_seq_data[mx.group(1)] = mx.group(2)

        test_data_dir = self.get_data_dir_path()

        ##################################################
        # Test BLAST option
        print("RUNNING BLAST TEST\n")

        self.prep_job_dir()
        print("    RUNNING BLAST TEST FOR INPUT FILE PARAMETER\n")
        self.run_est_BLAST(test_params, num_seq_data["blast"], use_seq_file: True)

        self.prep_job_dir()
        print("    RUNNING BLAST TEST FOR INPUT SEQUENCE ARG\n")
        self.run_est_BLAST(test_params, num_seq_data["blast"], use_seq_file: False)

        print("... SUCCESS\n\n")

        ##################################################
        # Test FAMILY option
        print("RUNNING FAMILY TEST\n")
        self.run_est_FAMILY(test_data_dir, test_params, num_seq_data["family"])
        print("... SUCCESS\n\n")

        ##################################################
        # Test FASTA option
        print("RUNNING FASTA TEST\n")
        self.run_est_FAMILY(test_data_dir, test_params, num_seq_data["fasta"])
        print("... SUCCESS\n\n")

        ##################################################
        # Test ACCESSION option
        print("RUNNING ACCESSION TEST\n")
        self.run_est_ACCESSION(test_data_dir, test_params, num_seq_data["accession"])
        print("... SUCCESS\n\n")

        return True

    def run_est_BLAST(self, test_params, num_seq_data, use_seq_file: False):
        test_blast_seq_file = self.get_test_data_file("blast")
        blast_seq = self.read_data_from_file(test_blast_seq_file) # Read the test file data
        blast_file_path = self.get_job_output_dir() + "/query.fa"
        self.save_data_to_file(">INPUT_ID\n"+blast_seq+"\n", blast_file_path) # Write the test file data to a location that can be read by the job (even though the unit test job can read the test files, we test this to ensure that the scripts are reading from the job locations)

        blast_data = {"blast_exclude_fragments": test_params["exclude_fragments"]}
        if use_seq_file:
            blast_data["sequence_file"] = seq_file
        else:
            blast_data["blast_sequence"] = blast_seq

        self.run_test("option_blast", blast_data, num_seq_data)

    def run_est_FAMILY(self, test_data_dir, test_params, num_seq_data):
        fam_name = "PF05544"
        fam_data = {"fam_family_name": fam_name, "fam_use_uniref": "none", "fam_exclude_fragments": test_params["exclude_fragments"]}
        self.run_test("option_family", fam_data, num_seq_data)

    def run_est_FASTA(self, test_data_dir, test_params, num_seq_data):
        fasta_file = self.get_test_data_file("fasta")
        fasta_file_job_path = self.get_job_output_dir() + "/input.fa"
        fasta_data = {"fasta_file": fasta_file_job_path, "fasta_exclude_fragments": test_params["exclude_fragments"]}
        self.run_test("option_fasta", fasta_data, num_seq_data)

    def run_est_ACCESSION(self, test_data_dir, test_params, num_seq_data):
        acc_file = self.get_test_data_file("accession")
        acc_file_job_path = self.get_job_output_dir() + "/id_list.txt"
        acc_data = {"acc_input_file": acc_file_job_path, "acc_exclude_fragments": test_params["exclude_fragments"]}
        self.run_test("option_accession", acc_data, num_seq_data)


    def run_test(self, option_key, option_data, num_seq):

        db_conf = "/apps/EFIShared/testing_db_conf.sh"

        run_data = {
                "workspace_name": self.wsName,
                "reads_ref": "70257/2/1",
                "output_name": "EfiFamilyApp",
                "efi_db_config": db_conf,
            }
        run_data[option_key] = option_data

        ret = self.serviceImpl.run_efi_family_app(
            self.ctx,
            run_data,
        )

        self.assertTrue(ret != None, "No report returned")
        self.assertTrue(isinstance(ret, list), "Report should be a list")
        self.assertTrue(len(ret) > 0, "Report must have at least one element")

        shared_dir = ret[0]["shared_folder"]
        print("OUTPUT DIR IS: " + shared_dir + "\n")
        self.assertTrue(os.path.exists(shared_dir), "Shared directory " + shared_dir + " does not exist.")

        job_dir = os.path.join(shared_dir, "job_temp", "output")
        report_dir = os.path.join(shared_dir, "reports")
        comp_results_file = os.path.join(job_dir, "1.out")
        output_image = os.path.join(report_dir, "length_histogram_uniprot.png")

        self.assertTrue(os.path.exists(job_dir), "Job output directory " + job_dir + " does not exist.")
        self.assertTrue(os.path.exists(report_dir), "Report output directory " + job_dir + " does not exist.")
        self.assertTrue(os.path.isfile(comp_results_file), "Computation failed; results file " + comp_results_file + " does not exist.")
        self.assertTrue(os.path.isfile(output_image), "No output image " + output_image + " was found in report dir")

        num_lines = self.count_lines(comp_results_file)
        print("Found " + num_lines + " results\n")
        if num_seq > 0:
            self.assertTrue(num_seq == num_lines, "Number of expected results is not equal to returned results")

    ###############################################################################################
    # UTILITY/MISC METHODS

    def count_lines(self, file_path):
        lc = 0
        with open(file_path, "r") as fh:
            while line:
                lc = lc + 1
        return lc

    def save_data_to_file(self, contents, file_path):
        with open(file_path, "w") as fh:
            fh.write(contents)

    def get_test_data_file(self, file_type):
        data_dir = self.get_data_dir_path()
        self.assertTrue(data_dir != None, "Unable to find data directory for unit test files")

        if file_type == "fasta":
            file_path = data_dir + "/PF05544_sp.fasta"
        elif file_type == "accession":
            file_path = data_dir + "/PF05544_sp.id_list.txt"
        elif file_type == "blast":
            file_path = data_dir + "/blast_seq.fa"
        else:
            self.assertTrue(false, "Invalid get_test_data_file " + file_type + " requested")

        self.assertTrue(os.path.isfile(file_path), "Unable to find " + file_type + " file for unit test")

        return file_path

    def get_data_dir_path(self):
        conf_file = "/apps/EFIShared/testing_db_conf.sh"
        data_path = None
        with open(conf_file, "r") as fh:
            line = fh.readline()
            while line and !data_path:
                rx = re.search("^export EFI_DB=(.+)/[^/]+$", line)
                if rx != None:
                    data_path = rx.group(1)
        return data_path

    def prep_job_dir(self):
        output_dir = self.get_job_output_dir()
        if os.path.isdir(output_dir):
            shutil.rmtree(output_dir)
        os.mkdir(output_dir)

    def get_job_output_dir(self):
        # This is where the EST jobs put their output data
        output_dir = self.scratch + "/job"
        return output_dir


