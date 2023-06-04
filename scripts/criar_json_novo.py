import pandas as pd

# montagem do dataframe para produção de plástico global por ano desde 1950
# lê o arquivo csv
df0 = pd.read_csv('../data/csv/global-plastics-production.csv')
# retira a coluna 'code'
df0 = df0.drop(columns=['code'])
# deixa como inteiro a coluna ano
df0['year'] = df0['year'].astype('int')
# salva um json
df0.to_json('../data/json/global-plastics-production.json', orient='records')


# produção por tipo
df1 = pd.read_csv('../data/csv/global-plastics-prod-by-type.csv')
df1['year'] = df1['year'].astype('int')
df1.to_json('../data/json/global-plastics-prod-by-type.json', orient='records')
# monta por década
group = df1['year']//10*10  # como décadas
df1 = df1.groupby([group, 'type_of_plastic']).value.sum().reset_index(name="value")
df1.to_json('../data/json/global-plastics-prod-by-type-decade.json', orient='records')


# para que usamos todo esse plástico
df2 = pd.read_csv('../data/csv/global-plastics-prod-by-application.csv')
# muda o modo da tabela de wide para long
df2 = df2.melt(id_vars=["plastics_applications"], var_name="year", value_name="weight")
# retira o 'Total' da coluna 'plastics_applications'
df2.drop(df2[df2.plastics_applications == 'Total'].index, inplace=True)
# renomeia as colunas para 'from', 'to', 'weight'
df2.rename(columns={'plastics_applications': 'to', 'year': 'from', 'value': 'weight'}, inplace=True)
# renomeia 'Other', 'Marine Coatings' e 'Road Marking' para incluir 'Applications'
df2.loc[df2['to'] == 'Other', 'to'] = 'Other Applications'
df2.loc[df2['to'] == 'Marine coatings', 'to'] = 'Marine Coatings Applications'
df2.loc[df2['to'] == 'Road marking', 'to'] = 'Road Marking Applications'
# deixa como inteiro a coluna to (anos)
df2['from'] = df2['from'].astype('int')
# agrupa por década
group2 = df2['from']//10*10  # como décadas
df2 = df2.groupby([group2, 'to']).weight.sum().reset_index(name="weight")
# altera a ordem das colunas
df2 = df2.reindex(columns=['from', 'to', 'weight'])

# pega a produção por polímero para juntar com a produção por aplicação
df3 = pd.read_csv('../data/csv/global-plastics-prod-by-polymer.csv')
# wide to long
df3 = df3.melt(id_vars=["polymer"], var_name="year", value_name="weight")
# agrupa por tipo de polímero e depois por ano
df3 = df3.groupby(['polymer', 'year']).weight.sum().reset_index(name="weight")
# retira o total da coluna polymer
df3.drop(df3[df3.polymer == 'Total'].index, inplace=True)
# renomeia as colunas para 'from', 'to', 'weight' mas de modo inverso ao do dataframe df2
df3.rename(columns={'year': 'to', 'polymer': 'from'}, inplace=True)
# renomeia other para other polymers
df3.loc[df3['from'] == 'Other', 'from'] = 'Other Polymers'
# deixa como inteiro a coluna to (anos)
df3['to'] = df3['to'].astype('int')
# agrupa por década
group3 = df3['to']//10*10  # como décadas
df3 = df3.groupby([group3, 'from']).weight.sum().reset_index(name="weight")
# altera a ordem das colunas
df3 = df3.reindex(columns=['from', 'to', 'weight'])

# concatena df2 e df3
link = pd.concat([df2, df3], axis=0)
# resetar o index do dataframe que fica repetido ao fazer a concatenação (deleta e recria)
link.reset_index(drop=True, inplace=True)

# salva json por década
link.to_json('../data/json/global-plastics-prod-by-app-and-polymer-dec.json', orient='records')


# consumo por país
df4 = pd.read_csv('../data/csv/global-plastics-prod-by-region.csv')
# apaga coluna group e subgroup que não iremos utilizar
df4 = df4.drop('group', axis=1)
df4 = df4.drop('subgroup', axis=1)
# wide to long
df4 = df4.melt(id_vars=["country"], var_name="year", value_name="value")
# deixa como inteiro a coluna to (anos)
df4['year'] = df4['year'].astype('int')
# agrupa por década
group4 = df4['year']//10*10  # como décadas
df4 = df4.groupby([group4, 'country']).value.sum().reset_index(name="value")
# calcula porcentagem, primeiro cria um dataframe para cada decada e depois faz a soma e porcentagem
# por fim une os dataframes em um só
# eu não sei fazer de outro jeito :(
df41 = df4.loc[(df4['year'] == 1990), ['year', 'country', 'value']]
df42 = df4.loc[(df4['year'] == 2000), ['year', 'country', 'value']]
df43 = df4.loc[(df4['year'] == 2010), ['year', 'country', 'value']]

df41['percent'] = (df41['value'] / df41['value'].sum()) * 100
df42['percent'] = (df42['value'] / df42['value'].sum()) * 100
df43['percent'] = (df43['value'] / df43['value'].sum()) * 100

df4_final = pd.concat([df41, df42, df43], axis=0)
# salva
df4_final.to_json('../data/json/global-plastics-prod-by-region-dec.json', orient='records')

# montagem dataframe descarte por país/região - Total
df5 = pd.read_csv('../data/csv/plastic-waste-by-region-and-end-of-life-fate-All.csv')
# wide to long
df5 = df5.melt(id_vars=["group", "subgroup", "country", "waste type"], var_name="year", value_name="value")
grupo = sorted(set(df5['group']))
subgrupo = sorted(set(df5['subgroup']))
country = sorted(set(df5['country']))
type = sorted(set(df5['waste type']))
year = sorted(set(df5['year']))
# novamente pra não perder tempo procurando alguma solução fiz esse loop infinito...
# pelo menos resolve o problema
lista = []
for ix, i in enumerate(grupo):
    dicionario = {}
    dicionario['id'] = 'g_' + str(ix)
    dicionario['name'] = i
    lista.append(dicionario)
    for jx, j in enumerate(subgrupo):
        dicionario = {}
        dicionario['id'] = 's_' + str(jx)
        dicionario['name'] = j
        dicionario['parent'] = 'g_' + str(ix)
        lista.append(dicionario)
        for xx, x in enumerate(country):
            dicionario = {}
            dicionario['id'] = 'c_' + str(xx)
            dicionario['name'] = x
            dicionario['parent'] = 's_' + str(jx)
            lista.append(dicionario)
            for yx, y in enumerate(type):
                dicionario = {}
                dicionario['id'] = 't_' + str(yx)
                dicionario['name'] = y
                dicionario['parent'] = 'c_' + str(xx)
                lista.append(dicionario)
                for zx, z in enumerate(year):
                    dicionario = {}
                    dicionario['id'] = 'y_' + str(zx)
                    dicionario['name'] = z
                    dicionario['parent'] = 't_' + str(yx)
                    lista.append(dicionario)
                    for w in range(0, len(df5)):
                        dicionario = {}
                        dicionario['name'] = 'value'
                        dicionario['parent'] = z
                        dicionario['value'] = df5.loc[
                            (df5['group'] == i) & (df5['subgroup'] == j) & (df5['country'] == x) &
                            (df5['waste type'] == y) & (df5['year'] == z), 'value'
                        ].item()
                        print(dicionario)
                        # lista.append(dicionario)