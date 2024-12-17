
Documentation for PLINK 2.0 GWAS
================================

# Module Overview


Use plink 2.0 to run parallelized GWAS for binary and/or quantitative traits.

[Paper Link for Reference](https://academic.oup.com/gigascience/article/4/1/s13742-015-0047-8/2707533)

[Tool Documentation Link](https://www.cog-genomics.org/plink/2.0/)
## Cloning Github Repository:


* Command: `git clone https://github.com/PMBB-Informatics-and-Genomics/geno_pheno_workbench.git`

* Navigate to relevant workflow directory run commands (our pipelines assume all of the nextflow files/scripts are in the current working directory)
## Software Requirements:


* [Nextflow version 23.04.1.5866](https://www.nextflow.io/docs/latest/cli.html)

* [Singularity version 3.8.3](https://sylabs.io/docs/) OR [Docker version 4.30.0](https://docs.docker.com/)
## Commands for Running the Workflow


* Singularity Command: `singularity build plink2_gwas.sif docker://pennbiobank/plink2_gwas:latest`

* Command to Pull from Google Container Registry: `docker pull `

* Run Command: `nextflow run plink2_gwas.nf -profile cluster -resume`

* Common `nextflow run` flags:

    * `-resume` flag picks up the workflow where it left off, otherwise, the workflow will rerun from the beginning

    * `-stub` performs a sort of dry run of the whole workflow, checks channels without executing any code

    * `-profile` selects the compute profiles we set up in nextflow.config (see nextflow.config file below)

    * `-profile` selects the compute profiles we set up in nextflow.config (see nextflow.config file below)

    * `-profile standard` uses the docker image to executes the processes

    * `-profile cluster` uses the singularity container and submits processes to a queue- optimal for HPC or LPC computing systems

    * `-profile all_of_us` uses the docker image to execute pipelines on the All of Us Researcher Workbench

* for more information visit the [Nextflow documentation](https://www.nextflow.io/docs/latest/cli.html)
# Configuration Parameters and Input File Descriptions

## Workflow


* `chromosome_list` (Type: List)

    * List of chromosomes, for testing use smaller chromosomes e.g chromosome_list = ["20", "21", "22"]

* `cohort_list` (Type: List)

    * List of cohorts usually ancestry stratified and or sex stratified

* `quant_pheno_list` (Type: List)

    * Quantitative phenotype list

* `sex_strat_cohort_list` (Type: List)

    * List of cohorts that are sex stratified
## Pre-Processing


* `cohort_sets` (Type: File Path)

    * A binary csv table in which the columns are the cohorts and the rows are the individuals. A 1 means that individual is a member of the column’s cohort, and a 0 means they aren’t.

    * Corresponding Input File: Cohort Membership

        * 0/1 table with cohorts as columns and participants as rows - 1 indicates that that row’s participant is a member of that column’s cohort

        * Type: Data Table

        * Format: csv

        * Input File Header:





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

* `data_csv` (Type: File Path)

    * A csv table with all of the phenotypes and covariates to be tested

    * Corresponding Input File: Phenotypes and Covariates

        * table with participants as rows and all needed phenotypes and covariates as columns

        * Type: Data Table

        * Format: csv

        * Input File Header:





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

* `id_col ` (Type: String)

    * ID column label
## QC Options


* `min_maf` (Type: Float)

    * Minimum minor allele frequency for plink QC

* `max_missing_per_sample` (Type: Float)

    * Maximum missingness per sample - samples with more missingness than this will be removed

* `max_missing_per_var` (Type: Float)

    * Maximum missingness per variant - variants with more missingness will be removed

* `hwe_min_pvalue` (Type: Float)

    * Minimum HWE p-value for plink QC - variants with smaller p-values will be removed
## Association Test Modeling


* `sex_strat_cat_covars` (Type: List)

    * Categorical covariates for sex stratified cohorts to ensure model converges

* `sex_strat_cont_covars` (Type: List)

    * Continuous covariates for sex stratified cohorts to ensure model converges

* `cat_covars` (Type: List)

    * Categorical covariates list

* `cont_covars ` (Type: List)

    * Continuous covariates list
## Plink


* `plink_chr_prefix` (Type: Plink Fileset Prefix)

    * Full path to chromosome-separated plink files - everything before the chromosome number

    * Corresponding Input File: Chr-Separated Plink Files

        * A group of plink file sets - one plink set for each chromosome in the analysis

        * Type: Plink Set

        * Format: plink binary

        * Input File Header:





        ```
        CHROM  POS     ID      REF     ALT     FILTER  INFO
        ```

* `plink_chr_suffix` (Type: Plink Fileset Prefix)

    * Full path to chromosome-separated plink files - everything after the chromosome number but before the extension

    * Corresponding Input File: Chr-Separated Plink Files

        * A group of plink file sets - one plink set for each chromosome in the analysis

        * Type: Plink Set

        * Format: plink binary

        * Input File Header:





        ```
        CHROM  POS     ID      REF     ALT     FILTER  INFO
        ```

* `plink_flag` (Type: String)

    * Either 
## Post-Processing


* `p_cutoff_summarize` (Type: Float)

    * P-Value Threshold for Summarizing Results at the End, arbitrary p-value threshold for creating a table of results combined with low p-values 

* `annotate` (Type: Bool (Java: true or false))

    * Whether or not to annotate results with the RSIDs and nearest genes for plotting and summary files.

* `plink2_col_names` (Type: Map (Dictionary))

    * Default Plink 2.0 column names mapped to new ones

* `biofilter_build` (Type: String)

    * The build to pass to biofilter - can be 19 or 38

* `biofilter_close_dist` (Type: Float)

    * The distance in bp for something to be considered “close” vs “far” with respect to nearest gene annotation. Value is often 5E4

* `biofilter_loki` (Type: File Path)

    * The path to a loki.db file to be used for nearest gene annotation

* `biofilter_script` (Type: File Path)

    * The path to the biofilter script to use. If using the singularity container, should be ‘/app/biofilter.py’
# Output Files from PLINK_2.0_GWAS


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

* GWAS QQ Plots

    * QQ plots for the GWAS results

    * Type: QQ Plot

    * Format: png

    * Parallel By: Cohort, Phenotype

* Plink 2.0 GWAS Top Hits Table

    * A FILTERED top hits csv summary file of results including cohort, phenotype, gene, group annotation, p-values, and other counts. One single summary file will be aggregated from all the “top hits” in each GWAS Summary Statistics file. The p-value threshold is specified by the user

    * Type: Summary Table

    * Format: csv
# Example Config File Contents


```
params {
    // default assumes use of the docker container
    my_python = "/opt/conda/bin/python"
    
    data_csv = "/path/to/data/cleaned_test_pheno_covars.csv"
    cohort_sets = "/path/to/data/Imputed_sample_table.csv"

    // default paths are for PMBB Imputed data
    plink_chr_prefix = "/path/to/data/PMBB-Release-2020-2.0_genetic_imputed-topmed-r2_chr"
    plink_chr_suffix = ""
    plink_flag = "--pfile"

    min_maf = 0.05
    max_missing_per_var = 0.05
    max_missing_per_sample = 0.05
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
        "AMR_ALL", "AMR_M", "AMR_F",
        "AFR_ALL", "AFR_F", "AFR_M",
        "EAS_ALL", "EAS_F", "EAS_M",
        "EUR_ALL", "EUR_F", "EUR_M",
        ]

    sex_strat_cohort_list = [
        "AMR_M", "AMR_F",
        "AFR_F", "AFR_M",
        "EAS_F", "EAS_M",
        "EUR_F", "EUR_M"
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
# Current Dockerfile for the Container/Image


```docker
FROM continuumio/miniconda3

WORKDIR /app

# biofilter version argument
ARG BIOFILTER_VERSION=2.4.3

RUN apt-get update \
    # install packages needed for PLINK, NEAT plots and biofilter installation
    && apt-get install -y --no-install-recommends libz-dev g++ gcc git wget tar unzip make \
    && rm -rf /var/lib/apt/lists/* \
    # install PLINK
    && wget https://s3.amazonaws.com/plink2-assets/alpha5/plink2_linux_x86_64_20240105.zip \
    && unzip plink2_linux_x86_64_20240105.zip \
    && rm -rf plink2_linux_x86_64_20240105.zip \
    # move plink2 executable to $PATH
    && mv plink2 /usr/bin \
    # install biofilter
    && wget https://github.com/RitchieLab/biofilter/releases/download/Biofilter-${BIOFILTER_VERSION}/biofilter-${BIOFILTER_VERSION}.tar.gz -O biofilter.tar.gz \
    && tar -zxvf biofilter.tar.gz --strip-components=1 -C /app/ \
    && /opt/conda/bin/python setup.py install \
    && chmod a+rx /app/biofilter.py \
    # install python packages needed for pipeline
    && conda install -y -n base -c conda-forge scikit-learn dominate wget libtiff conda-build scipy pandas seaborn matplotlib numpy apsw sqlite \
    && conda clean --all --yes \
    # install NEAT plots
    && git clone https://github.com/PMBB-Informatics-and-Genomics/NEAT-Plots.git \
    && mv NEAT-Plots/manhattan-plot/ /app/ \
    && conda develop /app/manhattan-plot/ \
    # remove NEAT-plots directory and biofilter tarball
    && rm -R NEAT-Plots biofilter.tar.gz

USER root

```
# Current `nextflow.config` contents


```
// set up profile to submit jobs to queue on LPC
// add -profile cluster to nextflow command to submit jobs to queue
profiles {

    standard {
        process.executor = awsbatch-or-lsf-or-slurm-etc
    }

    cluster {
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
}

includeConfig 'plink2_gwas.config'

```
# Advanced Nextflow Users: Take/Emit Info

## Output Channel (emit) Description


A Channel of three-part tuples with (cohort, phenotype, and path to summary stats file)