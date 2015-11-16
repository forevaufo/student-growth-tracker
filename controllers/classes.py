"""
The classes controller.

Everything concerning classes goes here. Sort of. We'll clarify as we go on.
"""

from gluon.contrib.simplejson import dumps, loads
import datetime

@auth.requires_login()
def index():
    """
    Display the list of classes associated with the logged in user.

    - If the user is a teacher, the list shows all of the classes that teacher
      teaches.
    - If the user is a student, the list shows all of the classes that student
      attends.

    .. todo:: Make these queries context sensitive per the list in the docstring.
              They should also have generic names, but I think the ones I chose
              are probably good, at least for now.

    .. todo:: Add checks to determine user role, and select appropriate query.
    """

    teacher_id = auth.user_id # Cache the user id of the logged-in teacher
                              # to make it easier to access and recognize.

    class_id = (request.args(0) != None) and request.args(0, cast=int) or None

    ############################################################################
    ## This should go into a function.
    if not class_id:
        response.flash = T("Class Does Not Exist")
        session.flash = T("Class does not exist.")

        # Redirect to previous link if via link, else redirect to main page.
        if (request.env.http_referer==None):
            redirect(URL('default', 'index'))
        else:
            redirect(request.env.http_referer)
    ##
    ############################################################################

    class_name = db.classes[class_id].name
    class_list = get_class_list(teacher_id)
    class_roster = get_class_roster(teacher_id, class_id)
    class_assignments = get_class_assignments(teacher_id, class_id)
    assignments = get_student_assignments(teacher_id, class_id)
    standards = get_standards_for_class(class_id)
    
    return dict(class_id=class_id,
                class_name=class_name,
                class_list=class_list,
                class_roster=class_roster,
                class_assignments=class_assignments,
                assignments=assignments,
                standards=standards)

@auth.requires_login()
def student_grades():
    """
    Retrieves grade information for a given ``class_id``
    and returns it as ``json``.
    """
    teacher_id = auth.user_id
    class_id = (request.args(0) != None) and request.args(0, cast=int) or None

    return dumps(get_student_assignments(teacher_id, class_id))

@auth.requires_login()
def save_student_grades():
    """
    Receives ``json`` data via ajax from the ``handsontable`` object
    and saves it back to the database.
    """
    vargs = request.vars

    try:
        for k in vargs.keys():
            student_grades = vargs[k]
            # grades = [int(s) for s in student_grades[2:]]
            for i in range(2, len(student_grades), 2):
                grade_id = int(student_grades[i])
                score = float(student_grades[i+1])
                db.student_grade[grade_id] = dict(student_score=score)

    except Exception, e:
        print 'Error: %s' % e

    return dict()


@auth.requires_login()
def overview():
    teacher_id = auth.user_id
    class_id = (request.args(0) != None) and request.args(0, cast=int) or None

    #To display class name.
    query = teacher_classes_query(teacher_id, class_id)
    class_query = db(query).select(db.classes.name)
    class_name = class_query[0].name

    #To display number of students.
    total_students = len(get_class_roster(teacher_id, class_id))

    #To display number of assignments
    grade_query = ((db.class_grade.class_id == class_id) & (db.class_grade.grade_id == db.grade.id))
    total_grades = db(grade_query).count()

    #To display class average
    total_score = get_class_total_score(class_id)
    total_possible= get_class_total_possible(class_id)
    print("total_score ",total_score)
    print("total_possible ",total_possible)
    average = 0
    try:
        average = round(total_score / total_possible * 100.0, 2)
    except:
        pass

    #To display standards
    query = ((db.classes.id==class_id) &
#             (db.classes.id==db.student_classes.class_id) &
             (db.class_grade.class_id==class_id) &
             (db.class_grade.grade_id==db.grade.id) &
#             (db.student_classes.student_id==db.student.id) &
#             (db.student.user_id==db.auth_user.id) &
#             (db.student.id==db.student_grade.student_id) &
             (db.student_grade.grade_id==db.grade.id) &
             (db.grade.id==db.grade_standard.grade_id) &
             (db.standard.id==db.grade_standard.standard_id) &
             (db.standard.content_area == db.contentarea.id))

    standard_list = db(query).select(db.standard.id, db.standard.short_name, db.standard.reference_number,db.student_grade.student_score, db.grade.score)

    standard_dict = {}
    for row in standard_list:
        if row.standard.id in standard_dict.keys():
            if((row.grade.score != 0.0) | (row.student_grade.student_score != 0.0)):
                max_score = standard_dict[row.standard.id][0] + row.grade.score
                student_score = standard_dict[row.standard.id][1] + row.student_grade.student_score
                standard_dict[row.standard.id] = [max_score, student_score, row.standard.reference_number, row.standard.short_name]
        else:
            standard_dict[row.standard.id] = [row.grade.score, row.student_grade.student_score, row.standard.reference_number, row.standard.short_name]

    #To display due soon
    due_soon_amount = 3

    #Need to filter with current day datetime.datetime.now()
    due_soon_query = ((db.classes.id==class_id) &
             (db.gradebook.teacher==teacher_id) &
             (db.gradebook.classes==db.classes.id) &
             (db.class_grade.class_id==db.classes.id) &
             (db.class_grade.grade_id==db.grade.id) &
             (db.grade.due_date != None) &
             (db.grade.due_date > datetime.datetime.now()))

    due_soon = db(due_soon_query).select(db.grade.name, db.grade.due_date,orderby=db.grade.due_date)

    #If number of assignment is less than the number we want to display
    if(len(due_soon) < due_soon_amount):
        due_soon_amount = len(due_soon)

    return dict(class_name=class_name,
                class_id=class_id,
                total_students=total_students,
                total_grades=total_grades,
                total_score=total_score,
                total_possible=total_possible,
                average=average,
                standard_dict=standard_dict,
                due_soon=due_soon,
                due_soon_amount=due_soon_amount
               )
