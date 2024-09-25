import pandas as pd
import argparse as ap

def make_arg_parser():
    parser = ap.ArgumentParser(description=".")
    
    parser.add_argument('-d', '--data', required=True, help='.csv Phenotype and covariate file')
    parser.add_argument('-c', '--cohort', required=True, help='Cohort to set up')
    parser.add_argument('-s', '--samples', required=True, help='.csv of cohort assignments')
    parser.add_argument('-i', '--id', required=True, help='Column with sample IDs')
    parser.add_argument('--plinkFam', required=True)

    return parser

args = make_arg_parser().parse_args()

id_col = args.id
cohort = args.cohort
plink_fam = args.plinkFam

data = pd.read_csv(args.data, index_col=id_col, dtype={id_col: str})
samples = pd.read_csv(args.samples, index_col=id_col, dtype={id_col: str})

print(data)
print(samples)

plink_fam = pd.read_table(plink_fam, header=None, comment='#', index_col=1, sep='\\s+', dtype={0: str, 1: str})

cohort_samples = samples.index[samples[cohort] == 1]
keep_samples = data.index.intersection(samples.index).intersection(plink_fam.index).intersection(cohort_samples)

data = data.loc[keep_samples]
plink_fam = plink_fam.loc[keep_samples]

if len(data) == 0:
    print(data)
    raise ValueError('No Samples Left - Check Cohort Table')

# The FIDs are usually either the IIDs duplicated or all 0
FIDs = plink_fam[0]
data.insert(0, 'IID', data.index)
if len(FIDs.unique()) == 1:
    data.insert(0, 'FID', 0)
else:
    data.insert(0, 'FID', data.index)

data.to_csv(f'{cohort}.plink2_pheno_covars.txt', sep='\t', index=False)
data[['FID', 'IID']].to_csv(f'{cohort}.sample_list.txt', sep=' ', index=False, header=False)

