import sys
from configparser import ConfigParser

from gitlab import Gitlab


def log(*args):
    print(*args, file=sys.stderr)


def print_labels(issue):
    print("\t", end='')
    for label in issue.labels:
        if label not in ['bug', 'feature'] and not label.startswith('P:'):
            print("[%s]" % label, end='')


def make_changelog():
    config = ConfigParser()
    config.read('defaults.cfg')

    gl = Gitlab(config.get('gitlab', 'url'), config.get('gitlab', 'key'), api_version='4')
    gl.auth()

    look_for = config.get('gitlab', 'project')
    project_path, project_name = '/' in look_for and look_for.split('/', 1) or (None, look_for)

    gl_project = None
    log("Looking for project '%s'" % project_name)
    for p in gl.projects.list(search=project_name):
        log(p.path_with_namespace)
        if p.path_with_namespace == look_for:
            gl_project = p
            break

    if not gl_project:
        log("ERROR: Project '%s' not found!" % look_for)
        exit()

    log(gl_project.id)

    milestones = [ml for ml in gl_project.milestones.list(all=True) if ml.due_date is not None]
    milestones.sort(key=lambda ml: ml.due_date or '', reverse=True)

    for milestone in milestones:
        # log(milestone)
        # log(len(milestone.issues()))
        issues = [issue for issue in milestone.issues() if not issue.confidential]
        title = "%s (%s) (%d issues)" % (milestone.title, milestone.due_date, len(issues))
        print(title)
        print('-' * len(title))
        print()
        # Features
        for issue in issues:
            # log(issue)
            if 'feature' in issue.labels:
                print("* **Feature #%d**: %s " % (issue.iid, issue.title), end='')
                print_labels(issue)
                print()

        # Bug fixes
        for issue in issues:
            # log(issue)
            if 'bug' in issue.labels:
                print("* **Fix #%d**: %s " % (issue.iid, issue.title), end='')
                print_labels(issue)
                print()

        # Other
        for issue in issues:
            # log(issue)
            if 'bug' not in issue.labels and 'feature' not in issue.labels:
                print("* **#%d**: %s " % (issue.iid, issue.title), end='')
                print_labels(issue)
                print()

        print()


if __name__ == '__main__':
    make_changelog()
