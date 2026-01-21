
Documentation for PLINK 2.0 GWAS
================================

# Module Overview


Use plink 2.0 to run parallelized GWAS for binary and/or quantitative traits.
- [Tool Paper Link for Reference](https://academic.oup.com/gigascience/article/4/1/s13742-015-0047-8/2707533)
- [Tool Documentation Link for Reference](https://www.cog-genomics.org/plink/2.0/)
- [Example Config File](https://github.com/PMBB-Informatics-and-Genomics/pmbb-geno-pheno-toolkit/tree/main/Example_Configs/plink2_gwas.config)
- [Example nextflow.config File](https://github.com/PMBB-Informatics-and-Genomics/pmbb-geno-pheno-toolkit/tree/main/Example_Configs/nextflow.config)

## Software Requirements


* [Nextflow version 24.04.3](https://www.nextflow.io/docs/latest/cli.html)

* [Singularity 3.8.3](https://sylabs.io/docs/) OR [Docker 4.30.0](https://docs.docker.com/)
## Commands for Running the Workflow


* Singularity Command: `singularity build plink2_gwas.sif docker://pennbiobank/plink2_gwas:latest`

* Docker Command: `docker pull pennbiobank/plink2_gwas:latest`

* Pull from Google Container Registry: `docker pull gcr.io/verma-pmbb-codeworks-psom-bf87/plink2_gwas:latest`

* Run Command: `nextflow run /path/to/toolkit/module/plink2_gwas.nf`

* Common `nextflow run` flags:

    * `-resume` flag picks up workflow where it left off

    * `-stub` performs a dry run, checks channels without executing code

    * `-profile` selects the compute profiles in nextflow.config

    * `-profile standard` uses the Docker image to execute processes

    * `-profile cluster` uses the Singularity container and submits processes to a queue

    * `-profile all_of_us` uses the Docker image on All of Us Workbench

* More info: [Nextflow documentation](https://www.nextflow.io/docs/latest/cli.html)
# Detailed Pipeline Steps

## Part I: Setup


1. Start your own tools directory and go there. You may do this in your project analysis directory, but it often makes sense to clone into a general `tools` location

```sh
# Make a directory to clone the pipeline into
TOOLS_DIR="/path/to/tools/directory"
mkdir $TOOLS_DIR
cd $TOOLS_DIR
```

2. Download the source code by cloning from git

```sh
git clone None
cd $TOOLS_DIR/pmbb-nf-toolkit-plink2-gwas
```

3. Build the singularity image
    - you may call the image whatever you like, and store it wherever you like. Just make sure you specify the name in `nextflow.conf`
    - this does NOT have to be done for every saige-based analysis, but it is good practice to re-build every so often as we update regularly.


```sh
cd $TOOLS_DIR/pmbb-nf-toolkit-plink2-gwas
singularity build plink2_gwas.sif docker://pennbiobank/plink2_gwas:latest
```
## Part II: Configure your run


1. Make a separate analysis/run/working directory.
    - The quickest way to get started, is to run the analysis in the folder the pipeline is run. However, subsequent analyses will over-write results from previous analyses.
    - ❗This step is optional, but We Highly recommend making a `tools` directory separate from your `run` directory. We recommend storing the `nextflow.conf` in here as it shouldn't change between runs.


```sh
WDIR="/path/to/analysis/run1"
mkdir -p $WDIR
cd $WDIR
```

2. Fill out the `nextflow.config` file for your system.
    - See [Nextflow configuration documentation](https://www.nextflow.io/docs/latest/config.html) for information on how to configure this file. An example can be found on our GitHub: [Nextflow Config](https://github.com/PMBB-Informatics-and-Genomics/pmbb-geno-pheno-toolkit/blob/main/Example_Configs/nextflow.config).
    - ❗IMPORTANTLY, you must configure a user-defined profile for your run environments (local, docker, saige, cluster, etc.). If multiple profiles are specified, run with a specific profile using `nextflow run -profile $MY_PROFILE`.
    - For singularity, The profile's attribute `process.container` should be set to `'/path/to/plink2_gwas.sif'` (replace `/path/to` with the location where you built the image above). See [Nextflow Executor Information](https://www.nextflow.io/docs/latest/executor.html) for more details.
    - ⚠️As this file remains mostly unchanged for your system, We recommend storing this file in the `tools/pipeline` directory and passing it to the pipeline with `-c /path/to/nextflow.config`.


3. Create a pipeline-specific `.config` file specifying your run parameters and input files. See Below for workflow-specific parameters and what they mean.
    - Everything in here can be configured in `nextflow.config`, however we find it easier to separate the system-level profiles from the individual run parameters.
    - Examples can be found in our Pipeline-Specific [Example Config Files](https://github.com/PMBB-Informatics-and-Genomics/pmbb-geno-pheno-toolkit/tree/main/Example_Configs).
    - you can compartamentalize your config file as much as you like by passing
    - There are 2 ways to specify the config file during a run:

        - with the `-c` option on the command line: `nextflow run -c Plink_2.0_GWAS/plink2_gwas.config`
        - in the `nextflow.config`: at the top of the file add: `includeConfig Plink_2.0_GWAS/plink2_gwas.config`

## Part III: Run your analysis


❗We HIGHLY recommend doing a STUB run to test the analysis using the `-stub` flag. This is a dry run to make sure your environment, parameters, and input_files are specified and formatted correctly.❗We also HIGHLY recommend doing a TEST run with the included test data in `$TOOLS_DIR/pmbb-nf-toolkit-plink2-gwas/test_data`we have several pre-configured analyses runs with input data and fully-specified config files.

```sh
# run an exwas stub
nextflow run $TOOLS_DIR/pmbb-nf-toolkit-plink2-gwas/plink2_gwas.nf \
   -profile cluster \
   -c /path/to/nextflow.config \
   -c Plink_2.0_GWAS/plink2_gwas.config \
   -stub

# run an exwas for real
nextflow run $TOOLS_DIR/pmbb-nf-toolkit-plink2-gwas/plink2_gwas.nf \
   -profile cluster \
   -c /path/to/nextflow.config \
   -c Plink_2.0_GWAS/plink2_gwas.config

# resume an exwas run if it was interrupted or ran into an error
nextflow run $TOOLS_DIR/pmbb-nf-toolkit-plink2-gwas/plink2_gwas.nf \
   -profile cluster \
   -c /path/to/nextflow.config \
   -c Plink_2.0_GWAS/plink2_gwas.config \
   -resume
```
# Pipeline Parameters

## Input Files for PLINK_2.0_GWAS


* Cohort Membership

    * 0/1 table with cohorts as columns and participants as rows - 1 indicates that that row’s participant is a member of that column’s cohort

    * Type: Data Table

    * Format: csv

    * File Header:


    ```
    IID,POP1,POP2,POP3
    1a1,1,0,1
    1a2,1,0,0
    1a3,0,0,0
    1a4,1,0,0
    1a5,1,0,0
    1a6,1,1,0
    1a7,0,0,0
    1a8,1,0,1
    1a9,0,1,1
    
    ```

* Phenotypes and Covariates

    * table with participants as rows and all needed phenotypes and covariates as columns

    * Type: Data Table

    * Format: csv

    * File Header:


    ```
    IID,y_quantitative,y_binary,x1,x2,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10
    1a1,2.0046544617651,0,1.51178116845085,1,0,0,0,0,0,0,0,0,1,0
    1a2,0.104213400269085,0,0.389843236411431,1,0,0,0,0,0,0,0,0,1,1
    1a3,-0.397498354133647,0,-0.621240580541804,1,0,0,0,0,0,0,0,0,0,1
    1a4,-0.333177899030597,0,-2.2146998871775,1,0,0,0,0,0,0,0,0,1,1
    1a5,1.21333962248852,0,1.12493091814311,1,0,0,0,0,0,0,0,0,1,0
    1a6,-0.275411643032321,0,-0.0449336090152309,1,0,0,0,0,0,0,0,0,1,0
    1a7,0.438532936074923,0,-0.0161902630989461,0,0,0,0,0,0,0,0,0,0,0
    1a8,0.0162938047248591,0,0.943836210685299,0,0,0,0,0,0,0,0,0,1,1
    1a9,0.147167262428064,0,0.821221195098089,1,0,0,0,0,0,0,0,0,1,0
    ```

* Sex Specific Phenotype List

    * A newline-separated list of phenotypes that should be excluded from non-sex-stratified cohorts (e.g., include in AFR_F or AFR_M but exclude from AFR_ALL). Set to 

    * Type: List File

    * Format: txt
## Output Files for PLINK_2.0_GWAS


* GWAS Manhattan Plots

    * Manhattan plots for the GWAS results. If annotate is set to true, top hits will be annotated with RSIDs and the nearest gene

    * Type: Manhattan Plot

    * Format: png

        * Parallel By: Cohort, Phenotype

* GWAS Summary Statistics

    * Summary statistics for all variants tested in the GWAS. Columns will be renamed according to the plink2_col_names parameter

    * Type: Summary Statistics

    * Format: tsv.gz

        * Parallel By: Cohort, Phenotype

* Plink 2.0 GWAS Top Hits Table

    * A FILTERED top hits csv summary file of results including cohort, phenotype, gene, group annotation, p-values, and other counts. One single summary file will be aggregated from all the “top hits” in each GWAS Summary Statistics file. The p-value threshold is specified by the user

    * Type: Summary Table

    * Format: csv

* GWAS QQ Plots

    * QQ plots for the GWAS results

    * Type: QQ Plot

    * Format: png

        * Parallel By: Cohort, Phenotype
## Other Parameters for PLINK_2.0_GWAS

### Association Test Modeling


* `cont_covars ` (Type: List)

    * Continuous covariates list

* `sex_strat_cont_covars` (Type: List)

    * Continuous covariates for sex stratified cohorts to ensure model converges

* `sex_strat_cat_covars` (Type: List)

    * Categorical covariates for sex stratified cohorts to ensure model converges
### PLINK


* `plink_chr_suffix` (Type: Plink Fileset Prefix)

    * Full path to chromosome-separated plink files - everything after the chromosome number but before the extension

* `plink_chr_prefix` (Type: Plink Fileset Prefix)

    * Full path to chromosome-separated plink files - everything before the chromosome number
### Post-Processing


* `plink2_col_names` (Type: Map (Dictionary))

    * Default Plink 2.0 column names mapped to new ones

* `biofilter_close_dist` (Type: Float)

    * The distance in bp for something to be considered “close” vs “far” with respect to nearest gene annotation. Value is often 5E4
### Pre-Processing


* `id_col ` (Type: String)

    * ID column label

* `data_csv` (Type: File Path)

    * A csv table with all of the phenotypes and covariates to be tested

    * Corresponding Input File: Phenotypes and Covariates

        * table with participants as rows and all needed phenotypes and covariates as columns

        * Type: Data Table

        * Format: csv

        * File Header:


        ```
        IID,y_quantitative,y_binary,x1,x2,a1,a2,a3,a4,a5,a6,a7,a8,a9,a10
        1a1,2.0046544617651,0,1.51178116845085,1,0,0,0,0,0,0,0,0,1,0
        1a2,0.104213400269085,0,0.389843236411431,1,0,0,0,0,0,0,0,0,1,1
        1a3,-0.397498354133647,0,-0.621240580541804,1,0,0,0,0,0,0,0,0,0,1
        1a4,-0.333177899030597,0,-2.2146998871775,1,0,0,0,0,0,0,0,0,1,1
        1a5,1.21333962248852,0,1.12493091814311,1,0,0,0,0,0,0,0,0,1,0
        1a6,-0.275411643032321,0,-0.0449336090152309,1,0,0,0,0,0,0,0,0,1,0
        1a7,0.438532936074923,0,-0.0161902630989461,0,0,0,0,0,0,0,0,0,0,0
        1a8,0.0162938047248591,0,0.943836210685299,0,0,0,0,0,0,0,0,0,1,1
        1a9,0.147167262428064,0,0.821221195098089,1,0,0,0,0,0,0,0,0,1,0
        ```
### QC Options


* `hwe_min_pvalue` (Type: Float)

    * Minimum HWE p-value for plink QC - variants with smaller p-values will be removed

* `min_maf` (Type: Float)

    * Minimum minor allele frequency for plink QC

* `max_missing_per_sample` (Type: Float)

    * Maximum missingness per sample - samples with more missingness than this will be removed
### Workflow


* `sex_strat_cohort_list` (Type: List)

    * List of cohorts that are sex stratified
# Configuration and Advanced Workflow Files

## Example Config File Contents (From Path)


```
params {
    // default assumes use of the docker container
    my_python = "/opt/conda/bin/python"
    
    data_csv = "/path/to/data/cleaned_test_pheno_covars.csv"
    cohort_sets = "/path/to/data/Imputed_sample_table.csv"
    related_list = '/path/to/data/PMBB-Release-2020-2.0_genetic_imputed-topmed-r2_relateds_droplist.txt'

    // default paths are for PMBB Imputed data
    plink_chr_prefix = "/path/to/data/PMBB-Release-2020-2.0_genetic_imputed-topmed-r2_chr"
    plink_chr_suffix = ""
    plink_flag = "--pfile"

    min_maf = 0.05
    max_missing_per_var = 0.05
    hwe_min_pvalue = 1E-10

    // categorical and continuous covariates
    cat_covars = ["SEX"]
    cont_covars = ["DATA_FREEZE_AGE", "Genotype_PC1","Genotype_PC2","Genotype_PC3",	"Genotype_PC4"]

    sex_strat_cat_covars = []
    sex_strat_cont_covars = cont_covars

    // P-Value Threshold for Summarizing Results at the End
    p_cutoff_summarize = 0.00001

    // ID column label
    id_col = "PMBB_ID"

// list of cohorts (usually ancestry-stratified)
   cohort_list = [
        "PMBB_AMR_ALL", "PMBB_AMR_M", "PMBB_AMR_F",
        "PMBB_AFR_ALL", "PMBB_AFR_F", "PMBB_AFR_M",
        "PMBB_EAS_ALL", "PMBB_EAS_F", "PMBB_EAS_M",
        "PMBB_EUR_ALL", "PMBB_EUR_F", "PMBB_EUR_M",
        ]

    sex_strat_cohort_list = [
        "PMBB_AMR_M", "PMBB_AMR_F",
        "PMBB_AFR_F", "PMBB_AFR_M",
        "PMBB_EAS_F", "PMBB_EAS_M",
        "PMBB_EUR_F", "PMBB_EUR_M"
        ]

    // lists of smaller cohorts used for testing
    // cohort_list = ["AMR_ALL", "AMR_M", "EAS_ALL", "EAS_F", "EAS_M"]
    // sex_strat_cohort_list = ["AMR_M", "EAS_F", "EAS_M"]

    // binary and quantitative phenotype lists
    bin_pheno_list = ["T2D", "AAA"]
    // bin_pheno_list = []
    quant_pheno_list = ["BMI_median", "LDL_median"]

    // list of sex-specific phenotypes to handle in _ALL cohorts
    sex_specific_pheno_file = null
    
    // list of chromosomes
    chromosome_list = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22"]
    // list of smaller chromosomes used for testing
    // chromosome_list = ["21", "22"]

    // Add Biofilter Annotations
    annotate = true
    biofilter_build = '38' // can be 19 or 38
    biofilter_loki = '/path/to/data/loki.db'
    biofilter_script = '/app/biofilter.py' // Must be an executable python file
    biofilter_close_dist = 5E4

    // Dictionary (Map) with default Plink2 GWAS GLM column names mapped to new ones
    plink2_col_names = [
        '#CHROM': 'chromosome',
        POS: 'base_pair_location',
        ID: 'variant_id',
        A2: 'other_allele',
        A1: 'effect_allele',
        A1_FREQ: 'effect_allele_frequency',
        BETA: 'beta',
        SE: 'standard_error',
        T_STAT: 't_statistic',
        P: 'p_value',
        N: 'n'
    ]
}
```
## Current `nextflow.config` contents


```
includeConfig 'plink2_gwas.config'

profiles {

    non_docker_dev {
        // run locally without docker
        process.executor = awsbatch-or-lsf-or-slurm-etc
    }

    standard {
        // run locally with docker
        process.executor = awsbatch-or-lsf-or-slurm-etc
        process.container = 'pennbiobank/plink2_gwas'
        docker.enabled = true
    }

    cluster {
        // run on LSF cluster
        process.executor = awsbatch-or-lsf-or-slurm-etc
        process.queue = 'epistasis_normal'
        executor {
            queueSize=500
        }
        process.memory = '15GB'
    	process.container = 'plink2_gwas.sif'
        singularity.enabled = true
        singularity.runOptions = '-B /root/,/directory/,/names/'
    }

    all_of_us {
        // CHANGE EVERY TIME! These are specific for each user, see docs
        google.lifeSciences.serviceAccountEmail = service@email.gservicaaccount.com
        workDir = /path/to/workdir/ // can be gs://
        google.project = terra project id

        // These should not be changed unless you are an advanced user
        process.container = 'gcr.io/verma-pmbb-codeworks-psom-bf87/plink2_gwas:latest' // GCR SAIGE docker container (static)

        // these are AoU, GCR parameters that should NOT be changed
        process.memory = '15GB' // minimum memory per process (static)
        process.executor = awsbatch-or-lsf-or-slurm-etc
        google.zone = "us-central1-a" // AoU uses central time zone (static)
        google.location = "us-central1"
        google.lifeSciences.debug = true 
        google.lifeSciences.network = "network"
        google.lifeSciences.subnetwork = "subnetwork"
        google.lifeSciences.usePrivateAddress = false
        google.lifeSciences.copyImage = "gcr.io/google.com/cloudsdktool/cloud-sdk:alpine"
        google.enableRequesterPaysBuckets = true
        // google.lifeSciences.bootDiskSize = "20.GB" // probably don't need this
    }
}

```
## Advanced Nextflow Users: Take/Emit Info

### Output Channel (emit) Description


A Channel of three-part tuples with (cohort, phenotype, and path to summary stats file)