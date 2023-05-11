/*
A KBase module: efi_family_app
*/

module efi_family_app {
    /*
     * The basic report structure that KBase requires.
     */
    typedef structure {
        string report_name;
        string report_ref;
    } ReportResults;

    typedef structure {
        string path;
        string shock_id;
        string name;
        string label;
        string description;
    } File;

    typedef structure {
        string workspace_name;
        int workspace_id;
        string job_name;
        list<mapping<string, string>> option_blast;
        list<mapping<string, string>> option_family;
        list<mapping<string, string>> option_fasta;
        list<mapping<string, string>> option_accession;
    } EfiEstAppParams;

   /*
    * The output of the first step in creating an SSN (i.e. "generate").
    * Contains a File and a job label. Also serves as input to the
    * Analysis module.
    * Returned data:
    *     File gen_file - A File object (can be defined multiple ways)
    *     string label - Label of job name
    */
   typedef structure {
       File gen_file;
       string label;
   } GenerateResults;


    funcdef run_efi_family_app(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;
    /*funcdef run_efi_family_app(EfiEstAppParams params) returns (ReportResults output) authentication required;*/

    funcdef run_efi_analysis_app(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;
    /*funcdef run_efi_analysis_app(GenerateResults results) returns (ReportResults output) authentication required;*/
};
