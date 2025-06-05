
import pandas as pd

# Login using e.g. `huggingface-cli login` to access this dataset
df = pd.read_parquet("hf://datasets/princeton-nlp/SWE-bench_Verified/data/test-00000-of-00001.parquet")

columns_to_use = [
    'instance_id',
    'repo',
    'difficulty',
]

df = df[columns_to_use]

selected_instances = [
    "matplotlib__matplotlib-24637",
    "pydata__xarray-3677",
    "sympy__sympy-22914",
    "astropy__astropy-14539",
    "scikit-learn__scikit-learn-11578",
    "django__django-11433",
    "sphinx-doc__sphinx-8269",
    "matplotlib__matplotlib-13989",
    "django__django-15277",
    "sphinx-doc__sphinx-7889",
    "django__django-13837",
]

df_selected = df[df['instance_id'].isin(selected_instances)]

# remove rows in df if instance_id is in selected_instances
df = df[~df['instance_id'].isin(selected_instances)]


# sample 4 from 1-4 hours
df_1_to_4_hours = df[df['difficulty'] == '1-4 hours'].sample(n=4, random_state=42)

df_new = pd.concat([df_selected, df_1_to_4_hours])
df_new = df_new.reset_index(drop=True)

df_new.to_csv("experiment_data/experiment_instances_new.csv", index=False)

instance_ids = df_new['instance_id'].tolist()

instance_ids_regex = '^(' + '|'.join(instance_ids) + ')$'

with open("experiment_data/experiment_instance_ids_new.txt", "w") as f:
    f.write(instance_ids_regex)