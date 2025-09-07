since apptainer does not support publishing portals

Now, we need to:
1. check how local files are modified through the tools
2. if possible, then we can build swebench instances as local repo and start running it.

Doable, check venv/lib64/python3.11/site-packages/swerex/runtime/local.py for more detail on how it is used