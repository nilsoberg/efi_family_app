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
        string workspace_name;
        int workspace_id;
        string job_name;
        list<mapping<string, string>> option_blast;
        list<mapping<string, string>> option_family;
        list<mapping<string, string>> option_fasta;
        list<mapping<string, string>> option_accession;
    } EfiEstAppParams;


    /*funcdef run_efi_family_app(mapping<string,UnspecifiedObject> params) returns (ReportResults output) authentication required;*/
    funcdef run_efi_family_app(EfiEstAppParams params) returns (ReportResults output) authentication required;

};
