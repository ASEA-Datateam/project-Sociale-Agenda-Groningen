# %%
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
import scipy as sp
import pyreadstat as prt

from openpyxl import workbook
from openpyxl.writer.excel import ExcelWriter
from openpyxl import load_workbook
import io


# %%
# Load data 13mnpl (and replace municipality names)
#achtergrond
columns_to_use = ['RINPERSOON',"huishoudnr_2021","leeftijd_2021","gem_2021","provincie_2021","typehh_2021"]
df_13 = pd.read_csv(r"H:\Analyse 082024\python basis bestanden\achtergrond_gem13.csv", delimiter=';',usecols=columns_to_use)
replacements = {1952:"Midden-Groningen", 1969:"Westerkwartier", 14:"Groningen Stad", 1730:"Tynaarlo", 1895:"Oldsambt",37:"Stadskanaal", 1699:"Noordenveld", 1979:"Eemsdelta", 1950:"Westerwolde", 1966:"Het Hogeland", 1680:"Aa en Hunze",47:"Veendam",765:"Pekela"}
df_13['gem_2021'] = df_13['gem_2021'].replace(replacements)

#SChuld
columns_to_use = ['RINPERSOON',"waardeeigwonbox1_2021","Smalle_schuld_2021","Smalle_schuld_huishouden_2021"]
df_schuld = pd.read_csv(r"H:\Analyse 082024\python basis bestanden\schulden_base.csv", delimiter=';',usecols=columns_to_use)



# %%
df_13

# %%
#Load GGZ an Income
columns_to_use = ['RINPERSOON',"belanginkbronhh_2021","inkpersprim_2021","inkhhbest_2021","basis_ggz_2021","special_ggz_2021"]
df_ggz_ink = pd.read_csv(r"H:\Analyse 082024\python basis bestanden\vraag2_nl.csv",delimiter=";", usecols=columns_to_use)

df_ggz_ink['gebruik_ggz'] = np.where((df_ggz_ink['basis_ggz_2021'] =='Ja') | (df_ggz_ink['special_ggz_2021'] =='Ja'),1,0)
df_ggz_ink['werk_binair'] = np.where((df_ggz_ink['inkpersprim_2021'] <= 0),0,1)



# %%
# Load NL dataset
columns_to_use = [
 'RINPERSOON',
 'waardeeigwonbox1_2021',
 'Smalle_schuld_2021',
 'Smalle_schuld_huishouden_2021',
 'huishoudnr_2021',
 'leeftijd_2021',
 'typehh_2021',
 'belanginkbronhh_2021',
 'inkhhbest_2021',
 'inkpersprim_2021',
 'basis_ggz_2021',
 'special_ggz_2021']

df_NL = pd.read_csv(r"H:\Analyse 082024\python basis bestanden\vraag2_nl.csv",delimiter=";", usecols=columns_to_use)
df_NL['gebruik_ggz'] = np.where((df_NL['basis_ggz_2021'] =='Ja') | (df_NL['special_ggz_2021'] =='Ja'), 1,0)
df_NL['werk_binair'] = np.where((df_NL['inkpersprim_2021'] <= 0),0,1)
df_NL['schuld_binair'] = df_NL['Smalle_schuld_2021'].replace({"Nee":0,"Ja":1})

bins = [18,24,34,44,54,64,float('inf')]
labels = ["18-24", "25-34", "35-44", "45-54"," 55-64","65+"]

df_NL['leeftijdscategorie'] = pd.cut(df_NL['leeftijd_2021'], bins=bins, labels=labels)

# %%
#Load onderwijs data
columns_to_use = ['RINPERSOON','hgopl_2021','typeonderwijs_2021','startkwalificatie_2021']
df_ow = pd.read_spss(r"G:\Maatwerk\STAPELINGSMONITOR_THEMA\STAPMON02Onderwijs\STAPMON02Onderwijs2021V1.sav", usecols=columns_to_use)
df_ow['RINPERSOON']= pd.to_numeric(df_ow['RINPERSOON'])
df_ow['startkwalificatie_binair'] = df_ow['startkwalificatie_2021'].replace({"Nee":0,"Ja":1})
df_ow['schoolgaand_binair'] = np.where((df_ow['typeonderwijs_2021'] == 'Volgt geen onderwijs'),0,1)
df_ow['startkwalificatie_binair'] = df_ow['startkwalificatie_binair'].astype(float)

# %%
#load uitkeringsdata
columns_to_use = [
 'RINPERSOON',
 'bijstand_pwet_2021',
 'bijstand_2021',
 'bijstandsduur_2021',
 ]
df_uitk = pd.read_spss(r"G:\Maatwerk\STAPELINGSMONITOR_THEMA\STAPMON08Uitkeringen\STAPMON08Uitkeringen2021V1.sav", usecols=columns_to_use)
df_uitk['RINPERSOON'] = pd.to_numeric(df_uitk['RINPERSOON'])

# %%
#Merge dataframes

#Merge debt and background data (13mnpl)
df_13_schuld = pd.merge(df_13,df_schuld,on="RINPERSOON",how='inner')
#add ggz and income data (13mnpl)
df_tot = pd.merge(df_13_schuld,df_ggz_ink,on='RINPERSOON',how='inner')
#add onderwijs data (13)
df_tot = pd.merge(df_tot,df_ow, on='RINPERSOON', how='inner')
#add uitkering data(13)
df_tot = pd.merge(df_tot,df_uitk, on='RINPERSOON', how='inner')
#add onderwijs to df_NL
df_NL = pd.merge(df_NL,df_ow,on='RINPERSOON',how='inner')
#add uitkering to df_NL
df_NL = pd.merge(df_NL,df_uitk,on='RINPERSOON',how='inner')

# %%
# Create age categories in df_tot

bins = [17,24,34,44,54,64,float('inf')]
labels = ["18-24", "25-34", "35-44", "45-54"," 55-64","65+"]

df_tot['leeftijdscategorie'] = pd.cut(df_tot['leeftijd_2021'], bins=bins, labels=labels)

# %%
#Create debt binary variable
df_tot['schuld_binair'] = df_tot['Smalle_schuld_2021'].replace({"Nee":0,"Ja":1})

# %%
#Per gemeente het aantal en aandeel mensen met een schuld
df_tot_schuld_stats_gemeente = df_tot.groupby('gem_2021').agg(totaal_inwoners=('schuld_binair','size'),inwoners_schuld=('schuld_binair','sum'))
df_tot_schuld_stats_gemeente['aandeel_schuld'] = (df_tot_schuld_stats_gemeente["inwoners_schuld"]/df_tot_schuld_stats_gemeente["totaal_inwoners"])

df_tot_schuld_stats_gemeente

# %%
#Per gemeente het aantal en aandeel mensen met een schuld
len(df_NL[df_NL['schuld_binair']==1])

# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    df_tot_schuld_stats_gemeente.to_excel(writer,sheet_name='schuld naar gemente', startrow=1,startcol=1,index=True,header=True)

# %%
# Aantal en aandeel mensen met schuld per leeftijdscategorie, totaal 13 gemeenten
df_tot_schuld_stats_leeftijd = df_tot.groupby('leeftijdscategorie').agg(totaal_in_categorie=('schuld_binair','size'),met_schuld_in_categorie=('schuld_binair','sum'))
df_tot_schuld_stats_leeftijd['aandeel_schuld'] = (df_tot_schuld_stats_leeftijd["met_schuld_in_categorie"]/df_tot_schuld_stats_leeftijd["totaal_in_categorie"])

df_tot_schuld_stats_leeftijd

# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    df_tot_schuld_stats_leeftijd.to_excel(writer,sheet_name='schuld naar leeftijd', startrow=1,startcol=1,index=True,header=True)

# %%
#Per gemeente het aantal en aandeel mensen met een schuld, per leeftijdscategorie
df_tot_schuld_stats_leeftijd_gemeente = df_tot.groupby(['gem_2021','leeftijdscategorie']).agg(totaal=('schuld_binair','size'),met_schuld=('schuld_binair','sum'))
df_tot_schuld_stats_leeftijd_gemeente['aandeel_schuld'] = (df_tot_schuld_stats_leeftijd_gemeente["met_schuld"]/df_tot_schuld_stats_leeftijd_gemeente["totaal"])

df_tot_schuld_stats_leeftijd_gemeente

# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    df_tot_schuld_stats_leeftijd_gemeente.to_excel(writer,sheet_name='schuld naar gemeente en leeftijd', startrow=1,startcol=1,index=True,header=True)

# %%
#Aantal en aandeel ggz voor heel NL en totaal 13 gemeenten.
print("Aantal met ggz (NL)", len(df_NL.loc[df_NL['gebruik_ggz']==1]))
print("Aandeel met GGZ (NL)", (len(df_NL.loc[df_NL['gebruik_ggz']==1])/len(df_NL)))

print("Aantal met ggz (13)", len(df_tot.loc[df_tot['gebruik_ggz']==1]))
print("Aandeel met GGZ (13)", (len(df_tot.loc[df_tot['gebruik_ggz']==1])/len(df_tot)))

# %%
# per gemeente het aantal en aandeel van mensen dat van ggz gebruik maakt
df_tot_ggz_gemeente = df_tot.groupby('gem_2021').agg(totaal_inwoners=('gebruik_ggz','size'),inwoners_ggz=('gebruik_ggz','sum'))
df_tot_ggz_gemeente['aandeel_ggz'] = (df_tot_ggz_gemeente["inwoners_ggz"]/df_tot_ggz_gemeente["totaal_inwoners"])

df_tot_ggz_gemeente

# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    df_tot_ggz_gemeente.to_excel(writer,sheet_name='ggz naar gemeente', startrow=1,startcol=1,index=True,header=True)

# %%
# per gemeente het aantal en aandeel van mensen met/zonder problematische schuld dat van ggz gebruik maakt
df_tot_ggz_gemeente_schuld = df_tot.groupby(['gem_2021','Smalle_schuld_2021']).agg(totaal_inwoners=('gebruik_ggz','size'),inwoners_ggz=('gebruik_ggz','sum'))
df_tot_ggz_gemeente_schuld['aandeel_ggz'] = (df_tot_ggz_gemeente_schuld["inwoners_ggz"]/df_tot_ggz_gemeente_schuld["totaal_inwoners"])

df_tot_ggz_gemeente_schuld

# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    df_tot_ggz_gemeente_schuld.to_excel(writer,sheet_name='ggz naar gemeente en schuld', startrow=1,startcol=1,index=True,header=True)

# %%
# Create inkomensgroepen in df_tot en df_NL
bins = [0,19999,39999,59999,79999,float('inf')]
labels = ["0 - 19.999","20.000-39.999","40.000-59.999","60.000-79.999","meer dan 80.000"]
df_NL['inkomensgroepen'] = pd.cut(df_NL['inkhhbest_2021'], bins=bins, labels=labels)
df_tot['inkomensgroepen'] = pd.cut(df_tot['inkhhbest_2021'], bins=bins, labels=labels)

# Create inkomensgroepen in df_tot en df_NL
bins = [0,21999,36499,float('inf')]
labels = ["0 - 21.999","22.000-36.499","meer dan 40.000"]
df_NL['inkomensgroepen_grof'] = pd.cut(df_NL['inkhhbest_2021'], bins=bins, labels=labels)
df_tot['inkomensgroepen_grof'] = pd.cut(df_tot['inkhhbest_2021'], bins=bins, labels=labels)

# %%
# Aantal en aandeel van mensen met wel/ geen problematische schulden dat in een bepaalde inkomenscategorie valt (hh) (heel Nederland)
df_NL_grouped = df_NL.dropna(subset=['inkomensgroepen']).groupby(["Smalle_schuld_2021","inkomensgroepen"]).size().reset_index(name='count')
total_counts = df_NL.dropna(subset=['inkomensgroepen']).groupby("Smalle_schuld_2021").size().reset_index(name='total')
merged = pd.merge(df_NL_grouped,total_counts,on='Smalle_schuld_2021')
merged['aandeel'] = (merged['count']/merged['total'])
merged

# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    merged.to_excel(writer,sheet_name='inkomensgroepen naar schuld (NL)', startrow=1,startcol=1,index=True,header=True)

# %%
# Aantal en aandeel van mensen met/zonder problematische schuld dat in een bepaalde inkomenscategorie (hh) valt (totaal 13 gemeenten).
grouped = df_tot.dropna(subset=['inkomensgroepen']).groupby(["Smalle_schuld_2021","inkomensgroepen"]).size().reset_index(name='count')
total_counts = df_tot.dropna(subset=['inkomensgroepen']).groupby("Smalle_schuld_2021").size().reset_index(name='total')
merged = pd.merge(grouped,total_counts,on='Smalle_schuld_2021')
merged['aandeel'] = (merged['count']/merged['total'])
merged

# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    merged.to_excel(writer,sheet_name='inkomensgroepen naar schuld (13)', startrow=1,startcol=1,index=True,header=True)

# %%
#Per gemeente het aantal en aandeel van de mensen met wel/ geen problematische schuld dat in een bepaalde inkomenscategorie (hh) valt.
grouped = df_tot.dropna(subset=['inkomensgroepen']).groupby(["gem_2021","Smalle_schuld_2021","inkomensgroepen"]).size().reset_index(name='count')
total_counts = df_tot.dropna(subset=['inkomensgroepen']).groupby(["gem_2021","Smalle_schuld_2021"]).size().reset_index(name='total')
merged = pd.merge(grouped,total_counts,on=['gem_2021','Smalle_schuld_2021'])
merged['aandeel'] = (merged['count']/merged['total'])
merged

# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    merged.to_excel(writer,sheet_name='inkomensgroepen naar gemeente en naar schuld (13)', startrow=1,startcol=1,index=True,header=True)

# %%
#Per gemeente het aantal en aandeel van de mensen met een problematische schuld dat in een bepaalde inkomenscategorie (hh) valt
grouped = df_tot.loc[df_tot['Smalle_schuld_2021']=="Ja"].dropna(subset=['inkomensgroepen']).groupby(["gem_2021","Smalle_schuld_2021","inkomensgroepen"]).size().reset_index(name='count')
total_counts = df_tot.loc[df_tot['Smalle_schuld_2021']=="Ja"].dropna(subset=['inkomensgroepen']).groupby(["gem_2021","Smalle_schuld_2021"]).size().reset_index(name='total')
merged = pd.merge(grouped,total_counts,on=['gem_2021','Smalle_schuld_2021'])
merged['aandeel'] = (merged['count']/merged['total'])
merged.drop(columns='Smalle_schuld_2021', inplace=True)
merged

# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    merged.to_excel(writer,sheet_name='inkomensgroepen naar gemeente en naar schuld (13)', startrow=1,startcol=9,index=True,header=True)

# %%
# per gemeente het aantal en aandeel van mensen met/zonder schuld dat ggz gebruikt
df_tot_ggz_gemeente = df_tot.groupby(['gem_2021','Smalle_schuld_2021']).agg(totaal_inwoners=('gebruik_ggz','size'),inwoners_ggz=('gebruik_ggz','sum'))
df_tot_ggz_gemeente['aandeel_ggz'] = (df_tot_ggz_gemeente["inwoners_ggz"]/df_tot_ggz_gemeente["totaal_inwoners"])

df_tot_ggz_gemeente

# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    df_tot_ggz_gemeente.to_excel(writer,sheet_name='ggz naar gemeente en naar schuld (13)', startrow=1,startcol=1,index=True,header=True)

# %%
#Create dataframe met jongeren
df_jong = df_tot.loc[df_tot['leeftijdscategorie']=='18-24']

# %%
# Per gemeente het aantal jongeren met een startkwalificatie
df_sk_stats = df_jong.groupby("gem_2021").agg(totaal=('startkwalificatie_binair','size'),aantal_sk=('startkwalificatie_binair','sum'))
df_sk_stats['aandeel'] = (df_sk_stats['aantal_sk']/df_sk_stats['totaal'])

df_sk_stats

# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    df_sk_stats.to_excel(writer,sheet_name='jongeren met sk naar gemeente (13)', startrow=1,startcol=1,index=True,header=True)

# %%
#Aantal en aandeel jongeren, per gemeente en met wel of niet een starkwalificatie, die werk/ problematische schuld hebben
df_gem_sk_stats = df_jong.groupby(["gem_2021","startkwalificatie_2021"]).agg(totaal=('RINPERSOON','size'),aantal_schuld=('schuld_binair','sum'),aantal_werk=('werk_binair','sum'))
df_gem_sk_stats['aandel_werk'] = (df_gem_sk_stats['aantal_werk']/df_gem_sk_stats['totaal'])
df_gem_sk_stats['aandeel_schuld'] = (df_gem_sk_stats['aantal_schuld']/df_gem_sk_stats['totaal'])

df_gem_sk_stats


# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    df_gem_sk_stats.to_excel(writer,sheet_name='werk en schulden jongeren (13)', startrow=1,startcol=1,index=True,header=True)

# %%
#Create Dataframe met jongeren die niet naar school gaan.
df_jong_niet_school = df_jong.loc[df_jong['schoolgaand_binair']==0]

# %%
# Aantal en aandeel niet schoolgaande jongeren met werk/schuld/startkwalificatie, per gemeente
df_gem_sk_stats = df_jong_niet_school.groupby(["gem_2021"]).agg(totaal=('RINPERSOON','size'),aantal_schuld=('schuld_binair','sum'),aantal_werk=('werk_binair','sum'),aantal_sk=('startkwalificatie_binair','sum'))
df_gem_sk_stats['aandel_werk'] = (df_gem_sk_stats['aantal_werk']/df_gem_sk_stats['totaal'])
df_gem_sk_stats['aandeel_schuld'] = (df_gem_sk_stats['aantal_schuld']/df_gem_sk_stats['totaal'])
df_gem_sk_stats['aandeel_sk'] = (df_gem_sk_stats['aantal_sk']/df_gem_sk_stats['totaal'])


df_gem_sk_stats


# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    df_gem_sk_stats.to_excel(writer,sheet_name='werk, schuld, sk, ns jongeren (13)', startrow=1,startcol=1,index=True,header=True)

# %%
# Aandeel mensen met/zonder problematische schuld in verschillende opleidingsniveaus, uitgesplitst naar gemeente
grouped = df_tot.loc[df_tot['hgopl_2021']!='Onbekend'].groupby(['gem_2021','Smalle_schuld_2021','hgopl_2021']).size().reset_index(name='aantal')
total_counts = df_tot.loc[df_tot['hgopl_2021']!='Onbekend'].groupby(['gem_2021','Smalle_schuld_2021']).size().reset_index(name='total')
merged = pd.merge(grouped,total_counts,on=['gem_2021','Smalle_schuld_2021'])
merged['aandeel'] = (merged['aantal']/merged['total'])
merged


# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    merged.to_excel(writer,sheet_name='opleidingsniveau naar gem en schuld (13)', startrow=1,startcol=1,index=True,header=True)

# %%
# Aandeel mensen met/zonder problematische schuld in verschillende opleidingsniveaus (heel NL)
grouped = df_NL.loc[df_NL['hgopl_2021']!='Onbekend'].groupby(['Smalle_schuld_2021',"hgopl_2021"]).size().reset_index(name='aantal')
total_counts = df_NL.loc[df_NL['hgopl_2021']!='Onbekend'].groupby(['Smalle_schuld_2021']).size().reset_index(name='totaal')
merged = pd.merge(grouped,total_counts,on=['Smalle_schuld_2021'])
merged['aandeel'] = (merged['aantal']/merged['totaal'])*100
merged = merged.iloc[[0,1,2,4,5,6]]
merged

# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    merged.to_excel(writer,sheet_name='opleidingsniveau naar schuld (NL)', startrow=1,startcol=1,index=True,header=True)

# %%
#Create dataframe with only people on welfare.
df_bijstand = df_tot.loc[df_tot['bijstand_pwet_2021']=='Ja']

# %%
#Aandeel bijstandsgerechtigden met problematishe schuld, per gemeente
df_bijstand_gem_schuld = df_bijstand.groupby('gem_2021').agg(totaal=('schuld_binair','size'), aantal_schuld=('schuld_binair','sum'))
df_bijstand_gem_schuld['aandeel'] = (df_bijstand_gem_schuld['aantal_schuld']/df_bijstand_gem_schuld['totaal'])
df_bijstand_gem_schuld

# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    df_bijstand_gem_schuld.to_excel(writer,sheet_name='bijstand en schuld naar gem', startrow=1,startcol=1,index=True,header=True)

# %%
# Aandeel bijstandsgerechtigden met problematische schuld (totaal 13 gemeenten)
(df_bijstand_gem_schuld['aantal_schuld'].sum()/df_bijstand_gem_schuld['totaal'].sum())

# %%
#Create bijstand_duur dataframe
df_bijstand_duur = df_bijstand.loc[(df_bijstand['bijstandsduur_2021']!="Nee of onbekend") & (df_bijstand['bijstandsduur_2021']!="Nee of onbekend")]
df_bijstand_duur['bijstandsduur_2021'] = pd.to_numeric(df_bijstand_duur['bijstandsduur_2021'], errors='coerce')
df_bijstand_duur["bijstand_+5_binair"] = np.where(df_bijstand_duur['bijstandsduur_2021']>=5,1,0)

# %%
#Aandeel bijstandsgerechtigden dat langer dan 5 jaar in de bijstand zit, per gemeente
df_bijstand_5 = df_bijstand_duur.dropna(subset='bijstandsduur_2021').groupby("gem_2021").agg(totaal=("bijstand_+5_binair",'size'),aantal_5plus=('bijstand_+5_binair','sum'))
df_bijstand_5['aandeel_5plus'] = (df_bijstand_5['aantal_5plus']/df_bijstand_5['totaal'])
df_bijstand_5

# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    df_bijstand_5.to_excel(writer,sheet_name='bijstand >5jaar per gemeente', startrow=1,startcol=1,index=True,header=True)

# %%
df_tot['schuld_hh'] = df_tot.groupby('huishoudnr_2021')["schuld_binair"].transform("max")
df_hh = df_tot.drop_duplicates(subset='huishoudnr_2021')
df_hh = df_hh.loc[df_hh['typehh_2021']<7]
replacements = {1:"Eenpersoons",2:"Paar zonder kinderen",3:"Paar zonder kinderen",4:"Paar met kinderen",5:"Paar met kinderen",6:"Alleenstaand met kind"}

df_hh['typehh_2021'] = df_hh['typehh_2021'].replace(replacements)

# %%
#Per gemeente het aantal en aandeel van de mensen met wel/ geen problematische schuld dat in een bepaalde inkomenscategorie (hh) valt.
grouped = df_hh.dropna().groupby(["typehh_2021","schuld_hh","inkomensgroepen_grof"]).size().reset_index(name='count')
total_counts = df_hh.dropna().groupby(["typehh_2021","schuld_hh"]).size().reset_index(name='total')
merged = pd.merge(grouped,total_counts,on=["typehh_2021","schuld_hh"])
merged['aandeel'] = (merged['count']/merged['total'])
merged

# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    merged.to_excel(writer,sheet_name='typhh_ink_schuld_tot', startrow=1,startcol=1,index=True,header=True)

# %%
#Per gemeente het aantal en aandeel van de mensen met wel/ geen problematische schuld dat in een bepaalde inkomenscategorie (hh) valt.
grouped = df_hh.dropna().groupby(["gem_2021","schuld_hh","typehh_2021"]).size().reset_index(name='count')
total_counts = df_hh.dropna().groupby(["gem_2021","schuld_hh"]).size().reset_index(name='total')
merged = pd.merge(grouped,total_counts,on=["gem_2021","schuld_hh"])
merged['aandeel'] = (merged['count']/merged['total'])
merged

# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    merged.to_excel(writer,sheet_name='gem_typhh_schuld', startrow=1,startcol=1,index=True,header=True)

# %%
#van mensen met schuld welk type hushoudens
grouped = df_hh[df_hh['schuld_hh']==1].dropna().groupby(["gem_2021","typehh_2021"]).size().reset_index(name='count')
total_counts = df_hh[df_hh['schuld_hh']==1].dropna().groupby(["gem_2021"]).size().reset_index(name='total')
merged = pd.merge(grouped,total_counts,on=["gem_2021"])
merged['aandeel'] = (merged['count']/merged['total'])
merged

# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    merged.to_excel(writer,sheet_name='metschuld_gem_typhh', startrow=1,startcol=1,index=True,header=True)

# %%
df_NL['schuld_hh'] = df_NL.groupby('huishoudnr_2021')["schuld_binair"].transform("max")

df_hh_NL = df_NL.drop_duplicates(subset='huishoudnr_2021')
df_hh_NL = df_hh_NL.loc[df_hh_NL['typehh_2021']<7]
replacements = {1:"Eenpersoons",2:"Paar zonder kinderen",3:"Paar zonder kinderen",4:"Paar met kinderen",5:"Paar met kinderen",6:"Alleenstaand met kind"}

df_hh_NL['typehh_2021'] = df_hh_NL['typehh_2021'].replace(replacements)

# %%
#Per gemeente het aantal en aandeel van de mensen met wel/ geen problematische schuld dat in een bepaalde inkomenscategorie (hh) valt.
grouped = df_hh_NL.dropna().groupby(["schuld_hh","typehh_2021"]).size().reset_index(name='count')
total_counts = df_hh_NL.dropna().groupby(["schuld_hh"]).size().reset_index(name='total')
merged = pd.merge(grouped,total_counts,on=["schuld_hh"])
merged['aandeel'] = (merged['count']/merged['total'])
merged

# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    merged.to_excel(writer,sheet_name='NL_schuld_typhh', startrow=1,startcol=1,index=True,header=True)

# %%
grouped = df_hh_NL.dropna().groupby(["schuld_hh","typehh_2021","inkomensgroepen_grof"]).size().reset_index(name='count')
total_counts = df_hh_NL.dropna().groupby(["schuld_hh","typehh_2021"]).size().reset_index(name='total')
merged = pd.merge(grouped,total_counts,on=["schuld_hh","typehh_2021"])
merged['aandeel'] = (merged['count']/merged['total'])
merged

# %%
with pd.ExcelWriter('Groningen.xlsx',engine='openpyxl',mode='a', if_sheet_exists='overlay') as writer:
    merged.to_excel(writer,sheet_name='NL_schuld_typhh_ink', startrow=1,startcol=1,index=True,header=True)


