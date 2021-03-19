#!/usr/bin/python3
import os
import sys
import zlib
import copy
from collections import deque

'''
I verified that my implementation does not use other commands by running "strace -f python3 topo_order_commits.py 2>&1 | grep git | grep execve" on all of the repositories provided in the test suite.
There was no output; therefore, no other commands were used.
'''

def find_git_directory():
    path = os.getcwd() # start in current working directory
    while not os.path.exists(path + "/.git"): # while path doesn't contain .git
        if path == "/": # if in root directory then exit
            exit("Not inside a git repository")
        path = os.path.dirname(path) # go to parent directory
    return path + "/.git"

def get_branch_names(directory, prefix):
    if prefix:
        prefix = prefix + "/"
    branches = {} # dict to store branches and their corresponding commit hashes
    for i in os.listdir(directory): # iterate over directory
        path = directory + "/" + i
        if os.path.isfile(path): # if i is a file (and therefore a branch)
            branch_file = open(path, "r")
            commit_hash = branch_file.readline().strip() # read first line containing commit hash
            branches[prefix + i] = commit_hash # store commit hash in the dict
        if os.path.isdir(path): # if i is a directory
            branches.update(get_branch_names(path, i))
    return branches

class CommitNode:
    def __init__(self, commit_hash):
        """
        :type commit_hash: str
        """
        self.commit_hash = commit_hash
        self.parents = set()
        self.children = set()

def decompress(commit_hash):
    path = find_git_directory() + "/objects" + "/" + commit_hash[:2] + "/" + commit_hash[2:]
    commit_file = open(path, "rb")
    commit_contents = zlib.decompress(commit_file.read()).decode().split("\n")
    return commit_contents

def build_commit_graph(branches):
    commit_nodes = {} # to store the graph
    visited = set() # to store visited nodes
    stack = list(branches.values())
    while stack: # while there are nodes to process
        commit_hash = stack.pop() # get a node
        if commit_hash in visited: # if already visited then done
            continue
        visited.add(commit_hash)
        if commit_hash not in commit_nodes: # if not in graph then add
            commit_nodes[commit_hash] = CommitNode(commit_hash)
        commit = commit_nodes[commit_hash]

        # decompress commit object to get parents
        commit_contents = decompress(commit_hash)
        for i in commit_contents:
            if i[0:6] == "parent":
                commit.parents.add(i[7:])

        for p in commit.parents: # iterate over parents
            if p not in visited: # if not visited then add to processing list
                stack.append(p)
            if p not in commit_nodes: # if not in graph then add
                commit_nodes[p] = CommitNode(p)
            commit_nodes[p].children.add(commit_hash) # establish relationship from parent to child
    return commit_nodes

def topological_sort(commit_nodes):
    result = [] # to store sorted commits
    no_children = deque() # to store leaf nodes
    copy_graph = copy.deepcopy(commit_nodes)

    for commit_hash in copy_graph: # iterate over graph
        if len(copy_graph[commit_hash].children) == 0: # identify leaf nodes
            no_children.append(commit_hash)

    while len(no_children) > 0: # while there are leaf nodes
        commit_hash = no_children.popleft() # get a leaf node
        result.append(commit_hash) # add to sorted commits

        for parent_hash in list(copy_graph[commit_hash].parents): # iterate over parents
            copy_graph[commit_hash].parents.remove(parent_hash) # dissolve relationship from child to parent
            copy_graph[parent_hash].children.remove(commit_hash) # dissolve relationship from parent to child
            if len(copy_graph[parent_hash].children) == 0: # if no children left then add to leaf nodes
                no_children.append(parent_hash)

    if len(result) < len(commit_nodes):
        raise Exception("cycle detected")

    return result

def print_ordered_commits(commit_nodes, topo_ordered_commits, head_to_branches):
    '''
    THE CODE FOR THIS FUNCTION WAS PROVIDED BY THE TA'S OF PAUL EGGERT'S CS 97 CLASS AT UCLA
    '''
    jumped = False
    for i in range(len(topo_ordered_commits)):
        commit_hash = topo_ordered_commits[i]
        if jumped:
            jumped = False
            sticky_hash = ' '.join(commit_nodes[commit_hash].children)
            print(f'={sticky_hash}')
        branches = sorted(head_to_branches[commit_hash]) if commit_hash in head_to_branches else []
        print(commit_hash + (' ' + ' '.join(branches) if branches else ''))
        if i + 1 < len(topo_ordered_commits) and topo_ordered_commits[i + 1] not in commit_nodes[commit_hash].parents:
            jumped = True
            sticky_hash = ' '.join(commit_nodes[commit_hash].parents)
            print(f'{sticky_hash}=\n')

def topo_order_commits():
    git_directory = find_git_directory() # step one: discover the .git directory
    branches = get_branch_names(git_directory + "/refs/heads", "") # step two: get a list of branch names
    commit_nodes = build_commit_graph(branches) # step three: build the commit graph
    topo_ordered_commits = topological_sort(commit_nodes) # step four: generate a topological ordering
    head_to_branches = {}
    for branch_name, branch_head_hash in branches.items():
        head_to_branches[branch_head_hash] = [ branch_name ]
    print_ordered_commits(commit_nodes, topo_ordered_commits, head_to_branches) # step five: print commit hashes in order

if __name__ == '__main__':
    topo_order_commits()