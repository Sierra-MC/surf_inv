from pandas import read_excel, concat, DataFrame
from pathlib import Path

from pandas.core.interchange.dataframe_protocol import DataFrame


def read_taams_pull(file):
    path = Path(file)
    df = read_excel(path, names=['LAC', 'TractRefNo', 'Acres', 'InactiveDate',
                                 'Resource', 'EntityType', 'InterestType', 'OwnerID',
                                 'OwnerDec', 'OwnerSeqNo', 'OwnershipType'],)
    trimmed_df = df[['TractRefNo', 'Acres', 'EntityType', 'OwnerDec', 'OwnershipType']].copy()
    lac = df['LAC'][0]
    return trimmed_df, lac

def check_sum_to_1(df):
    sum_by_id = df.groupby('TractRefNo', as_index=False)['OwnerDec'].sum()
    tracts_not_summing = sum_by_id[round(sum_by_id['OwnerDec'],6)!=1]
    return len(tracts_not_summing), tracts_not_summing

def combine_owners(df):
    sum_by_refno = df.groupby(['TractRefNo', 'Acres', 'OwnershipType', 'EntityType'], as_index=False)['OwnerDec'].sum()
    return sum_by_refno

def group_tracts_by_category(df):
    df = combine_owners(df)
    tribal_tracts = df[df['EntityType']=='TRBE'][df['OwnerDec'] == 1.0]
    df_trust = df[df['OwnershipType'] == 'T-Trust'].groupby(['TractRefNo', 'Acres', 'OwnershipType'], as_index=False)['OwnerDec'].sum()
    allotted_tracts = df_trust[~df_trust.isin(tribal_tracts)].dropna()
    return tribal_tracts, allotted_tracts, df_trust

def create_output_row(tribal_tracts, allotted_tracts, df_trust):
    tribal_acres = tribal_tracts['Acres'].sum()
    allotted_acres = allotted_tracts['Acres'].sum()
    trust_acres = df_trust['Acres'].sum()
    trust_interest_perc = df_trust['OwnerDec'].sum() / len(df_trust)
    row = DataFrame.from_dict({'Tribal Acreage': tribal_acres,
                                'Allotted Acreage':  allotted_acres,
                                'Trust Acreage': trust_acres,
                                'Trust Interest %': trust_interest_perc
    })
    return row

def single_file_workflow(infile, outfile, to_csv=True):
    df, lac = read_taams_pull(infile)
    ownership_issues, _ = check_sum_to_1(df)
    if ownership_issues > 0:
        return 'Error: Tracts included without sum to 1 title ownership; check TAAMS pull'
    output = create_output_row(*group_tracts_by_category(df))
    output.insert(0, 'LAC', lac)
    if to_csv:
        output.to_csv(Path(outfile))
    else:
        return output

def batch_workflow(infolder, outfile):
    xlsx_lst = Path(infolder).glob('*.xlsx')
    output_dfs = []
    for file in xlsx_lst:
        acreage = single_file_workflow(file, outfile, to_csv=False)
        output_dfs.append(acreage)
    full_acreage_df = concat(output_dfs)
    outpath = Path(infolder + outfile + '.csv')
    full_acreage_df.to_csv(outpath)


# Example Usage:
# infile = 'C:/Users/sierra.brown/OneDrive - DOI/Documents/224_Surface_Inv.xlsx'
# outfile = infile.split(infile.split('/')[-1])[0] + '224_Surface_Inv_Summ.csv'
# single_file_workflow(infile, outfile)
# OR, for batch workflow:
# infolder = 'C:/Users/sierra.brown/OneDrive - DOI/Documents/SurfaceInvTAAMSpulls/'
# outfile = 'Surface_Inventory_Summ.csv'
# batch_workflow(infolder, outfile)

