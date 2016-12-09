__author__ = 'ricard'
from redmine import Redmine
from gitlab import Gitlab
from configparser import ConfigParser

config = ConfigParser()
config.readfp(open('defaults.cfg'))

redmine = Redmine(config.get('redmine', 'url'), key=config.get('redmine', 'key') )

red_project = redmine.project.get(config.get('redmine', 'project'))

gl = Gitlab(config.get('gitlab', 'url'), config.get('gitlab', 'key'))
gl.auth()
look_for = config.get('gitlab', 'project')
for p in gl.Project(per_page=1000):
    # print (p.path_with_namespace)
    if p.path_with_namespace == look_for:
        gl_project_id = p.id
        gl_project = p
        break

print (gl_project.id)

closed_status = []
for status in redmine.issue_status.all():
    # print (status, list(status))
    if getattr(status, 'is_closed', False):
        closed_status.append(status.id)

trackers = {
    1: "bug",
    2: "feature",
    3: "help",
    5: "task"
}

# for tracker in redmine.tracker.all():
#     print (tracker, dir(tracker))
#     trackers[tracker.id] = tracker.name
# exit(1)

labels = gl_project.Label(per_page=1000)
for cat in red_project.issue_categories:
    found = False
    cat_name  = cat.name.lower()
    for label in labels:
        if label.name == cat_name:
            found = True
            break
    if not found:
        print ("Creating label %s" % cat_name)
        label = gl_project.Label({'name': cat_name, 'color': '#5cb85c'})
        label.save()

versionDict = {}
milestones = gl_project.Milestone(per_page=1000)
for version in red_project.versions:
    found = False
    for ms in milestones:
        if version.name == ms.title:
            found = True
            if version.status == 'closed' and ms.state == 'active':
                print ("Closing milestone %s" % ms.title)
                ms.state_event = 'close'
                ms.save()
            break
    if not found:
        print ("Creating milestone %s" % version.name)
        ms = gl_project.Milestone({'title': version.name, 'description': version.description, 'due_date': getattr(version, 'due_date', None)})
        ms.save()
        if version.status == 'closed':
            ms.state_event = 'close'
            ms.save()
        # label.save()
    versionDict[version.id] = ms.id


#gl_issues = gl_project.Issue()
for issue in redmine.issue.filter(project_id=red_project.id, status_id='*', sort='id'):
    # if issue.id < 609:
    #     continue
    issue = redmine.issue.get(issue.id, include='journals')
    print (issue.status, dir(issue.status))
    #print (type(issue.fixed_version), issue.fixed_version.id, issue.fixed_version)
    # print (issue.id, issue.subject, issue.tracker)
    categories = [trackers[issue.tracker.id]]
    if hasattr(issue, 'category'):
        categories.append(issue.category.name.lower())
        
    print (issue.id, issue.status, categories, issue.subject)
    
    milestone_id = None
    if hasattr(issue, 'fixed_version'):
        milestone_id = versionDict.get(issue.fixed_version.id)
    gl_issue = gl_project.Issue({'title': issue.subject, 'description': issue.description,
                                'labels': ','.join(categories), 'milestone_id': milestone_id, 'state_event': issue.status.id in closed_status})
    gl_issue.save()
    if issue.status.id in closed_status:
        print ("CLOSED!!")
        gl_issue = gl_project.Issue(gl_issue.id)
        gl_issue.state_event = "close"
        gl_issue.save()
    
    if hasattr(issue, 'journals'):
        for j in issue.journals:
            print ("  ", j.id, j.created_on, j.user, j.details, "Note:", getattr(j, 'notes', None))
            notes = getattr(j, 'notes', None)
            if notes and notes.strip():
                #print ("[%s] Note: %s" % (type(notes), notes), repr(notes))
                note = gl_issue.Note({'body': notes})
                note.save()
    
    
