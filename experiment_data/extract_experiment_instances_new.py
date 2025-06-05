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


# so finally, sample 10 from 15 min - 1 hour, 5 from < 15 min, 10 from 1-4 hours



# randomly sampe 13 from 15 min - 1 hour, 9 from < 15 min, 2 from 1-4 horus, and 1 from > 4 hours
# intotal 25 samples

# # sample 13 from 15 min - 1 hour
# df_15_min_to_1_hour = df[df['difficulty'] == '15 min - 1 hour'].sample(n=13, random_state=42)
# # sample 9 from < 15 min
# df_less_than_15_min = df[df['difficulty'] == '<15 min fix'].sample(n=9, random_state=42)
# # sample 2 from 1-4 hours
# df_1_to_4_hours = df[df['difficulty'] == '1-4 hours'].sample(n=2, random_state=42)
# # sample 1 from > 4 hours
# df_greater_than_4_hours = df[df['difficulty'] == '>4 hours'].sample(n=1, random_state=42)
# # concatenate the samples
# df_sampled = pd.concat([df_15_min_to_1_hour, df_less_than_15_min, df_1_to_4_hours, df_greater_than_4_hours])
# # reset the index
# df_sampled = df_sampled.reset_index(drop=True)
# # save the sampled dataframe to a csv file
# df_sampled.to_csv("data/experiment_instances.csv", index=False)

# # extract the instance ids
# instance_ids = df_sampled['instance_id'].tolist()

# # convert instance_ids to a regex format, meaning only matches with the instance_ids inside, e.g. ^(matplotlib__matplotlib-24149|sympy__sympy-17630)$
# instance_ids_regex = '^(' + '|'.join(instance_ids) + ')$'
# # save as a txt file
# with open("data/experiment_instance_ids.txt", "w") as f:
#     f.write(instance_ids_regex)