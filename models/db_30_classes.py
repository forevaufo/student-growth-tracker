# -*- coding: utf-8 -*-

db.define_table(
    'classes',
    Field('name', required=True, requires=IS_NOT_EMPTY()),
    Field('gradeLevel', 'integer', required=True, requires=IS_NOT_EMPTY()),
    Field('startDate', 'integer', required=True, requires=IS_NOT_EMPTY()),
    Field('endDate', 'integer', required=True, requires=IS_NOT_EMPTY()),
    # studentList Obj
    #Field('studentList', 'reference student'),
    Field('studentList'),
    # grade Obj
    #Field('grade', 'reference grade'),
    Field('grade'),
    # content area Obj
    #Field('content_area', 'reference contentarea'),
    Field('content_area'),
    format = '%(name)s')

db.classes.id.readable = db.classes.id.writable = False
