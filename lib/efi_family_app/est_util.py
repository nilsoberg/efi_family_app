
import io
import logging
import os
import subprocess
import uuid
import json

# This is the SFA base package which provides the Core app class.
from base import Core




@staticmethod
def get_streams(process):
    """
    Returns decoded stdout,stderr after loading the entire thing into memory
    """
    stdout, stderr = process.communicate()
    return (stdout.decode("utf-8", "ignore"), stderr.decode("utf-8", "ignore"))


class EstJob(Core):

    def __init__(self, ctx, config):
        # self.shared_folder is defined in the Core App class.
        self.output_dir = os.path.join(self.shared_folder, 'job_temp', str(uuid.uuid4()))
        self._mkdir_p(self.output_dir)
        self.script_file = ''
        self.est_dir = config.get('est_home')



    def create_job(self, params: dict):

        create_job_pl = os.path.join(self.est_dir, 'create_job.pl')

        process_args = [create_job_pl, '--job-dir', self.output_dir]
        if params.get('job_id') != None:
            process_args.append('--job-id', params['job_id'])

        process_params = {'type': 'generate'}
        if params.get('family') != None:
            process_params['family'] = params['family']
        json_str = json.dumps(process_params)
        process_args.append('--params', json_str)

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

        # Do something???

        return True



    def generate_report(self, create_args, ca, sa):
        #TODO:
        """
        This method is where to define the variables to pass to the report.
        """
        # This path is required to properly use the template.
        reports_path = os.path.join(self.shared_folder, "reports")
        # Path to the Jinja template. The template can be adjusted to change
        # the report.
        template_path = os.path.join(TEMPLATES_DIR, "report.html")
        # A sample multiplication table to use as output
        table = [[i * j for j in range(10)] for i in range(10)]
        headers = "one two three four five six seven eight nine ten".split(" ")
        # A count of the base calls in the reads
        count_df_html = params["count_df"].to_html()
        # Calculate a correlation table determined by the quality scores of
        # each base read. This requires pandas and matplotlib, and these are
        # listed in requirements.txt. You can see the resulting HTML file after
        # runing kb-sdk test in ./test_local/workdir/tmp/reports/index.html
        scores_df_html = (
            pd.DataFrame(params["scores"]).corr().style.background_gradient().render()
        )
        # The keys in this dictionary will be available as variables in the
        # Jinja template. With the current configuration of the template
        # engine, HTML output is allowed.
        template_variables = dict(
            count_df_html=count_df_html,
            headers=headers,
            scores_df_html=scores_df_html,
            table=table,
            upa=params["upa"],
            output_value=params["output_value"],
        )
        # The KBaseReport configuration dictionary
        config = dict(
            report_name=f"ExampleReadsApp_{str(uuid.uuid4())}",
            reports_path=reports_path,
            template_variables=template_variables,
            workspace_name=params["workspace_name"],
        )
        return self.create_report_from_template(template_path, config)



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


