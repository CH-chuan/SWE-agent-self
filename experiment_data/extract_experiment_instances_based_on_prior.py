import pandas as pd

# Login using e.g. `huggingface-cli login` to access this dataset
df = pd.read_parquet("hf://datasets/princeton-nlp/SWE-bench_Verified/data/test-00000-of-00001.parquet")

columns_to_use = [
    'instance_id',
    'repo',
    'difficulty',
]

df = df[columns_to_use]

#print(df.head())

# # count by repo and difficulty
# vcs = df[['repo', 'difficulty']].value_counts()
# # sort by repo
# vcs = vcs.sort_index(level=0)
# print(vcs)


# check difficulty counts
# count by difficulty
difficulty_counts = df['difficulty'].value_counts()
print(difficulty_counts)
# difficulty
# 15 min - 1 hour    261
# <15 min fix        194
# 1-4 hours           42
# >4 hours             3


print(df[df['difficulty'] == '>4 hours']) # one of them can be solved by claude3.7, but for other models, all cannot be solved, so do not include any
# Name: count, dtype: int64
#                 instance_id               repo difficulty
# 316      pydata__xarray-6992      pydata/xarray   >4 hours
# 392  sphinx-doc__sphinx-7590  sphinx-doc/sphinx   >4 hours
# 441       sympy__sympy-13878        sympy/sympy   >4 hours

last_selection_df1 = pd.read_csv("experiment_data/15instances_3level/experiment_instances_new.csv")
last_selection_df2 = pd.read_csv("experiment_data/20randominstances_4level/experiment_instances.csv")

last_selection_dfs = pd.concat([last_selection_df1, last_selection_df2])
last_selection_dfs = last_selection_dfs.drop_duplicates()

# print(last_selection_dfs.difficulty.value_counts())
# difficulty
# 15 min - 1 hour    13
# <15 min fix         9
# 1-4 hours           5
# >4 hours            1
# Name: count, dtype: int64

prior_instance_ids = set(last_selection_dfs['instance_id'].tolist())

# remove instances in df that are in prior_instance_ids
df = df[~df['instance_id'].isin(prior_instance_ids)]

# now, sample 1 from <15 min fix and 5 from 1-4 hours
df_sampled_15min = df[df['difficulty'] == '<15 min fix'].sample(n=1, random_state=42)
df_sampled_1to4hours = df[df['difficulty'] == '1-4 hours'].sample(n=5, random_state=42)

# concatenate the samples
df_sampled = pd.concat([df_sampled_15min, df_sampled_1to4hours, last_selection_dfs])

# drop difficulty == 15 min - 1 hour and >4 hours
df_sampled = df_sampled[df_sampled['difficulty'] != '15 min - 1 hour']
df_sampled = df_sampled[df_sampled['difficulty'] != '>4 hours']

# sort by difficulty
df_sampled = df_sampled.sort_values(by='difficulty')

# reset the index
df_sampled = df_sampled.reset_index(drop=True)

print(df_sampled.difficulty.value_counts())

# save the sampled dataframe to a csv file
df_sampled.to_csv("experiment_data/20intances_2level/experiment_instances.csv", index=False)

# extract the instance ids
instance_ids = df_sampled['instance_id'].tolist()

# convert instance_ids to a regex format, meaning only matches with the instance_ids inside, e.g. ^(matplotlib__matplotlib-24149|sympy__sympy-17630)$
instance_ids_regex = '^(' + '|'.join(instance_ids) + ')$'
# save as a txt file
with open("experiment_data/20intances_2level/experiment_instance_ids.txt", "w") as f:
    f.write(instance_ids_regex)