import pandas as pd
import datetime
import locale
import plotly.graph_objects as go
locale.setlocale(locale.LC_MONETARY, 'en-GB')
import os
import seaborn as sns
import matplotlib.pyplot as plt

#variables
direct = ['001 Bag In Box', '002 Bulk Wine', '004 Closures', '009 Glass', '013 Labels', '017 Outside Operations', '018 Packaging', '019 PET', '022 Raw Materials']

indirect = ['003 Catering', '005 Engineering', '006 Enviromental', '007 Estates', '008 Filtration Media', '010 HR', '011 Hygeine Chemicals', '012 IT & Comms',
            '014 Laboratory', '015 Material Handling', '016 Office Services', '020 Process Agents/Chemicals', '021 Professional Services', '023 Safety',
            '024 Sales & Marketing', '025 Security', '026 Site Services', '027 Subscriptions', '028 Training', '029 Travel', '030 Uniforms/Clothing',
            '031 Utilities & Gases', '032 Vehicles', '033 Warehouse & Distribution', '034 Waste', '035 Gov/Taxing Authority', '036 Insurance']

multi_site_supplier1 = ['supplier_site1', 'supplier_site2']


def top40():
    #top 40 indirects spend last month:
    indir_sup_lm = df_lm['Direct/Indirect']=='Indirect'
    df_indir_sup_lm = df_lm[indir_sup_lm]
    #Removes Marketing, HR, IT & Professional Services from the dataframe
    df_indir_sup_lm = df_indir_sup_lm[df_indir_sup_lm.Supplier_Type != '024 Sales & Marketing']
    df_indir_sup_lm = df_indir_sup_lm[df_indir_sup_lm.Supplier_Type != '010 HR']
    df_indir_sup_lm = df_indir_sup_lm[df_indir_sup_lm.Supplier_Type != '012 IT & Comms']
    df_indir_sup_lm = df_indir_sup_lm[df_indir_sup_lm.Supplier_Type != '021 Professional Services']

    #Add up spend by supplier and take top 40 spend
    top40_df = pd.DataFrame(df_indir_sup_lm.groupby('Supplier')['total_amount'].sum(level=0).nlargest(40)).reset_index()
  
    #seaborn barplot:
    x = top40_df['Supplier']
    y = top40_df['total_amount']
    sns.set_style('whitegrid')
    plt.figure(figsize=(12,8))
    indFig = sns.barplot(x, y,palette='GnBu_d')
    indFig.set(xlabel='Supplier', ylabel='Spend (£)')
    indFig.set_xticklabels(indFig.get_xticklabels(), rotation=45, horizontalalignment='right')
    #insert and format data labels:
    for p in indFig.patches:
        indFig.text(p.get_x() + p.get_width()/2.,p.get_height(),' £{:,.2f}'.format(p.get_height()),
                    fontsize=12, rotation=90, color='black', ha='center', va='bottom')
    plt.tight_layout()
    #plt.savefig(lastMonth.strftime("%B") + ' Spend - Top 40 indirect.pdf')
    
def monthSpend():
    monthSpend_df = pd.DataFrame(df_lm.groupby('Supplier')['total_amount'].sum(level=0)).reset_index()
    print(monthSpend_df)

def monthSpendbyCat():
    monthSpendCat_df = pd.DataFrame(df_lm.groupby('Supplier_Type')['total_amount'].sum(level=0).sort_values(ascending=False, kind='quicksort')).reset_index()
    monthSpendCat_formatted = monthSpendCat_df.copy()
    #format into currency
    monthSpendCat_formatted['total_amount'] = monthSpendCat_formatted['total_amount'].map('£{:,.2f}'.format)
    #plot graph
    x = monthSpendCat_df['Supplier_Type']
    y = monthSpendCat_df['total_amount']
    fig = go.Figure(data=[go.Bar(x=x, y=y)])
    fig.update_traces(marker_color='rgb(158,202,225)', marker_line_color='rgb(8,48,107)',
                      marker_line_width=0.2, opacity=0.9)
    fig.update_layout(title_text= lastMonth.strftime("%B") + ' Spend - by Category')
    fig.show()

    print(monthSpendCat_formatted.to_string(index=False))


if __name__=="__main__":
       
    topDir = os.getcwd()
    #read CSV
    spend_data = pd.read_csv(topDir + '\RSQL 8.2 Supplier Spend.csv')
    #import relevant csv columns as pandas dataframe:
    dfRaw = pd.DataFrame(spend_data, columns= ['Supplier_Code','Supplier','Taxable_Amount', 'Non_Taxable_Amount', 'total_amount', 'Supplier_Type', 'Direct/Indirect', 'Payment_Date'])

    #works out the previous month in the format yyyymm:
    today = datetime.date.today()
    first = today.replace(day=1)
    lastMonth = first - datetime.timedelta(days=1)
    lastMonthM = lastMonth.month    
    
    #removes the comma in the price and changes type to float so values can be added together:
    dfRaw['Taxable_Amount'] = dfRaw['Taxable_Amount'].str.replace(',', '')
    dfRaw['Taxable_Amount'] = dfRaw['Taxable_Amount'].astype(float)
    dfRaw['Non_Taxable_Amount'] = dfRaw['Non_Taxable_Amount'].str.replace(',', '')
    dfRaw['Non_Taxable_Amount'] = dfRaw['Non_Taxable_Amount'].astype(float)
    dfRaw['total_amount'] = dfRaw['Taxable_Amount']+dfRaw['Non_Taxable_Amount']

   
    #insert new column calculating if supplier is direct/indirect based on value of 'Supplier_Type' column:
    dfRaw.loc[dfRaw['Supplier_Type'].isin(direct), 'Direct/Indirect'] = 'Direct'
    dfRaw.loc[dfRaw['Supplier_Type'].isin(indirect), 'Direct/Indirect'] = 'Indirect'
    dfRaw.loc[dfRaw['Supplier_Type'] =='                             .', 'Direct/Indirect'] = 'Undefined'

    #convert the payment date in spend_data to month number:
    month_no = pd.to_datetime(dfRaw['Payment_Date'], format="%d/%m/%Y", errors='coerce') # 'coerce' rectified error in date conversion
    dfRaw['month_no'] = month_no.dt.month

    #create new dataframe with just the rows where payment date = last month
    lm = dfRaw['month_no']==lastMonthM
    df_lm = dfRaw[lm]
