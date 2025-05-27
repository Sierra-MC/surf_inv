from pandas import read_excel, concat
import pandas as pd
from pathlib import Path


def read_taams_pull(file):
    """Read in a properly formatted TAAMS pull as a pandas dataframe, trim the columns that we don't
    need to make the calculation (but were needed to make sure the proper data was pulled from TAAMS)."""
    path = Path(file)
    df = read_excel(path, names=['LAC', 'TractRefNo', 'Acres', 'InactiveDate',
                                 'Resource', 'EntityType', 'InterestType', 'OwnerID',
                                 'OwnerDec', 'OwnerSeqNo', 'OwnershipType'],)
    trimmed_df = df[['TractRefNo', 'Acres', 'EntityType', 'OwnerDec', 'OwnershipType']].copy()
    lac = df['LAC'][0]
    return trimmed_df, lac

def check_sum_to_1(df):
    """Checks that the ownership of all tracts sums to 1. This is a hard requirement in TAAMS, and it
    shouldn't ever happen that there is a tract without sum to 1 ownership. If there is we might be
    missing something in the TAAMS pull, or the columns were not in the order specified in the readme."""
    sum_by_id = df.groupby('TractRefNo', as_index=False)['OwnerDec'].sum()
    tracts_not_summing = sum_by_id[round(sum_by_id['OwnerDec'],6)!=1]
    return len(tracts_not_summing), tracts_not_summing

def combine_owners(df):
    """For these calculations we don't care about each separate ownership stake. Here we combine them by
    entity type (e.g. tribal, indian, nonindian) and ownership type (e.g. Fee, Restricted Fee, Trust)."""
    sum_by_refno = df.groupby(['TractRefNo', 'Acres', 'OwnershipType', 'EntityType'], as_index=False)['OwnerDec'].sum()
    return sum_by_refno

def group_tracts_by_category(df):
    """Groups a dataframe in to three dataframes. One with the tribally owned trust tracts, one with the
    allotted tracts, and one with all trust tracts. Note there can (and should) be overlap on which
    tracts are included in the trust dataframe and the other two."""
    df = combine_owners(df)
    tribal_tracts = df[df['EntityType']=='TRBE'][df['OwnerDec'] == 1.0]
    df_trust = df[df['OwnershipType'].str.contains('Trust')].groupby(['TractRefNo', 'Acres', 'OwnershipType'], as_index=False)['OwnerDec'].sum()
    allotted_tracts = df_trust[~df_trust['TractRefNo'].isin(tribal_tracts['TractRefNo'])].dropna()
    tribal_tracts = df_trust[df_trust['TractRefNo'].isin(tribal_tracts['TractRefNo'])].dropna()
    return tribal_tracts, allotted_tracts, df_trust

def create_output_row(tribal_tracts, allotted_tracts, df_trust):
    """Creates a single row output dataframe following the necessary format for the surface acreage
    inventory maps."""
    tribal_acres = tribal_tracts['Acres'].sum()
    allotted_acres = allotted_tracts['Acres'].sum()
    trust_acres = df_trust['Acres'].sum()
    trust_interest_perc = df_trust['OwnerDec'].sum() / len(df_trust)
    row = pd.DataFrame.from_dict({'Tribal Acreage': [tribal_acres],
                                'Allotted Acreage':  [allotted_acres],
                                'Trust Acreage': [trust_acres],
                                'Trust Interest %': [trust_interest_perc],
    })
    return row

def single_file_workflow(infile, outfile='', to_csv=True, allow_error=0):
    """Runs the entire workflow for a single TAAMS pull specified. If `to_csv` is True, an output csv
    is created; if it is False the output is returned as a single row pandas dataframe.
    The optional value `allow_error` is an integer value of the number of tracts that are allowed to
    have an ownership that is out of unity. This should normally always be set to zero (and is by
    default). If there are known tracts out of unity, notify the responsible LTRO, and use
    allow_error to set the number of tracts that are "allowed" to have the out of unity error without
    raising an error in the workflow."""
    df, lac = read_taams_pull(infile)
    ownership_issues, _ = check_sum_to_1(df)
    if ownership_issues > allow_error:
        raise Exception('Error: Tracts included without sum to 1 title ownership; check TAAMS pull')
    output = create_output_row(*group_tracts_by_category(df))
    output.insert(0, 'LAC', lac)
    if to_csv:
        if outfile == '':
            outfile = infile.split('.xlsx')[0] + '_output.csv'
        output.to_csv(Path(outfile), index=False)
    else:
        return output

def batch_workflow(infolder, outfile, allow_error=0):
    """Runs the entire workflow for all .xlsx files in a specified folder and outputs a single csv
    file with one row of output per input .xlsx file.
    The optional value `allow_error` is an integer value of the number of tracts that are allowed to
    have an ownership that is out of unity. This should normally always be set to zero (and is by
    default). If there are known tracts out of unity, notify the responsible LTRO, and use
    allow_error to set the number of tracts that are "allowed" to have the out of unity error without
    raising an error in the workflow.
    *Note*: this error allowance will be applied to all the files in the batch. It is recommended you
     run the offending file separately if the other files are not already known to comply with the
     sum to one constraint."""
    xlsx_lst = Path(infolder).glob('*.xlsx')
    output_dfs = []
    for file in xlsx_lst:
        acreage = single_file_workflow(file, to_csv=False, allow_error=allow_error)
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

