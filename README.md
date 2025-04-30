# surf_inv
Scripts for BIA surface inventory calculations from TAAMS. No data included.

Requires a TAAMS QLIK pull with columns in the following order:

1. General - Land Area Code
2. General - Tract Reference No.
3. General - Acres
4. General - Inactivated Date (Filtered to just 0)
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
### Output

The output of the script will be a `.csv` file that contains 5 columns:

#### Column 1: LAC
  - LAC as entered in TAAMS
    
#### Column 2: Tribal Acreage
  - Summation of acres of tracts within this LAC that are 100% tribally owned

#### Column 3: Allotted Acreage
  - Summation of acres of tracts within this LAC that have any percentage trust ownership and are less than 100% tribally owned

#### Column 4: Trust Acreage
  - Summation of acres of tracts with _any_ trust ownership within this LAC (*note*: This should always be equal to the sum of the two prior columns, but is not directly calculated that way in the script so if it is not, that is an indication that there may be an issue)

#### Column 5: Trust Interest %
  - This is the % of the trust acreage in the LAC with trust ownership type. While all tracts with any trust ownership are considered part of trust acreage and are managed in trust, there can still be partial fee owners on those tracts. 
