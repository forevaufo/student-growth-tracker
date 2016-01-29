# -*- coding: utf-8 -*-
# try something like

def index(): 
    if auth.has_membership(1, auth.user_id):
        pass
    else:
        redirect(URL('default','index'))

    return dict()

def classes_create():
    if auth.has_membership(1, auth.user_id):
        pass
    else:
        redirect(URL('default','index'))

    form = SQLFORM.factory(db.classes, submit_button='Create Class')
    return dict(form=form)


def teacher_create():
    if auth.has_membership(1, auth.user_id):
        pass
    else:
        redirect(URL('default','index'))

    query = ((db.auth_group.id == 2))
    role_field = Field('Account_Type', requires=IS_IN_DB(db(query), 'auth_group.id', '%(role)s', zero = None))
    form = SQLFORM.factory(db.auth_user, role_field, submit_button='Create Teacher')

    if form.process().accepted:
        id = db.auth_user.insert(**db.auth_user._filter_fields(form.vars))
        db.auth_membership.insert(user_id = id, group_id = 2)

    return dict(form=form)




def student_create():
    if auth.has_membership(1, auth.user_id):
        pass
    else:
        redirect(URL('default','index'))

    query = ((db.auth_group.id == 3))
    role_field = Field('Account_Type', requires=IS_IN_DB(db(query), 'auth_group.id', '%(role)s', zero = None))
    school_id_field = Field("School_ID_Number")
    grade_level_field = Field("Grade_Level")
    home_field = Field("Home_Address")
    parent_email_field = Field("Parent_Email")
    form = SQLFORM.factory(db.auth_user, role_field, school_id_field, grade_level_field, home_field, parent_email_field, submit_button='Create Student')

    if form.process().accepted:
        id = db.auth_user.insert(**db.auth_user._filter_fields(form.vars))
        db.auth_membership.insert(user_id = id, group_id = 3)
        db.student.insert(user_id = id,
                          school_id_number = form.vars.School_ID_Number,
                          grade_level = form.vars.Grade_Level,
                          home_address = form.vars.Home_Address,
                          parent_email = form.vars.Parent_Email)

    return dict(form=form)




def parent_create():
    if auth.has_membership(1, auth.user_id):
        pass
    else:
        redirect(URL('default','index'))

    query = ((db.auth_group.id == 4))
    role_field = Field('Account_Type', requires=IS_IN_DB(db(query), 'auth_group.id', '%(role)s', zero = None))
    form = SQLFORM.factory(db.auth_user, role_field, submit_button='Create Parent')

    if form.process().accepted:
        id = db.auth_user.insert(**db.auth_user._filter_fields(form.vars))
        db.auth_membership.insert(user_id = id, group_id = 4)

    return dict(form=form)




def assign_teacher_to_class():
    if auth.has_membership(1, auth.user_id):
        pass
    else:
        redirect(URL('default','index'))

    teacher_query = ((db.auth_group.id == 2)&
            (db.auth_membership.group_id == db.auth_group.id)&
            (db.auth_membership.user_id == db.auth_user.id))
    teacher_field = Field("Teacher",  requires=IS_IN_DB(db(teacher_query), "auth_user.id", '%(first_name)s'+' ' + '%(last_name)s', zero = None))

    class_query = ((db.classes.id > 0))
    class_field = Field("Class",  requires=IS_IN_DB(db(class_query), "classes.id", '%(name)s', zero = None))

    form = SQLFORM.factory(teacher_field, class_field, submit_button='Assign To Class')

    if form.process().accepted:
        row = db.gradebook(teacher = form.vars.Teacher, classes = form.vars.Class)
        if not row:
            db.gradebook.insert(teacher = form.vars.Teacher, classes = form.vars.Class)
        else:
            response.flash = "Already Exist"
            pass


    return dict(form=form)




def assign_student_to_class():
    if auth.has_membership(1, auth.user_id):
        pass
    else:
        redirect(URL('default','index'))

    student_query = ((db.student.id > 0))
    student_field = Field("Student",  requires=IS_IN_DB(db(student_query), "student.id", '%(school_id_number)s', zero = None))

    class_query = ((db.classes.id > 0))
    class_field = Field("Class",  requires=IS_IN_DB(db(class_query), "classes.id", '%(name)s', zero = None))

    form = SQLFORM.factory(student_field, class_field, submit_button='Assign To Class')


    if form.process().accepted:
        row = db.student_classes(student_id = form.vars.Student, class_id = form.vars.Class)
        if not row:
            db.student_classes.insert(student_id = form.vars.Student, class_id = form.vars.Class)
        else:
            response.flash = "Already Exist"
            pass

    return dict(form=form)

def assign_parent_to_student():
    if auth.has_membership(1, auth.user_id):
        pass
    else:
        redirect(URL('default','index'))

    parent_query = ((db.auth_group.id == 4)&
            (db.auth_membership.group_id == db.auth_group.id)&
            (db.auth_membership.user_id == db.auth_user.id))
    parent_field = Field("Parent",  requires=IS_IN_DB(db(parent_query), "auth_user.id", '%(first_name)s'+' ' + '%(last_name)s', zero = None))

    student_query = ((db.student.id > 0))
    student_field = Field("Student",  requires=IS_IN_DB(db(student_query), "student.id", '%(school_id_number)s', zero = None))

    form = SQLFORM.factory(parent_field, student_field, submit_button='Assign To Student')


    if form.process().accepted:
        row = db.parent_student(parent_id = form.vars.Parent, student_id = form.vars.Student)
        if not row:
            db.parent_student.insert(parent_id = form.vars.Parent , student_id = form.vars.Student)
        else:
            response.flash = "Already Exist"
            pass

    return dict(form=form)



def standard_overview():
    grade_query = ((db.classes.grade_level))
    grade = db(grade_query).select(db.classes.grade_level)
    grade_list = []
    for row in grade:
        grade_list.append(row.grade_level)
    grade_list = list(set(grade_list))
    #print(grade_list)

    overview_data = {}
    for grade in grade_list:
        standard_query = ((db.classes.grade_level == grade)&
                          (db.classes.id == db.student_classes.class_id)&
                          (db.student.id == db.student_classes.student_id)&
                          (db.student.id == db.student_grade.student_id)&
                          (db.grade.id == db.student_grade.grade_id)&
                          (db.grade.id == db.grade_standard.grade_id)&
                          (db.standard.id == db.grade_standard.standard_id)&
                          (db.classes.id == db.class_grade.class_id)&
                          (db.grade.id == db.class_grade.grade_id)&
                          (db.standard.content_area == db.contentarea.id))

        standard_list = db(standard_query).select(db.standard.id, db.standard.short_name, db.standard.reference_number,db.student_grade.student_score, db.grade.score)

        standard_dict = {}
        for row in standard_list:
            if row.standard.id in standard_dict.keys():
                if((row.grade.score != 0.0) | (row.student_grade.student_score != 0.0)):
                    max_score = standard_dict[row.standard.id][0] + row.grade.score
                    student_score = standard_dict[row.standard.id][1] + row.student_grade.student_score
                    standard_dict[row.standard.id] = [max_score, student_score, row.standard.reference_number, row.standard.short_name]
            else:
                standard_dict[row.standard.id] = [row.grade.score, row.student_grade.student_score, row.standard.reference_number, row.standard.short_name]

        overview_data[grade] = standard_dict


    return dict(overview_data = overview_data)
