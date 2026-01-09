import github
import os
import subprocess
import glob
import shutil
ORG = "UoY-PDM1" # REPLACE WITH YOUR ORG NAME
LOCAL_FOLDER = "/Users/ae1001/Documents/GitHub/PDM1/2526" # THIS SHOULD BE THE PATH TO THE FOLDER ON YOUR COMPUTER THAT YOU WANT TO CLONE ALL REPOS TO
GITHUB = "https://github.com"


def clone_all(templates):
    """
    Clones all repos in the list of templates to the local folder.

    Arg:
        templates (list of str) - the names of repos to clone
    """
    for template in templates:
        print("Clone URL", f"{GITHUB}/{ORG}/{template}.git")
        subprocess.run(["git", "clone", f"{GITHUB}/{ORG}/{template}.git"], capture_output=True)
    print("Done cloning")

def copy_latest_test_script(templates):
    """
    PDM 1 only. Copies the latest test script to all repos in templates list.

    Arg:
        templates (list of str) - the folder names of the local repos to update
    """
    latest_test = "../../test-demo/testing/test-utils.js"
    for template in templates:
        print("Searching in", template)
        # go into to repo folder
        os.chdir(template)
        files = glob.glob("*/test-utils.js", recursive=True)
        for file in files:
            shutil.copyfile(latest_test, file)
            print("Updated", file, "in", template)
        # go back to org folder
        os.chdir("../")


def commit_all_changes(templates):
    """
    Commit and push all changes to the listed repos.

    Arg:
        templates (list of str) - the folder names of the local repos to update
    """
    for template in templates:
        print("Updating", template)
        os.chdir(template)
        subprocess.run(["git", "add", "."])
        subprocess.run(["git", "commit", "-m", 'automated update'])
        subprocess.run(["git", "push"])
        os.chdir("../")
    print("Done!")

def change_visibility(templates, make_public):
    """
    Set the visibility of a group of GitHub repos.

    Args:
        templates (list of str) - the names of the GitHub repos to update
        make_public (bool) - True to make the repos public, or False to make them private.
    """
    for template in templates:
        print("Updating", template)
        github.set_visibility(ORG, template, make_public)

if __name__ == "__main__":
    org_templates = github.get_all_template_repos(ORG) # Gets all template repos in the org

    # Optional: These two lines clone all template repos to your local folder
    os.chdir(LOCAL_FOLDER) # Points the command line to 
    clone_all(org_templates)
    
    # Make all template repos public
    change_visibility(org_templates, True)