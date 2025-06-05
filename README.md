# surfinv
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
from surfinv import single_file_workflow
infile = 'C:/Users/sierra.brown/OneDrive - DOI/Documents/224_Surface_Inv.xlsx'
outfile = infile.split(infile.split('/')[-1])[0] + '224_Surface_Inv_Summ.csv'
single_file_workflow(infile, outfile)
```

OR, for batch workflow, where all the TAAMS pulls files for each LAC are located in `infolder`:
```
from surfinv import batch_workflow
infolder = 'C:/Users/sierra.brown/OneDrive - DOI/Documents/SurfaceInvTAAMSpulls/'
outfile = 'Surface_Inventory_Summ.csv'
batch_workflow(infolder, outfile)
```
### Output

The output of the script will be a `.csv` file that contains 5 columns:

#### Column 1: LAC
  - LAC as entered in TAAMS
    
#### Column 2: Tribal Acreage
  - Summation of acres of tracts within this LAC that have any percentage trust ownership and are 100% tribally owned

#### Column 3: Allotted Acreage
  - Summation of acres of tracts within this LAC that have any percentage trust ownership and are less than 100% tribally owned

#### Column 4: Trust Acreage
  - Summation of acres of tracts with _any_ trust ownership within this LAC
    
  **note**: This should always be equal to the sum of the two prior columns, (but is not directly calculated that way in the script) so if it is not, that is an indication that there may be an issue

#### Column 5: Trust Interest %
  - This is the decimal (out of 1.0) of the trust acreage in the LAC with trust ownership type. While all tracts with any trust ownership are considered part of trust acreage and are managed in trust, there can still be partial fee owners on those tracts. 

### Methodological Explanation:
The methdology for these surface acreage pulls was developed over the course of several months in consultation with representatives from several departments. There are multiple possible methodologies for calculating surface acreage based on the definitions chosen for various categories; no one way is necessarily "wrong" or "correct". This section explains the methods used _here_ so they can be understood and replicated.

#### Definitions:
**Surface Acerage**: Acres from tracts that have surface rights in trust. Any tracts which combine of surface rights with any form of mineral rights are also included.
**Trust Acreage**: Acres of tracts with any percentage trust ownership.
**Tribal Acreage**: Surface acres from tracts that contain 100% tribal ownership and have any percentage trust ownership.
**Allotted Acreage**: Surface acres from tracts that are less than 100% tribally owned and have any percentage trust ownership.

### The QLIK Query Explained

As explained above, the first step is to create a QLIK pull for the LAC(s) of interest with the columns in the following order:

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

The ordering is critical as the code expects a certain number of columns to be present and for each to contain specific information. The filtering is important to ensure we have captured the necessary information without including duplicates of any particular information. There is a step in this process through which there is a check applied to ensure that the interests represented sum to one for each tract. This ensures duplication or loss of information has not occurred. This will be covered in more detail below. First, let's explore each of the columns and their filters so there is an understanding of why they were chosen.

The _General - Land Area Code_ column allows the optional filtering to a specific land area code. QLIK has a limited number of rows it will output before it truncates the data and it is necessary to stay under that limit, LAC provides an opportunity to do that as the number of rows required to get all the information neeeded for this calculation expands quite quickly.

The _General - Tract Reference No._ allows distinction between each of the tracts having the interest calculated. It is important to use to be able to group the interests and ensure they are deliniated by tract. Testing was done to ensure that either Tract Reference No. or Tract ID could be used. Nationally, when limitting to only active tracts there is no difference in the number of records when using Tract ID vs. Tract Reference No. Here, we preferred Tract Reference No. as it is always a number and does not contain special characters like are sometimes in the Tract ID (like "-"), this allows more code flexibility without any loss of data. Again, testing has confirmed there is no difference in the final calculations when limiting to active tracts. If historical tracts are included this is not the case as there have been reused Tract IDs, however we limit to only active tracts later on in this pull (column 4) so that's not something we need to consider here (though if we did Tract Reference No. would likely be preferred as it's unlikley to be reused).

The _General - Acres_ tract is included because if you want to calculate a summation of acreage you'll need to know how many acres there are!

The _General - Inactivated Date_ is filtered to "0". This represents only active tracts. Inactive tracts should no longer be included in the summation of the acreage. Active tracts are those with an inactivated date set to 0.

The _General - Resource Code_ column is filtered to S, B, D, E, and F. S represents tracts that are only surface rights. B represents tracts that include both surface and mineral rights. D represents tracts that _also_ include both surface and mineral rights, but which have had the Oil and Gas rights separated out. E, similarly, represents tract that _also_ include both surface and minereal rights, but which have had the Coal right separated out. Note that D and E are the surface and remaining mineral rights represented in the tracts _not_ the separated out oil, gas, or coal rights themselves. F is tracts for which there is a specific note, sometimes this is separating out a different mineral right that is not represented elsewhere (like gravel), and would need to be handled separately per tract. This is a small source of error as we do not separately check each tract but simply include all F tracts. F tracts are relatively rare and we have determined the overall contribution is small enough to err on the side of inclusion rather than exclusion.

The _Ownership - Entity Type Code_ column designates the type of entity for which that interest fraction is designated. This is what we will use to determine if tracts are counted as allotted or tribal.

The _Ownership - Interest Type Code_ column is filtered to A, J, O, P, T, and V. These are all various types of interest code that specifically include the Title rights. Tract rights can be split into title and beneficial. If all interest type codes are included without filter, the portions that are split will be double counted in acreage. By filtering to just title this ensures there is no duplication in the amount of interest of a tract.

The _Ownership - Owner ID_ displays a number for each separate owner of a tract. We don't need this value in particular for the calculations we do, but it is necessary to ensure the QLIK query properly displays all relevant rows.

The _Ownership - Owner Interest Decimal_ is what tells us the fraction of a tract that is owned by this particular owner. The interest decimals for every tract in this pull should alwyas add to 1.00. This is checked in the code. If the tract does not add to 1.00 there is an issue, more on this below in the explanation of the steps of the script.

The _Ownership - Owner Seq. No_ is incredibly important. While a seemingly small change to the QLIK pull, it allows rows that would otherwise be virtually the same to show. The classic example of this is a tract that has been split into thirds all of which are owned by the same entity/Owner ID. In this case, without Seq. No. you'd see two rows in QLIK one with owner interest decimal 0.33 and another with owner interest decimal 0.34. That only adds to 0.67! Where is the other 0.33?! If you go into the title tract module for that tract you'll see there is no error being highlighted for a lack of recorded title, so why are they not being shown? The answer lies within how QLIK presents data. If two rows are otherwise identical QLIK treats them as a duplicate so they will not show the second row. Owner Seq. No. allows differentiation between the two shares that are both 0.33. When adding this column you'll find you have Owner Seq. No. 1, 2, and 3 and owner interest decimals: 0.33, 0.33, and 0.34. Now we can sum to 1.0 and know we have all interests represented. Without including this, due to initiative like Land Buy Back where small fractions were purchased from several sources, tribal interest in particular would be vastly underepresented in some tracts.

The _Ownership - Owner Type Code_ tells us if an interest is being held in trust, restricted fee, or fee. While a tract can be split between trust and another owner type interest, if any part of the tract is held in trust, the entire acreage is included as trust acreage (as explained above in the trust acreage definitions.

### The Code Calculations: A plain language walkthrough

Right, now that we've gotten a good understanding of the various QLIK columns and why they're included, let's move onto the process that this pull undergoes in the code to get to our end calcualtions of surface acreage. Note that this explanation is a walkthrough of what is happening "under the hood" with the code. A user does not need to interact with the majority of these functions at all and should refer to the the above "Example Usage" section for the execution instructions.

First, a function called `read_taams_pull` is executed which brings the data in the QLIK query into a format the python code can read. This is called a `pandas Dataframe`. The Dataframe is trimmed to only include the Tract Reference Number, Acres, Ownership Entity Type, Ownership Interest Decimal, and Ownership Type Code. The other fields, while important to ensuring the QLIK query contains all relevant data won't be necessary to calculate the acreage summations within the code. We also grab the LAC in this function so we can add it to the row output at the end. This function returns a tuple (a group of values) containing (1) the trimmed Dataframe with the relevant fields and (2) the lac.

Next, we take the trimmed Dataframe and we run a function called `check_sum_to_1` this function confirms that the owner interest demcials for each Tract Reference Number all add to 1.0 out to six decimal places. It returns a tuple containing (1) the number of tracts that do not sum to 1.0 and (2) The Tract Reference Numbers of the tracts that do not sum to 1.0. If the number of tracts that do not sum to 1.0 is great than 0 an exception is raised, the entire code stops running, and you will see the message `Error: Tracts included without sum to 1 title ownership; check TAAMS pull`. Now, in the even that this message occurs you can run the functions `read_taams_pull` followed by `check_sum_to_1` outside of the workflow codes and investigate the output of `check_sum_to_1` to find the tracts that are throwing these errors. Typically if there are many tracts the TAAMS pull itself has been incorrectly formatted. This may be because your columns are not in the same order as prescribed above, or that you did not include all the columns that were above, or perhaps an extra column. The other option is that the filters were not correctly applied. There is one last possibility: there may be a tract included in your pull that _actually_ doesn't sum to one in TAAMS for title interest. This is very very rare. Of the over 500 LACs that have been run using this code there was a single tract identified that fell into this category. The good news is that it is also very simple to check, if you look at that tract in the TAAMS title tract module you'll find there is a large yellow caution sign next to the title interest and the fraction will be below one. If you find this it is a good idea to notify the relevant LTRO so they can look into the issue and do a title search to repair it. However, because you don't want to have to wait to continue to your calculations on account of a single tract there is an override built into the code. Once you've confirmed you have a legimately "out of unity" tract you can use the `allow_error` keyword to your workflow function and that will change the accepted number of tracts that can not sum to 1 from zero to whatever value you input. Again, please note this is incredibly rare and the `allow_error` keyword should not be used lightly or without significant prior research and confirmation through TAAMS.

After clearing the sum to one check, the owners are combined on each tract in the function `combine_owners`. For these calculations we don't care about each separate ownership stake only the totals by certain categories. We combine them by entity type (e.g. tribal, indian, nonindian) and ownership type (e.g. Fee, Restricted Fee, Trust). Then, in `group_tracts_by_category`, we break the tracts out into three groups: tribal tracts, allotted tracts, and trust tracts (which will contain both tribal and allotted). The tribal tracts are broken out first. They are identified by those tracts with an entity type equal to `TRBE` and an ownership interest decimal equal to 1.0. This is only the 100% tribally owned tracts. Next, the trust tracts are grouped by identifying any tracts with the string "TRUST" as a part of the Ownner Type Code. Lastly, the allotted tracts are represented by any of the trust tracts that are not found in the list of tribal tracts. This means all trust tracts with partial tribal ownership are included as allotted as well trust tracts with government ownership, business ownership, or those that are fully owned by individuals. For all of these groups, there is one row per tract reference number to ensure there is no repeated acreage.

Finally, in `create_output_row` the values for acreage within each of those groups are summed. These values, along with the lac from `read_taams_pull` are the output of the code. When using `single_file_workflow` this can output as a small four column, one row Dataframe as described in the "Output" section above if you use the keyword `to_csv=False`. Otherwise, a one row, 5 column .csv file will be produced either named as you specify or with the pattern: `{name_of_input_TAAMS_pull}_output.csv`. In `batch_file_workflow` the only option is a .csv output which will similarly be 5 columns and follow the description in the "Output" section. The number of rows of data will be equal to the number of input TAAMS pulls in the folder that is pointed to. Note, the code will execute on all `.xlsx` files in the folder using the batch workflow, it is therefore inadvisable to run this code with a folder containing `.xlsx` files that are not properly formatted TAAMS pulls. This will cause errors.
