import os
import json
from datetime import datetime
import hashlib
import difflib
import base64



class Repository:
    def __init__(self, path):
        # Initialise the repo, makes folders for objects and branches if doesnt exist
        # by calling initialise repository
        self.path = path
        self.magit_dir = os.path.join(path, '.magit')
        self.objects_dir = os.path.join(self.magit_dir, 'objects')
        self.branches_dir = os.path.join(self.magit_dir, 'branches')
        self.HEAD = os.path.join(self.magit_dir, 'HEAD')


        #create master branch 
        master_branch_path = os.path.join(self.branches_dir, 'master')
        with open(master_branch_path, 'w') as master_file:
            master_file.write('') 
        self.initialize_repository()

    def initialize_repository(self):
        # Only create the .magit file is not exist
        if not os.path.exists(self.magit_dir):
            os.makedirs(self.magit_dir)
            os.makedirs(self.objects_dir)
            os.makedirs(self.branches_dir)
            with open(self.HEAD, 'w') as f:
                f.write('ref: refs/heads/master\n')
            print(f"Initialized empty Magit repository in {self.magit_dir}")


#Blob and Tree Objects: Git uses blob objects for file contents and tree objects to represent 
#the directory structure. MAgit does not do that for simplicity.  
    def add(self, filenames):
        # create  a staged directory, unlike gits index file this is a directory with a collection 
        # of files rather than a single index file 
        # doesn’t create separate blob objects for each file. Instead,
        # it saves the entire content of the file in the staging area 
        # TODO: is to create blob objects 
        staged_area = os.path.join(self.magit_dir, 'staged')
        if not os.path.exists(staged_area):
            os.makedirs(staged_area)

        for filename in filenames:
            # Hash the file content
            with open(filename, 'rb') as file:
                content = file.read()
                file_hash = hashlib.sha1(content).hexdigest()
            file_stage_path = os.path.join(staged_area, file_hash)
            with open(file_stage_path, 'wb') as file_stage:
                file_stage.write(content)

            print(f"Added {filename} to the staging area.")


    def commit(self, message, author):
        # Fix: doesn't check whether there are new changes in the staging area before creating a new commit.
        commit_data = {
            'timestamp': datetime.now().isoformat(),
            'author': author,
            'message': message,
            'parent': self.get_current_commit_hash(),
            'changes': self.get_staged_changes()
        }
        # TODO: only commit if files in staged areas and then remove from staged 
        commit_hash = self.create_object(commit_data)
        self.update_HEAD(commit_hash)
        print(f"Committed with hash {commit_hash}")
        staged_area = os.path.join(self.magit_dir, 'staged')
        for staged_file in os.listdir(staged_area):
            os.remove(os.path.join(staged_area, staged_file))


    def get_current_commit_hash(self):
        if os.path.isfile(self.HEAD):
            with open(self.HEAD, 'r') as f:
                ref_line = f.readline().strip()
                if ref_line.startswith('ref:'):
                    ref_path = os.path.join(self.magit_dir, ref_line.split(':')[1].strip())
                    if os.path.isfile(ref_path):
                        with open(ref_path, 'r') as ref_file:
                            return ref_file.read().strip()
        return None



    def get_staged_changes(self):
        staged_area = os.path.join(self.magit_dir, 'staged')
        changes = {}
        if os.path.exists(staged_area):
            for staged_file in os.listdir(staged_area):
                staged_file_path = os.path.join(staged_area, staged_file)
                if os.path.isfile(staged_file_path):
                    with open(staged_file_path, 'rb') as file:
                        content = file.read()
                        encoded_content = base64.b64encode(content).decode('utf-8')
                        changes[staged_file] = encoded_content
        return changes


    def create_object(self, data):
        print(data)
        commit_hash = hashlib.sha1(json.dumps(data).encode()).hexdigest()
        commit_path = os.path.join(self.objects_dir, commit_hash)
        with open(commit_path, 'w') as commit_file:
            json.dump(data, commit_file)
        return commit_hash
    
    def update_HEAD(self, commit_hash):
        if os.path.isfile(self.HEAD):
            with open(self.HEAD, 'r') as f:
                ref_line = f.readline().strip()
                if ref_line.startswith('ref:'):
                    branch_name = ref_line.split('/')[-1]

                    branch_path = os.path.join(self.branches_dir, branch_name)

                    with open(branch_path, 'w') as branch_file:
                        branch_file.write(commit_hash)



    def create_branch(self, branch_name):
        branch_path = os.path.join(self.branches_dir, branch_name)
        current_commit = self.get_current_commit_hash()
        with open(branch_path, 'w') as branch_file:
            branch_file.write(current_commit)
        print(f"Branch {branch_name} created.")

    def switch_branch(self, branch_name):
        # todo : handle uncommited changes 
        branch_path = os.path.join(self.branches_dir, branch_name)
        if os.path.exists(branch_path):
            with open(self.HEAD, 'w') as head_file:
                head_file.write(f'ref: refs/heads/{branch_name}\n')
            print(f"Switched to branch {branch_name}")
        else:
            print(f"Branch {branch_name} does not exist.")


    
    def merge(self, source_branch, destination_branch):
        # a basic merge ASSUMING NO CONFILICT 
        source_branch_path = os.path.join(self.branches_dir, source_branch)
        destination_branch_path = os.path.join(self.branches_dir, destination_branch)

        if os.path.exists(source_branch_path) and os.path.exists(destination_branch_path):
            with open(source_branch_path, 'r') as source_file:
                source_commit = source_file.read().strip()

            with open(destination_branch_path, 'w') as dest_file:
                dest_file.write(source_commit)
            
            print(f"Merged {source_branch} into {destination_branch}")
        else:
            print("Branches not found.")

    # todo: handle if not .magit file
    def diff(self, commit_hash1, commit_hash2):
        commit1_path = os.path.join(self.objects_dir, commit_hash1)
        commit2_path = os.path.join(self.objects_dir, commit_hash2)

        if os.path.exists(commit1_path) and os.path.exists(commit2_path):
            with open(commit1_path, 'r') as file1, open(commit2_path, 'r') as file2:
                lines1 = file1.readlines()
                lines2 = file2.readlines()

                for line in difflib.unified_diff(lines1, lines2, fromfile=commit_hash1, tofile=commit_hash2):
                    print(line)
        else:
            print("Commits not found.")



    def status(self):
        # just checking if files are staged for commit 
        # TODO: add the files not staged for commit, and untracked (new) files
        staged_area = os.path.join(self.magit_dir, 'staged')
        if os.path.exists(staged_area):
            print("Staged files:")
            for file in os.listdir(staged_area):
                print(file)
        else:
            print("No files staged for commit.")



    def log(self):
        #basic log reading from objects directory 
        current_commit = self.get_current_commit_hash()
        while current_commit:
            commit_path = os.path.join(self.objects_dir, current_commit)
            if os.path.exists(commit_path):
                with open(commit_path, 'r') as commit_file:
                    commit_data = json.load(commit_file)
                    print(f"commit {current_commit}")
                    print(f"Author: {commit_data['author']}")
                    print(f"Date: {commit_data['timestamp']}")
                    print(f"\n\t{commit_data['message']}\n")
                # if parent exists other wise none
                current_commit = commit_data['parent'] if 'parent' in commit_data else None
            else:
                break















# Usage
repo = Repository('test')
#repo.add(['test/test1.py'])
#repo.commit('nice','mai')
#repo.status()
#repo.log() 
#repo.diff("0863aebc3ad229f06867aae724f75d44f12e861c","d368e86ea7f69dcf7c18e8c4f6ec94ac5f6b0ac7")
#repo.get_staged_changes()
repo.create_branch("branch1")
repo.switch_branch("branch1")

