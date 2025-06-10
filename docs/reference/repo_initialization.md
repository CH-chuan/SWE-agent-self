# Repository Initialization in SWE-agent

This document explains how different repository types are initialized in SWE-agent, with special focus on batch instances and the SWEBench dataset.

## Repository Types

SWE-agent supports three main repository types, all defined in `sweagent.environment.repo`:

1. **PreExistingRepoConfig** - Used for repositories that already exist at the root of the deployment
2. **LocalRepoConfig** - Used for local repositories on the file system
3. **GithubRepoConfig** - Used for GitHub repositories

## Repository Initialization Logic

The core logic for repository initialization happens in the `SimpleBatchInstance.to_full_batch_instance()` method in `sweagent/run/batch_instances.py`. The method determines which repository type to instantiate based on the `repo_name` parameter:

```python
if not self.repo_name:
    repo = None
elif "github" in self.repo_name:
    repo = GithubRepoConfig(github_url=self.repo_name, base_commit=self.base_commit)
elif "/" not in self.repo_name:
    repo = PreExistingRepoConfig(repo_name=self.repo_name, base_commit=self.base_commit)
else:
    repo = LocalRepoConfig(path=Path(self.repo_name), base_commit=self.base_commit)
```

This logic follows these rules:
- If `repo_name` is empty, no repository is used (`repo = None`)
- If `repo_name` contains the string "github", it's treated as a GitHub repository
- If `repo_name` doesn't contain a forward slash ("/"), it's treated as a pre-existing repository
- Otherwise, it's treated as a local repository

## SWEBenchInstances

The `SWEBenchInstances` class in `sweagent/run/batch_instances.py` provides a specialized workflow for loading and initializing repositories from the SWE-bench dataset:

1. It loads SWE-bench instances from Hugging Face datasets
2. Converts each instance to a `SimpleBatchInstance` using the `from_swe_bench()` method
3. Then transforms those into full `BatchInstance` objects using `to_full_batch_instance()`

For SWE-bench instances, repositories are always initialized as `PreExistingRepoConfig` with:
- Repository name: "testbed"
- Base commit: taken from each instance's data

## Instance Filtering and Processing

After creating the batch instances, the `_filter_batch_items` function can:
1. Filter instances by ID using regex patterns
2. Select slices of instances
3. Apply optional shuffling

This allows for flexible batch processing and experimentation with different subsets of repositories.

## Usage Examples

### Command line usage

```bash
# Using a pre-existing repository
--env.repo.repo_name="testbed"
--env.repo.type=preexisting

# Using a local repository
--env.repo.path=path/to/repo
--env.repo.type=local
```

### Code usage

```python
# Pre-existing repository
repo = PreExistingRepoConfig(repo_name="testbed", base_commit="HEAD")

# Local repository
repo = LocalRepoConfig(path=Path("path/to/repo"), base_commit="HEAD")

# GitHub repository
repo = GithubRepoConfig(github_url="https://github.com/user/repo", base_commit="main")
```
