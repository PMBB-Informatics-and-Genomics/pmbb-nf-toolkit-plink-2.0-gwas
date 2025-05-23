nextflow.enable.dsl = 2

// Using this space to set some default parameter values
// Setting these defaults helps to avoid any Errors due to null/undefined values
// These values are overwritten when defined in the .config file as well
params.putAll([
    min_bin_cases: 50,
    min_quant_n: 500,
    bin_pheno_list: [],
    quant_pheno_list: [],
    cohort_list: [],
    sex_strat_cohort_list: [],
    chromosome_list: [21, 22]
])

MIN_BIN_CASES = params.min_bin_cases
MIN_QUANT_N = params.min_quant_n

log.info """\
    NEXTFLOW - DSL2 - PLINK 2.0 GWAS - P I P E L I N E
    ==================================================
    run as                  : ${workflow.commandLine}
    run location            : ${launchDir}
    started at              : ${workflow.start}
    python exe              : ${params.my_python}

    Cohorts, Phenotypes, and Chromosomes
    ==================================================
    cohort_list             : ${params.cohort_list}
    bin_pheno_list          : ${params.bin_pheno_list}
    quant_pheno_list        : ${params.quant_pheno_list}
    chromosome_list         : ${params.chromosome_list}

    Input Output
    ==================================================
    pheno_covar_file        : ${params.data_csv}
    cohort_sample_file      : ${params.cohort_sets}
    plink_prefix            : ${params.plink_chr_prefix}
    plink_suffix            : ${params.plink_chr_suffix}
    plink_flag              : ${params.plink_flag}

    Plink GWAS QC
    ==================================================
    min_bin_cases           : ${MIN_BIN_CASES}
    min_quant_n             : ${MIN_QUANT_N}
    min_maf                 : ${params.min_maf}
    max_missing_per_variant : ${params.max_missing_per_var}
    min_hardy_p_value       : ${params.hwe_min_pvalue}

    Output Parameters
    ==================================================
    p-value filter          : ${params.p_cutoff_summarize}
    column name map         : ${params.plink2_col_names}

    """.stripIndent()

workflow {
    // Channel with tuples of (cohort, phenotype, sumstats file)
    cohort_pheno_sumstats = PLINK2_GWAS()
}

def paramToList(param) {
    // Function to check if parameter is a file or list
    if (param instanceof List) {
        // If the parameter is a list, return list
        return param
    } else if (param instanceof String && new File(param).exists()) {
        // If the parameter is a file, read the file contents into a list
        def listFromFile = new File(param).readLines()
        return listFromFile
    // return param.text.readLines()
    } else {
        // Handle cases where the parameter is neither a list nor a valid file
        // throw new IllegalArgumentException("Parameter must be a list or an existing file")
        return param
    }
}

include { BIOFILTER_POSITIONS } from './biofilter_wrapper.nf'

workflow PLINK2_GWAS {
    main:
        cohort = Channel.fromList(params.cohort_list)
        bin_pheno_list = paramToList(params.bin_pheno_list)
        quant_pheno_list = paramToList(params.quant_pheno_list)

        bin_pheno = Channel.fromList(bin_pheno_list)
        quant_pheno = Channel.fromList(quant_pheno_list)

        chromosome = Channel.fromList(params.chromosome_list)
        plink_suffixes_list = params.plink_flag == '--bfile' ? ['.bed', '.bim', '.fam'] : ['.pgen', '.pvar', '.psam']

        cohort_setup_script = "${moduleDir}/scripts/set_up_cohort_directory.py"
        standardize_pheno_script = "${moduleDir}/scripts/standardize_phenos.py"
        pheno_table_script = "${moduleDir}/scripts/make_pheno_summary_table.py"
        pheno_covar_plots_script = "${moduleDir}/scripts/make_pheno_covar_summary_plots.py"
        merge_plink2_script = "${moduleDir}/scripts/merge_and_filter_plink2_results.py"
        plotting_script = "${moduleDir}/scripts/make_manhattan_qq_plots.py"
        report_script = "${moduleDir}/scripts/generate_plink_reports.py"

        pheno_covar_table = "${params.data_csv}"
        cohort_table = "${params.cohort_sets}"
        related_file = params.related_list == null ? [] : "${params.related_list}"

        plink_fam = "${params.plink_chr_prefix}${params.chromosome_list.get(0)}${params.plink_chr_suffix}${plink_suffixes_list.get(2)}"
        cohort_tables_samples = set_up_cohort(
            cohort, cohort_setup_script,
            pheno_covar_table,
            cohort_table,
            plink_fam,
            related_file
        )
        standardized_pheno_files = standardize_phenos(cohort_tables_samples, standardize_pheno_script)

        // make pheno summary table, conditionally handle empty phenotype lists
        pheno_table = make_pheno_summaries(
                cohort.collect(),
                (bin_pheno_list.size() == 0)  ? '[]' : bin_pheno.toSortedList(),
                (quant_pheno_list.size() == 0) ? '[]' : quant_pheno.toSortedList(),
                plink_fam,
                pheno_covar_table, cohort_table,
                pheno_table_script
                )
        pheno_plots = make_pheno_covar_summary_plots(
                cohort.collect(),
                (bin_pheno_list.size() == 0)  ? '[]' : bin_pheno.toSortedList(),
                (quant_pheno_list.size() == 0) ? '[]' : quant_pheno.toSortedList(),
                plink_fam,
                pheno_covar_table, cohort_table,
                pheno_covar_plots_script
                )

        // parse the pheno-cohort summary table
        pheno_table_filename = "${launchDir}/Summary/pheno_summaries.csv"
        // parse the pheno-cohort summary table
        all_pheno_table_lines = parse_pheno_summary_table(pheno_table, pheno_table_filename)
        num_combos = params.cohort_list.size() * (bin_pheno_list.size() + quant_pheno_list.size())
        num_channel = Channel.fromList(1..num_combos)
        lines_with_num = num_channel.combine(all_pheno_table_lines)
        pheno_table_info = lines_with_num.map { i, all_lines ->
            all_lines.get(i) // Use i not i-1 because 0 is the header row
        }

        bin_pheno_info = pheno_table_info.filter { row -> bin_pheno_list.contains(row.get(1)) }
        quant_pheno_info = pheno_table_info.filter { row -> quant_pheno_list.contains(row.get(1)) }

        // sex-specific pheno handling
        sex_pheno_list = params.sex_specific_pheno_file == null ? [] : (new File(params.sex_specific_pheno_file)).readLines()

        // Filter out combinations with too few cases
        // For binary, must have MIN_BIN_CASES cases
        // For quantitative, must have MIN_QUANT_N samples
        cohort_bin_pheno_case_ct = bin_pheno_info.map { row -> new Tuple(row.get(0), row.get(1), row.get(4) == '' ? 0 : row.get(4).toDouble()) }
        keep_cohort_bin_pheno_combos = cohort_bin_pheno_case_ct.filter { cohort, pheno, cases -> cases >= MIN_BIN_CASES } \
            .map { cohort, pheno, cases -> new Tuple(cohort, pheno) } \
            .filter {
                // sex-specific pheno handling
                // if the pheno is not in sex-specific list, keep it
                // OR if it IS in the list AND the cohort is in sex-stratified list, keep it
                cohort, pheno -> !sex_pheno_list.contains(pheno) || \
                (sex_pheno_list.contains(pheno) && params.sex_strat_cohort_list.contains(cohort))
            }
        cohort_quant_pheno_ct = quant_pheno_info.map { row -> new Tuple(row.get(0), row.get(1), row.get(2) == '' ? 0 : row.get(2).toDouble()) }
        keep_cohort_quant_pheno_combos = cohort_quant_pheno_ct.filter { cohort, pheno, count -> count >= MIN_QUANT_N } \
            .map { cohort, pheno, count -> new Tuple(cohort, pheno) } \
            .filter {
                // sex-specific pheno handling
                // if the pheno is not in sex-specific list, keep it
                // OR if it IS in the list AND the cohort is in sex-stratified list, keep it
                cohort, pheno -> !sex_pheno_list.contains(pheno) || \
                (sex_pheno_list.contains(pheno) && params.sex_strat_cohort_list.contains(cohort))
            }

        gwas_bin_pheno_data = standardized_pheno_files.combine(bin_pheno).combine(chromosome).map { cohort, data, samples, pheno, chr -> new Tuple(cohort, pheno, chr, data, samples) }
        gwas_bin_pheno_data = gwas_bin_pheno_data.join(keep_cohort_bin_pheno_combos.combine(chromosome), by: [0, 1, 2])
        gwas_bin_pheno_all_input = gwas_bin_pheno_data.map { cohort, pheno, chr, data, samples ->
            new Tuple(cohort, pheno, chr, data, samples, plink_suffixes_list.collect {
                ext -> "${params.plink_chr_prefix}${chr}${params.plink_chr_suffix}${ext}"
            },
            "${params.plink_chr_prefix}${chr}${params.plink_chr_suffix}".tokenize('/').last()
            )
        }

        gwas_bin_results_by_chr = call_plink2_logistic(gwas_bin_pheno_all_input)

        gwas_quant_pheno_data = standardized_pheno_files.combine(quant_pheno).combine(chromosome).map { cohort, data, samples, pheno, chr -> new Tuple(cohort, pheno, chr, data, samples) }
        gwas_quant_pheno_data = gwas_quant_pheno_data.join(keep_cohort_quant_pheno_combos.combine(chromosome), by: [0, 1, 2])
        gwas_quant_pheno_all_input = gwas_quant_pheno_data.map { cohort, pheno, chr, data, samples ->
            new Tuple(cohort, pheno, chr, data, samples, plink_suffixes_list.collect {
                ext -> "${params.plink_chr_prefix}${chr}${params.plink_chr_suffix}${ext}"
            },
            "${params.plink_chr_prefix}${chr}${params.plink_chr_suffix}".tokenize('/').last()
            )
        }

        gwas_quant_results_by_chr = call_plink2_linear(gwas_quant_pheno_all_input)

        all_gwas_results_by_chr = gwas_bin_results_by_chr.concat(gwas_quant_results_by_chr)
        all_gwas_results_grouped = all_gwas_results_by_chr.groupTuple(by: [0, 1], size: params.chromosome_list.size())

        (merged_sumstats, filtered_sumstats) = merge_and_filter_plink2_output(all_gwas_results_grouped, merge_plink2_script, params.p_cutoff_summarize, params.plink2_col_names)

        // take filtered output on a journey through BioFilter
        // plots and report post-processing
        // tuple val(cohort), val(pheno), path("${pheno}.plink2.gz")
        // tuple val(cohort), val(pheno), path("${pheno}.filtered.plink2.gz")

        filtered_sumstats_list = filtered_sumstats.map { cohort, pheno, sumstats -> sumstats }.collect()
        if (params['annotate']) {
            biofilter_input = make_biofilter_positions_input(filtered_sumstats_list)
            bf_input_channel = Channel.of('plink_stats').combine(biofilter_input)
            biofilter_annots = BIOFILTER_POSITIONS(bf_input_channel)
            manhattan_qq_plots = plot_plink_results_with_annot(merged_sumstats.combine(biofilter_annots), plotting_script)
            top_hit_table = make_summary_table_with_annot(filtered_sumstats_list, biofilter_annots)
        }
        else {
            manhattan_qq_plots = plot_plink_results(merged_sumstats, plotting_script)
            top_hit_table = make_summary_table(filtered_sumstats_list)
        }
        // tuple val(cohort), val(pheno), path("${pheno}.plink2.gz")
        // tuple val(cohort), val(pheno), path("${pheno}.filtered.plink2.gz")

        // make results manifest
        // results_manifest = collect_plot_files(pheno_table)

        // Collect a list of plots and phenotypes
        all_plots = pheno_plots.concat(manhattan_qq_plots).collect()
        all_phenos = quant_pheno_list + bin_pheno_list

        // Use the reporting script to generate a .zip folder
        // Containing HTML and source files
        make_results_report(
            all_plots,
            top_hit_table,
            report_script,
            all_phenos,
            params.cohort_list
        )

    emit:
        merged_sumstats
        pheno_table
}

process set_up_cohort {
    publishDir "${launchDir}/${cohort}/"
    machineType 'n2-standard-4'

    input:
        val cohort
        path cohort_script
        path pheno_covar_table
        path cohort_table
        path plink_fam
        path remove_relateds
    output:
        tuple val(cohort), path("${cohort}.plink2_pheno_covars.txt"), path("${cohort}.sample_list.txt")
    shell:
        """
        ${params.my_python} ${cohort_script} \
          --data ${pheno_covar_table} \
          --cohort ${cohort} \
          --samples ${cohort_table} \
          ${params.related_list == null ? '' : '--remove ' + remove_relateds} \
          --plinkFam ${plink_fam} \
          --id ${params.id_col}
        """
}

process make_pheno_summaries {
    publishDir "${launchDir}/Summary/"
    machineType 'n2-standard-4'

    input:
        val cohort_list
        val bin_pheno_list
        val quant_pheno_list
        path plink_fam
        path pheno_covar_table
        path cohort_table

        path(pheno_table_script)
    output:
        path('pheno_summaries.csv')

    shell:
        """
        ${params.my_python} ${pheno_table_script} \
          -c ${cohort_list.join(' ')} \
          -b ${bin_pheno_list.join(' ')} \
          -q ${quant_pheno_list.join(' ')} \
          --plinkFam ${plink_fam} \
          --data ${pheno_covar_table} \
          --samples ${cohort_table} \
          --id ${params.id_col}
        """
}

process parse_pheno_summary_table {
    machineType 'n2-standard-4'

    cache false
    input:
        path pheno_table_file // this is the appropriate path object
        val pheno_table_string // for executing Groovy code, must be val not path
    output:
        val list_of_info_lists
    script:
        exist_checks = 0
        sleep_interval = 100 // milliseconds
        max_sleep = 10 * 1000 // 10 seconds

        current_sleep = 0
        while (exist_checks < 3 && current_sleep <= max_sleep) {
            if (file(pheno_table_string).exists()) {
                exist_checks += 1
            }
            sleep(sleep_interval)
            current_sleep += sleep_interval
        }

        not_empty_checks = 0
        current_sleep = 0
        while (not_empty_checks < 3 && current_sleep <= max_sleep) {
            if ((new File(pheno_table_string)).empty()) {
                not_empty_checks += 1
            }
            sleep(sleep_interval)
            current_sleep += sleep_interval
        }

        assert file(pheno_table_string).exists() && !(new File(pheno_table_string)).empty() : 'File System Latency Issues. Please Try Re-Running'

        pheno_table_lines = (new File(pheno_table_string)).readLines()
        info_row_lists = []
        pheno_table_lines.each {
            line ->
            line_parts = line.toString().trim().replace('[', '').replace(']', '').split(',') as List
            info_row_lists.add(line_parts)
        }
        list_of_info_lists = [info_row_lists]

        '''
        echo "done"
        '''
}

process make_pheno_covar_summary_plots {
    publishDir "${launchDir}/Plots/"
    machineType 'n2-standard-4'

    input:
        val cohort_list
        val bin_pheno_list
        val quant_pheno_list
        path plink_fam
        path pheno_covar_table
        path cohort_table

        path(pheno_covar_plots_script)
    output:
        path('*.png')
    shell:
        """
        ${params.my_python} ${pheno_covar_plots_script} \
          -c ${cohort_list.join(' ')} \
          -b ${bin_pheno_list.join(' ')} \
          -q ${quant_pheno_list.join(' ')} \
          --plinkFam ${plink_fam} \
          --data ${pheno_covar_table} \
          --samples ${cohort_table} \
          --id ${params.id_col}
        """
    stub:
        '''
        touch stub_plot.png
        '''
}

process standardize_phenos {
    //this process will standardize or normalize the raw phenoptype and covariates files
    publishDir "${launchDir}/${cohort}/"
    machineType 'n2-standard-4'

    input:
        tuple val(cohort), path(pheno_covar_file), path(sample_list)
        path standardize_phenos_script
    output:
        tuple val(cohort), path("${cohort}.plink2_pheno_covars_standardized.tsv"), path(sample_list)

    script:
    """
        ${params.my_python} ${standardize_phenos_script} \
          -c ${cohort} \
          -p ${pheno_covar_file} \
          -s ${sample_list}
    """
    stub:
        """
        touch ${cohort}.plink2_pheno_covars_standardized.tsv
        """
}

String get_covar_list_args(String cohort, cohort_cat_covars, cohort_cont_covars) {
    String output = ''

    if (cohort_cont_covars.size() > 0 || cohort_cat_covars.size() > 0) {
        output += '--covar-name '
        if (cohort_cont_covars.size() > 0) {
            output += cohort_cont_covars.join(',')
        }
        if (cohort_cat_covars.size() > 0) {
            output += ',' + cohort_cat_covars.join(',') + ' '
        }
        else {
            output += ' '
        }
    }

    return output
}

process call_plink2_logistic {
    publishDir "${launchDir}/${cohort}/GWAS_Plink/"
    machineType 'n2-standard-4'

    //this process will perform association test with logistic regression
    input:
        tuple val(cohort), val(pheno), val(chromosome), path(pheno_covar), path(sample_list), path(plink_set), val(plink_prefix)
    output:
        tuple  val(cohort), val(pheno), val(chromosome), path("${cohort}.${pheno}.${chromosome}.glm.logistic.hybrid")
    script:
        covariate_args = get_covar_list_args(cohort,
            params.sex_strat_cohort_list.contains(cohort) ? params.sex_strat_cat_covars : params.cat_covars,
            params.sex_strat_cohort_list.contains(cohort) ? params.sex_strat_cont_covars : params.cont_covars)
        """

        plink2 --glm hide-covar firth-fallback cols=+a1freq,+a1freqcc,+firth \
            --ci 0.95 \
            --keep ${sample_list} \
            --maf ${params.min_maf} \
            --geno ${params.max_missing_per_var} \
            --hwe ${params.hwe_min_pvalue} \
            ${params.plink_flag} ${plink_prefix} \
            --pheno ${pheno_covar} \
            --pheno-name ${pheno} \
            --covar ${pheno_covar} \
            ${covariate_args} \
            --out ${cohort}.${pheno}.${chromosome}

        mv ${cohort}.${pheno}.${chromosome}.${pheno}.glm.logistic.hybrid ${cohort}.${pheno}.${chromosome}.glm.logistic.hybrid

        """
    stub:
        """
        touch ${cohort}.${pheno}.${chromosome}.glm.logistic.hybrid
        """
}

process call_plink2_linear {
    publishDir "${launchDir}/${cohort}/GWAS_Plink/"
    machineType 'n2-standard-4'

    //this process will perform association test with logistic regression
    input:
        tuple val(cohort), val(pheno), val(chromosome), path(pheno_covar), path(sample_list), path(plink_set), val(plink_prefix)
    output:
        tuple  val(cohort), val(pheno), val(chromosome), path("${cohort}.${pheno}.${chromosome}.glm.linear")
    script:
        covariate_args = get_covar_list_args(cohort,
            params.sex_strat_cohort_list.contains(cohort) ? params.sex_strat_cat_covars : params.cat_covars,
            params.sex_strat_cohort_list.contains(cohort) ? params.sex_strat_cont_covars : params.cont_covars)
        """
        plink2 --glm hide-covar cols=+a1freq \
            --ci 0.95 \
            --keep ${sample_list} \
            --maf ${params.min_maf} \
            --geno ${params.max_missing_per_var} \
            --hwe ${params.hwe_min_pvalue} \
            ${params.plink_flag} ${plink_prefix} \
            --pheno ${pheno_covar} \
            --pheno-name ${pheno} \
            --covar ${pheno_covar} \
            ${covariate_args} \
            --out ${cohort}.${pheno}.${chromosome}

        mv ${cohort}.${pheno}.${chromosome}.${pheno}.glm.linear ${cohort}.${pheno}.${chromosome}.glm.linear
        """
    stub:
        """
        touch ${cohort}.${pheno}.${chromosome}.glm.linear
        """
}

process merge_and_filter_plink2_output {
    publishDir "${launchDir}/${cohort}/Sumstats/"
    machineType 'n2-standard-4'

    input:
        // variables
        tuple val(cohort), val(pheno), val(chr_list), path(chr_inputs)
        path merge_plink2_script
        val pvalue_cutoff
        val column_names
    output:
        tuple val(cohort), val(pheno), path("${cohort}.${pheno}.plink2.gz")
        tuple val(cohort), val(pheno), path("${cohort}.${pheno}.filtered.plink2.csv")
    shell:
        """
        echo "${column_names.collect().join('\n')}" > colnames.txt
        cat colnames.txt
        ${params.my_python} ${merge_plink2_script} \
          -p ${pheno} \
          -c colnames.txt \
          -s ${chr_inputs.join(' ')} \
          --pvalue ${pvalue_cutoff} \
          --cohort ${cohort}
        """
    stub:
        """
        touch ${cohort}.${pheno}.plink2.gz
        touch ${cohort}.${pheno}.filtered.plink2.csv
        """
}

process make_biofilter_positions_input {
    publishDir "${launchDir}/Annotations/"
    machineType 'n2-standard-4'

    input:
        path(filtered_sumstats, stageAs: '?/*')
    output:
        path('plink2_gwas_biofilter_input_positions.txt')
    shell:
        """
        #! ${params.my_python}
        import pandas as pd

        dfs = []
        input_list = '${filtered_sumstats.join(' ')}'.split()
        id_col = '${params.plink2_col_names['ID']}'
        chr_col = '${params.plink2_col_names['#CHROM']}'
        pos_col = '${params.plink2_col_names['POS']}'

        for f in input_list:
            dfs.append(pd.read_csv(f))
        all = pd.concat(dfs)
        keep_cols = [chr_col, id_col, pos_col]
        all[keep_cols].to_csv('plink2_gwas_biofilter_input_positions.txt', header=False, index=False, sep=' ')
        """
    stub:
        '''
        touch plink2_gwas_biofilter_input_positions.txt
        '''
}

process plot_plink_results_with_annot {
    publishDir "${launchDir}/Plots/"
    machineType 'n2-standard-4'

    input:
        tuple val(cohort), val(pheno), path(sumstats), val(data_nickname), path(biofilter_annots)
        path(plotting_script)
    output:
        path "${cohort}.${pheno}.{manhattan.png,qq.png,qq.csv}"
    shell:
        """
        echo "${params.plink2_col_names.collect().join('\n')}" > colnames.txt
        cat colnames.txt

        ${params.my_python} ${plotting_script} \
          --pheno ${pheno} \
          --cohort ${cohort} \
          --colnames colnames.txt \
          --sumstats ${sumstats} \
          --annot ${biofilter_annots}
        """
    stub:
        """
        touch ${cohort}.${pheno}.manhattan.png
        touch ${cohort}.${pheno}.qq.png
        touch ${cohort}.${pheno}.qq.csv
        """
}

process plot_plink_results {
    publishDir "${launchDir}/Plots/"
    machineType 'n2-standard-4'

    input:
        tuple val(cohort), val(pheno), path(sumstats)
        path(plotting_script)
    output:
        path "${cohort}.${pheno}.{manhattan.png,qq.png,qq.csv}"
    shell:
        """
        echo "${params.plink2_col_names.collect().join('\n')}" > colnames.txt
        cat colnames.txt

        ${params.my_python} ${plotting_script} \
          --pheno ${pheno} \
          --colnames colnames.txt \
          --cohort ${cohort} \
          --sumstats ${sumstats}
        """
    stub:
        """
        touch ${cohort}.${pheno}.manhattan.png
        touch ${cohort}.${pheno}.qq.png
        touch ${cohort}.${pheno}.qq.csv
        """
}

process make_summary_table {
    publishDir "${launchDir}/Summary/"
    machineType 'n2-standard-4'

    input:
        path(all_filtered_sumstats, stageAs: '?/*')
    output:
        path('plink2_all_suggestive.csv')
    script:
        """
        #! ${params.my_python}

        import pandas as pd
        dfs = []
        input_list = '${all_filtered_sumstats.join(' ')}'.split()
        output = "plink2_all_suggestive.csv"
        id_col = '${params.plink2_col_names['ID']}'
        chr_col = '${params.plink2_col_names['#CHROM']}'
        pos_col = '${params.plink2_col_names['POS']}'

        for f in input_list:
            dfs.append(pd.read_csv(f))

        pd.concat(dfs).sort_values(by=[chr_col,pos_col,id_col]).to_csv(output, index=False)
        """
    stub:
        '''
        touch plink2_all_suggestive.csv
        '''
}

// Make top hits summary table with RSIDs and nearest genes
process make_summary_table_with_annot {
    publishDir "${launchDir}/Summary/"
    machineType 'n2-standard-4'

    input:
        path(all_filtered_sumstats, stageAs: '?/*')
        tuple val(data_nickname), path(biofilter_annots)
    output:
        path('plink2_all_suggestive.csv')
    script:
        """
        #! ${params.my_python}

        import pandas as pd
        dfs = []
        input_list = '${all_filtered_sumstats.join(' ')}'.split()
        output = "plink2_all_suggestive.csv"

        id_col = '${params.plink2_col_names['ID']}'
        chr_col = '${params.plink2_col_names['#CHROM']}'
        pos_col = '${params.plink2_col_names['POS']}'

        for f in input_list:
            dfs.append(pd.read_csv(f))

        all_gwas = pd.concat(dfs).sort_values(by=[chr_col,pos_col,id_col])

        annot_df = pd.read_csv('${biofilter_annots}', index_col='Var_ID')
        all_gwas[['Gene', 'RSID']] = annot_df.loc[all_gwas[id_col], ['Gene', 'RSID']].values

        all_gwas.to_csv(output, index=False)
        """
    stub:
        '''
        touch plink2_all_suggestive.csv
        '''
}

process collect_plot_files {
    publishDir "${launchDir}/Summary/"
    machineType 'n2-standard-4'

    input:
        path(pheno_table)
    output:
        path('results_manifest.csv')
    script:
        """
        #! ${params.my_python}

        import pandas as pd
        def plots_filename(row):
            barplot = f"Plots/{row['PHENO']}.barplots.png"
            violinplot = f"Plots/{row['PHENO']}.violinplot.png"
            manhattanplot = f"Plots/{row['COHORT']}.{row['PHENO']}.manhattan.png"
            qqplot = f"Plots/{row['COHORT']}.{row['PHENO']}.qq.png"
            resultsfile = f"{row['COHORT']}/Sumstats/{row['COHORT']}.{row['PHENO']}.filtered.plink2.csv"
            return (barplot, violinplot, manhattanplot, qqplot, resultsfile)

        pheno_table = pd.read_csv('${pheno_table}')
        pheno_table[['pheno_bar_plot', 'pheno_violin_plot', 'manhattan_plot', 'qq_plot', 'results_file']] = pheno_table.apply(lambda row: plots_filename(row), axis=1,result_type='expand')
        pheno_table.to_csv('results_manifest.csv',index=False)
        """
    stub:
        '''
        touch results_manifest.csv
        '''
}

process make_results_report {
    publishDir "${launchDir}", mode: 'copy'
    machineType 'n2-standard-4'
    
    input:
        path all_plots, stageAs: 'Plots/*'
        path top_hits_table
        path report_script
        val all_pheno_list
        val all_cohort_list
    output:
        path('Plink_2.0_GWAS_Report.tar.gz')
    shell:
        """
        ${params.my_python} ${report_script} \
            --phenotypes ${all_pheno_list.join(' ')} \
            --cohorts ${all_cohort_list.join(' ')} \
            --top_hits_csv ${top_hits_table} \
            --output_dir Plink_2.0_GWAS_Report

        tar -czvf Plink_2.0_GWAS_Report.tar.gz Plink_2.0_GWAS_Report/
        """
    stub:
        '''
        touch Plink_2.0_GWAS_Report.tar.gz
        '''
}
