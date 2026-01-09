import requests
API_URL = "https://api.github.com"
TOKEN = "YOUR TOKEN HERE" # Your classic access token with admin access to all repos and orgs you want to access / change. https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens
HEADER = {"Authorization": f"Bearer {TOKEN}"}
AUTH = "?access_token={}".format(TOKEN)
REPOS_PER_PAGE = 100

def get_all_repos_in_org(org, private_only = False, exclude_templates = True):
    """ 
    Gets a list of the organization's repo names.
    API reference: https://developer.github.com/enterprise/2.20/v3/repos/#list-organization-repositories

    Arg:
        org (str) - The organization name.

    Returns:
        (list of str) - A list of repo names.
    """
    repo_names = []
    page = 1
    results_returned = True
    while results_returned:
        get_repos = f"{API_URL}/orgs/{org}/repos?per_page=100&page={page}"
        r = requests.get(get_repos, headers=HEADER).json()
        for repo in r:
            if ((private_only and bool(repo["private"])) or not private_only) and (not bool(repo["is_template"]) or not exclude_templates):
                repo_names.append(repo["name"])
        page += 1
        if len(r) == 0:
            results_returned = False
    return repo_names

def get_all_template_repos(org):
    """ 
    Gets a list of the organization's template repo names.
    API reference: https://developer.github.com/enterprise/2.20/v3/repos/#list-organization-repositories

    Arg:
        org (str) - The organization name.

    Returns:
        (list of str) - A list of repo names.
    """
    repo_names = []
    page = 1
    results_returned = True
    while results_returned:
        get_repos = f"{API_URL}/orgs/{org}/repos?per_page=100&page={page}"
        r = requests.get(get_repos, headers=HEADER).json()
        for repo in r:
            if bool(repo["is_template"]):
                repo_names.append(repo["name"])
        page += 1
        if len(r) == 0:
            results_returned = False
    return repo_names

def get_collaborators(org, repo):
    get_collaborators = f"{API_URL}/repos/{org}/{repo}/collaborators"
    r = requests.get(get_collaborators, headers=HEADER).json()
    return r

def set_collaborator_permission(org, repo, user, permission_level):
    set_collaborator = f"{API_URL}/repos/{org}/{repo}/collaborators/{user}"
    r = requests.put(set_collaborator, headers=HEADER, json={"permission": permission_level})
    print(f"gave {user} {permission_level} rights to {repo}")

def set_visibility(org, repo, make_public):
    set_visibility = f"{API_URL}/repos/{org}/{repo}"
    r = requests.patch(set_visibility, headers=HEADER, json={"visibility": "public" if make_public else "private"})
    print(f"set visibility of {repo} - is public? {make_public}")

# ORIG
def get_team_member_count(org, team_slug):
    get_team_info = "{}/orgs/{}/teams/{}{}".format(API_URL, org, team_slug, AUTH)
    r = requests.get(get_team_info).json()
    return int(r["members_count"])

def page_count(repos):
    return repos // REPOS_PER_PAGE + 1


def create_private_repo(org, repo_name, is_template = False):
    """ 
    Creates a private repo in an organization.
    API reference: https://developer.github.com/enterprise/2.20/v3/repos/#create-an-organization-repository

    Args:
        org (str) - The organization name.
        repo_name (str) - The name of the new repo.

    Returns:
        (bool) - True if the repo is created, false otherwise.
    """
    repo_config = {
        "name": repo_name,
        "private": "true",
        "visibility": "private",
        "auto_init": "true",
        "is_template": str(is_template).lower()
    }
    create_repo_url = "{}/orgs/{}/repos{}".format(API_URL, org, AUTH)
    r = requests.post(create_repo_url, json=repo_config).json()
    return "id" in r

def create_repo_from_template(org, repo_name, template_owner, template_name, is_private = True, is_template = False):
    """ 
    Creates a private repo in an organization.
    API reference: https://developer.github.com/enterprise/2.20/v3/repos/#create-an-organization-repository

    Args:
        org (str) - The organization name that will own the new repo.
        repo_name (str) - The name of the new repo.
        template_owner (str) - The owner of the template repo
        template_name (str) - The name of the template repo
        is_private (bool) - Whether the new repo should be private
        is_template (bool) - Whether the new repo should also be a template

    Returns:
        (bool) - True if the repo is created, false otherwise.
    """
    repo_config = {
        "name": repo_name,
        "owner": org,
        "private": is_private#str(is_private).lower()
    }
    # /repos/{template_owner}/{template_repo}/generate
    create_repo_url = f"{API_URL}/repos/{template_owner}/{template_name}/generate"
    r = requests.post(create_repo_url, json=repo_config, headers=HEADER).json()
    if "id" in r:
        if is_template:
            patch_repo_url = f"{API_URL}/repos/{org}/{repo_name}"
            repo_update = {
                "is_template": is_template
            }
            p = requests.patch(patch_repo_url, headers=HEADER, json=repo_update).json()
        return True
    print(r)
    # get_repos = f"{API_URL}/orgs/{org}/repos?per_page=100&page={page}"
    #     r = requests.get(get_repos, headers=HEADER).json()
    return False


def add_collaborators_to_repo(org, repo_name, collaborators = []):
    """ 
    Adds collaborators to a repo. Collaborators have write access. Silent if
    something goes wrong.

    API reference: https://developer.github.com/enterprise/2.20/v3/repos/collaborators/#add-user-as-a-collaborator

    Args:
        org (str) - The organization name.
        repo_name (str) - The name of the new repo.
        collaborators (list of str) - A list of usernames.
    """
    collab_permissions = {
        "permission":"push"
    }
    for user in collaborators:
        repo_url = "https://github.ccs.neu.edu/api/v3/repos/{}/{}/collaborators/{}?access_token={}".format(org, repo_name, user, TOKEN)
        requests.put(repo_url, json=collab_permissions)


def add_staff_to_repo(org_name, repo_name, team_id):
    """ 
    Adds a team to a repo. The team has admin access. Silent if something goes
    wrong.

    API reference: https://developer.github.com/enterprise/2.20/v3/teams/#add-or-update-team-repository

    Args:
        org (str) - The organization name.
        repo_name (str) - The name of the new repo.
        team_id (str or int) - The team ID. This is different from the team name. The 
        team ID can be retrieved using get_org_team().
    """
    team_permissions = {
        "permission":"admin"
    }
    repo_url = "{}/teams/{}/repos/{}/{}{}".format(API_URL, team_id, org_name, repo_name, AUTH)
    requests.put(repo_url, json=team_permissions)


def get_org_team(org, team_slug):
    """ 
    Gets a team ID using the team slug. Crashes if given an invalid team slug.

    API reference: https://developer.github.com/enterprise/2.20/v3/teams/#get-team-by-name

    Args:
        org (str) - The organization name.
        team_slug (str) - The team slug. This is the team name as it appears in
        the team page URL.

    Returns:
        (str) - The team ID.
    """
    get_team_url = "{}/orgs/{}/teams/{}{}".format(API_URL, org, team_slug, AUTH)
    r = requests.get(get_team_url).json()
    return r["id"]

def get_team_members(org, team_slug):
    """
    Gets team members.
    
    API reference: https://developer.github.com/v3/teams/members/#list-team-members

    Args:
        org (str) - The organization name.
        team_slug (str) - The team slug. This is the team name as it appears in
        the team page URL.

    Returns:
        (list) - A list of team member usernames.
    """
    member_count = get_team_member_count(org, team_slug)
    print(team_slug, "has", member_count, "members")
    pages = member_count // 30 + 1
    print("There are", member_count, "members in", pages, "pages")
    members = []
    for p in range(1, pages + 1): # PAGiNatE
        get_team_members_url = "{}/orgs/{}/teams/{}/members{}&page={}".format(API_URL, org, team_slug, AUTH, p)
        print(get_team_members_url)
        r = requests.get(get_team_members_url).json()
        for user in r:
            members.append(user["login"])
    return  members


def add_user_to_team(org, team_slug, username):
    """
    Adds the given user to the given team with member privileges.

    API reference: 

    Args:
        org (str) - The organization name.
        team_slug (str) - The team slug, as it appears on the teams page.
        username (str) - The user to add
    """
    print("adding", username)
    #/orgs/:org/teams/:team_slug/memberships/:username
    add_url = "{}/orgs/{}/teams/{}/memberships/{}{}".format(API_URL, org, team_slug, username, AUTH)
    requests.put(add_url)


def enable_pages(org, repo, source):
    """ 
    Enables GitHub Pages with the given source. Using a preview API. Only works
    if Pages is not already enabled.

    API reference: https://developer.github.com/enterprise/2.20/v3/repos/pages/#enable-a-pages-site

    Args:
        org (str) - The organization name.
        repo (str) - The repo name.
        source (obj) - The source used to publish the Pages site. See the API
        docs.
    """
    pages_url = "{}/repos/{}/{}/pages{}".format(API_URL, org, repo, AUTH)
    header = {"Accept": "application/vnd.github.switcheroo-preview+json"}
    requests.post(pages_url, json=source, headers=header)


def enable_pages_on_master(org, repo):
    """ 
    Enables GitHub Pages on the master branch. Using a preview API. Only works
    if Pages is not already enabled.

    API reference: https://developer.github.com/enterprise/2.20/v3/repos/pages/#enable-a-pages-site

    Args:
        org (str) - The organization name.
        repo (str) - The repo name.
    """
    source = {
        "source": {
            "branch":"master"
        }
    }
    enable_pages(org, repo, source)


def enable_pages_from_docs(org, repo):
    """ 
    Enables GitHub Pages from the docs folder on the master branch. Using a
    preview API. Only works if the docs folder already exists and Pages is not
    already enabled.

    API reference: https://developer.github.com/enterprise/2.20/v3/repos/pages/#enable-a-pages-site

    Args:
        org (str) - The organization name.
        repo (str) - The repo name.
    """
    source = {
        "source": {
            "branch":"master",
            "path": "/docs"
        }
    }
    enable_pages(org, repo, source)

def get_user(username):
    """ 
    Gets a Khoury GitHub user by username.

    API reference: https://developer.github.com/enterprise/2.20/v3/users/#get-a-single-user

    Args:
        username (str) - The username.

    Returns:
        (obj) - A JSON object with user details or an error message if the user
        is not found.
    """
    get_user_url = "{}/users/{}{}".format(API_URL, username, AUTH)
    r = requests.get(get_user_url)
    return r.json()


def is_valid_user(username):
    """ 
    Checks if a user is a valid Khoury GitHub user.

    Args:
        username (str) - The username.

    Returns:
        (bool) - True if the user exists, False if not.
    """
    user = get_user(username)
    return "id" in user

def validate_accounts(accounts):
    """ 
    Sorts a dict of user accounts into two objects: one containing valid users,
    the other containing invalid users. (Students, especially Align students,
    sometimes confuse their Khoury usernames with their GitHub usernames)

    Args:
        accounts (dict) - Account info. Keys should be usernames.

    Returns:
        (dict) - The valid accounts.
        (dict) - The invalid accounts.
    """
    valid_accounts = {}
    invalid_accounts = {}
    for user in accounts:
        user = user.strip()
        if is_valid_user(user):
            print("VALID", user)
            valid_accounts[user] = accounts[user]
        else:
            print("INVAlID", user)
            invalid_accounts[user] = accounts[user]
    return valid_accounts, invalid_accounts
