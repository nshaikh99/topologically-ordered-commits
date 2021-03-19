# topologically ordered commits
A Python script that prints the commits of a Git repository in topological order
## Prerequisites
python3
## Usage
Download topo_order_commits.py and put it in your Git directory. Then, use the command line to navigate to your Git directory and execute the following commands:
```
chmod u+x topo_order_commits.py
./topo_order_commits.py
```
In the event that the command `./topo_order_commits.py` does not work, try `python3 topo_order_commits.py` instead.
## Implementation
The implementation of this script relies on five methods that execute in succession:
1. find_git_directory, which discovers the .git directory
2. get_branch_names, which gets a list of branch names
3. build_commit_graph, which builds the commit graph
4. topological_sort, which generates a topological ordering
5. print_ordered_commits, which prints commit hashes in order

Commits are stored as CommitNode objects which have a commit hash, parent(s), and child(ren).
