# surf_inv
Scripts for BIA surface inventory calculations from TAAMS. No data included.

Requires a TAAMS QLIK pull with columns in the following order:

1. General - Land Area Code
2. General - Tract Reference No.
3. General - Acres
4. General - Inactived Date (Filtered to just 0)
5. General - Resource Code (Filtered to B, S, D, E, and F)
6. Ownership - Entity Type Code
7. Ownership - Interest Type Code (Filtered to A, J, O, P, T, and V)
8. Ownership - Owner ID
9. Ownership - Owner Interest Decimal
10. Ownership - Owner Seq. No.
11. Ownership - Owner Type Code

It is critical that the column order and filtering is correctly applied.

### Example Usage:
First the conda environment needs to be activated and the python shell needs to be started:
```
conda activate surfinv
python
```

To create surface inventory table for a single LAC:
```
from surf_inv import single_file_workflow
infile = 'C:/Users/sierra.brown/OneDrive - DOI/Documents/224_Surface_Inv.xlsx'
outfile = infile.split(infile.split('/')[-1])[0] + '224_Surface_Inv_Summ.csv'
single_file_workflow(infile, outfile)
```

OR, for batch workflow, where all the TAAMS pulls files for each LAC are located in `infolder`:
```
from surf_inv import batch_workflow
infolder = 'C:/Users/sierra.brown/OneDrive - DOI/Documents/SurfaceInvTAAMSpulls/'
outfile = 'Surface_Inventory_Summ.csv'
batch_workflow(infolder, outfile)
```