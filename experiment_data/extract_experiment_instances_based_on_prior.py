import pandas as pd
import os

# Login using e.g. `huggingface-cli login` to access this dataset
df = pd.read_parquet("hf://datasets/princeton-nlp/SWE-bench_Verified/data/test-00000-of-00001.parquet")

columns_to_use = [
    'instance_id',
    'repo',
    'difficulty',
    'problem_statement'
]

df = df[columns_to_use]

def url_in_problem_statement(problem_statement):
    not_count_content = [
"""
<!-- Please be sure to check out our contributing guidelines,
https://github.com/astropy/astropy/blob/main/CONTRIBUTING.md .
Please be sure to check out our code of conduct,
https://github.com/astropy/astropy/blob/main/CODE_OF_CONDUCT.md . -->
""",
"""
<!-- Please check that the development version still produces the same bug.
You can install development version with
pip install git+https://github.com/astropy/astropy
command. -->
"""
    ]
    # strip the problem_statement
    problem_statement = problem_statement.strip()
    # remove the not_count_content from the problem_statement
    for content in not_count_content:
        problem_statement = problem_statement.replace(content.strip(), '')
    # check if url is in the problem_statement
    if 'https://' in problem_statement or 'http://' in problem_statement:
        return True
    return False

df['url_in_problem_statement'] = df['problem_statement'].apply(url_in_problem_statement)
# remove instances with url in problem statement
df = df[~df['url_in_problem_statement']]
instances_with_url = df[df['url_in_problem_statement']].instance_id.tolist()
# drop problem_statement and url_in_problem_statement
df = df.drop(columns=['problem_statement', 'url_in_problem_statement'])

#print(df.head())

# # count by repo and difficulty
# vcs = df[['repo', 'difficulty']].value_counts()
# # sort by repo
# vcs = vcs.sort_index(level=0)
# print(vcs)


# check difficulty counts
# count by difficulty
difficulty_counts = df['difficulty'].value_counts()
# print(difficulty_counts)
# difficulty
# 15 min - 1 hour    261
# <15 min fix        194
# 1-4 hours           42
# >4 hours             3


# print(df[df['difficulty'] == '>4 hours']) # one of them can be solved by claude3.7, but for other models, all cannot be solved, so do not include any
# Name: count, dtype: int64
#                 instance_id               repo difficulty
# 316      pydata__xarray-6992      pydata/xarray   >4 hours
# 392  sphinx-doc__sphinx-7590  sphinx-doc/sphinx   >4 hours
# 441       sympy__sympy-13878        sympy/sympy   >4 hours

last_selection_df1 = pd.read_csv("experiment_data/15instances_3level/experiment_instances_new.csv")
last_selection_df2 = pd.read_csv("experiment_data/20randominstances_4level/experiment_instances.csv")
last_selection_df3 = pd.read_csv("experiment_data/20intances_2level_old/experiment_instances.csv")

last_selection_dfs = pd.concat([last_selection_df1, last_selection_df2, last_selection_df3])
last_selection_dfs = last_selection_dfs.drop_duplicates()

# only keep lawful prior instances, i.e. <15 min fix and 5 from 1-4 hours
last_selection_dfs = last_selection_dfs[(last_selection_dfs['difficulty'] == '<15 min fix') | (last_selection_dfs['difficulty'] == '1-4 hours')]

def create_sample_with_prior_instances(to_remove, last_selection_dfs, df):
    # Remove specified instances
    last_selection_dfs = last_selection_dfs[~last_selection_dfs['instance_id'].isin(to_remove)]

    # Count task with each difficulty level
    easy_count = last_selection_dfs[last_selection_dfs['difficulty'] == '<15 min fix'].shape[0]
    difficult_count = last_selection_dfs[last_selection_dfs['difficulty'] == '1-4 hours'].shape[0]

    print("easy_count: ", easy_count)
    print("difficult_count: ", difficult_count)

    prior_instance_ids = set(last_selection_dfs['instance_id'].tolist())

    # Remove instances in df that are in prior_instance_ids and to_remove
    df_filtered = df[~df['instance_id'].isin(prior_instance_ids.union(to_remove))]

    # Sample new instances to reach target counts
    df_sampled_15min = df_filtered[df_filtered['difficulty'] == '<15 min fix'].sample(n=10 - easy_count, random_state=42)
    df_sampled_1to4hours = df_filtered[df_filtered['difficulty'] == '1-4 hours'].sample(n=10 - difficult_count, random_state=42)

    # Print the new tasks
    print(df_sampled_15min.instance_id.tolist())
    print(df_sampled_1to4hours.instance_id.tolist())

    # Concatenate the samples
    df_sampled = pd.concat([df_sampled_15min, df_sampled_1to4hours, last_selection_dfs])

    # Sort by difficulty
    df_sampled = df_sampled.sort_values(by='difficulty')

    # Reset the index
    df_sampled = df_sampled.reset_index(drop=True)
    
    return df_sampled, df_filtered

to_remove = [
    'django__django-11433', 'sphinx-doc__sphinx-9229', 'pylint-dev__pylint-4551', 'psf__requests-1142', 'django__django-11138', 'sphinx-doc__sphinx-7889', 'django__django-13837', 'sphinx-doc__sphinx-826',
]

df_sampled, df_filtered = create_sample_with_prior_instances(to_remove, last_selection_dfs, df)
print(df_sampled.difficulty.value_counts())


toremove_again = ['sympy__sympy-24539', 'django__django-16116', 'django__django-14011', 'sphinx-doc__sphinx-9461']
df_sampled, df_filtered = create_sample_with_prior_instances(toremove_again, df_sampled, df_filtered)
print(df_sampled.difficulty.value_counts())


futher_remove = ['django__django-15268', 'django__django-16560', 'django__django-13212','django__django-13344']
df_sampled, df_filtered = create_sample_with_prior_instances(futher_remove, df_sampled, df_filtered)
print(df_sampled.difficulty.value_counts())


# remove instances with url in problem statement
df_sampled, df_filtered = create_sample_with_prior_instances(instances_with_url, df_sampled, df_filtered)
print(df_sampled.difficulty.value_counts())


# print(df_sampled.difficulty.value_counts())

# create folder if not exists
os.makedirs("experiment_data/20intances_2level", exist_ok=True)

# save the sampled dataframe to a csv file
df_sampled.to_csv("experiment_data/20intances_2level/experiment_instances.csv", index=False)

# extract the instance ids
instance_ids = df_sampled['instance_id'].tolist()

# convert instance_ids to a regex format, meaning only matches with the instance_ids inside, e.g. ^(matplotlib__matplotlib-24149|sympy__sympy-17630)$
instance_ids_regex = '^(' + '|'.join(instance_ids) + ')$'
# save as a txt file
with open("experiment_data/20intances_2level/experiment_instance_ids.txt", "w") as f:
    f.write(instance_ids_regex)