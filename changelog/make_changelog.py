import sys

from gitlab import Gitlab
from configparser import ConfigParser


def log(*args):
    print(*args, file=sys.stderr)


config = ConfigParser()
config.read('defaults.cfg')

gl = Gitlab(config.get('gitlab', 'url'), config.get('gitlab', 'key'))
gl.auth()

look_for = config.get('gitlab', 'project')
project_name = '/' in look_for and look_for.split('/', 1)[1] or look_for

gl_project = None
log("Looking for project '%s'" % project_name)
for p in gl.projects.search(project_name):
    log (p.path_with_namespace)
    if p.path_with_namespace == look_for:
        gl_project = p
        break

if not gl_project:
    log("ERROR: Project '%s' not found!" % look_for)
    exit()

log (gl_project.id)

milestones = [ml for ml in gl_project.milestones.list(all=True) if ml.state == 'closed']
milestones.sort(key=lambda ml: ml.due_date or '', reverse=True)

for milestone in milestones:
    # log(milestone)
    title = "%s (%s)" % (milestone.title, milestone.due_date)
    print(title)
    print('-' * len(title))
    print()
    issues = [issue for issue in milestone.issues() if not issue.confidential]
    for issue in issues:
        # log(issue)
        print("* Fix #%d: %s" % (issue.iid, issue.title))
    print()
