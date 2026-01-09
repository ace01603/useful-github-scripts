import github

OLD_ORG = "UoY-IM-PDM" # The name of the org used in previous semesters. Templates will be copied FROM this org.
CURRENT_ORG = "UoY-PDM1" # The org name for the current semester. New repos will be created in this org using the templates in the old org.

if __name__ == "__main__":
    old_org_templates = github.get_all_template_repos(OLD_ORG)
    current_org_repos = github.get_all_repos_in_org(CURRENT_ORG, False, False)
    for template in old_org_templates:
        print("Found template", template)
        # check if repo exists in current repo
        if template not in current_org_repos:
            # create a new repo using the old one as template
            result = github.create_repo_from_template(CURRENT_ORG, template, OLD_ORG, template, True, True)
            print("Creating", template, "in", CURRENT_ORG, "success?", result)
            if not result:
                break
    print("Done!")
