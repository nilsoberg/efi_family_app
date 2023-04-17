
import io
import logging
import os
import subprocess
import uuid
import json
import shutil

# This is the SFA base package which provides the Core app class.
from base import Core


MODULE_DIR = "/kb/module"
TEMPLATES_DIR = os.path.join(MODULE_DIR, "lib/templates")


def get_streams(process):
    """
    Returns decoded stdout,stderr after loading the entire thing into memory
    """
    stdout, stderr = process.communicate()
    return (stdout.decode("utf-8", "ignore"), stderr.decode("utf-8", "ignore"))


class EstJob(Core):

    def __init__(self, ctx, config, clients_class=None):
        super().__init__(ctx, config, clients_class)
        # self.shared_folder is defined in the Core App class.
        self.output_dir = os.path.join(self.shared_folder, 'job_temp')
        self._mkdir_p(self.output_dir)
        self.script_file = ''
        self.est_dir = config.get('est_home')
        self.efi_db_config = config.get('efi_db_config')
        self.report = self.clients.KBaseReport
        if self.efi_db_config == None:
            self.efi_db_config = '/apps/EFIShared/db_conf.sh'
        #TODO: make a more robust way of doing this
        self.est_env = ['/apps/EST/env_conf.sh', '/apps/EFIShared/env_conf.sh', '/apps/env.sh', '/apps/blast_legacy.sh', self.efi_db_config]



    def create_job(self, params: dict):

        create_job_pl = os.path.join(self.est_dir, 'create_job.pl')

        process_args = [create_job_pl, '--job-dir', self.output_dir]
        if params.get('job_id') != None:
            process_args.extend(['--job-id', params['job_id']])

        process_params = {'type': 'generate'}
        if params.get('family') != None:
            process_params['family'] = params['family']
        json_str = json.dumps(process_params)
        process_args.extend(['--params', "'"+json_str+"'"])
        process_args.extend(['--env-scripts', ','.join(self.est_env)])

        process = subprocess.Popen(
            process_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = get_streams(process)
        if stdout != None:
            script_file = stdout.strip()
        else:
            return None

        print("### OUTPUT FROM CREATE JOB ####################################################################################\n")
        print(str(stdout) + "\n---------\n")
        print(str(stderr) + "\n")

        self.script_file = script_file

        return script_file



    def start_job(self):
        if not os.path.exists(self.script_file):
            #TODO: throw error
            return False

        start_job_pl = os.path.join('/bin/bash')

        process_args = [start_job_pl, self.script_file]
        process = subprocess.Popen(
            process_args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        stdout, stderr = get_streams(process)

        print("### OUTPUT FROM GENERATE ######################################################################################\n")
        print(str(stdout) + "\n---------\n")
        print(str(stderr) + "\n")

        return True



    def generate_report(self, params):
        #TODO:
        """
        This method is where to define the variables to pass to the report.
        """
        # This path is required to properly use the template.
        reports_path = os.path.join(self.shared_folder, "reports")
        self._mkdir_p(reports_path)
        # Path to the Jinja template. The template can be adjusted to change
        # the report.
        template_path = os.path.join(TEMPLATES_DIR, "report.html")

        length_histogram = "length_histogram_uniprot.png"
        alignment_length = "alignment_length.png"
        percent_identity = "percent_identity.png"

        length_histogram_src = os.path.join(self.output_dir, "output", length_histogram)
        alignment_length_src = os.path.join(self.output_dir, "output", alignment_length)
        percent_identity_src = os.path.join(self.output_dir, "output", percent_identity)

        length_histogram_out = os.path.join(reports_path, length_histogram)
        alignment_length_out = os.path.join(reports_path, alignment_length)
        percent_identity_out = os.path.join(reports_path, percent_identity)

        length_histogram_rel = os.path.join("reports", length_histogram)
        alignment_length_rel = os.path.join("reports", alignment_length)
        percent_identity_rel = os.path.join("reports", percent_identity)

        #print(os.listdir(self.output_dir + "/output"))

        shutil.copyfile(length_histogram_src, length_histogram_out)
        shutil.copyfile(alignment_length_src, alignment_length_out)
        shutil.copyfile(percent_identity_src, percent_identity_out)

        template_variables = {
                'length_histogram_file': length_histogram_rel,
                'alignment_length_file': alignment_length_rel,
                'percent_identity_file': percent_identity_rel,
                }

        # The KBaseReport configuration dictionary
        config = dict(
            report_name = f"EfiFamilyApp_{str(uuid.uuid4())}",
            reports_path = reports_path,
            template_variables = template_variables,
            workspace_name = params["workspace_name"],
        )
        
        output_report = self.create_report_from_template(template_path, config)
        print("OUTPUT REPORT\n")
        print(str(output_report) + "\n")
        return output_report



    def _mkdir_p(self, path):
        """
        _mkdir_p: make directory for given path
        """
        if not path:
            return
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else:
                raise

