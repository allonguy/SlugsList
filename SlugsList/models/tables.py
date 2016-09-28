# -*- coding: utf-8 -*-

from datetime import datetime
from time import time


def get_first_name():
    fname = ''
    if auth.user:
        fname = auth.user.first_name
    return fname

def get_last_name():
    lname = ''
    if auth.user:
        lname = auth.user.last_name
    return lname


LOOKING_FOR = ['Study group', 'Tutor', 'Someone to Tutor']
CLASS_LEVEL = ['Freshman', 'Sophomore', 'Junior', 'Senior']

#
# List of UCSC majors
#
db.define_table('majors',
                Field('name'),
                Field('abbreviation'),
                format = '%(name)s'
               )
db.define_table('ucsc_classes',
                Field('name'),
                Field('major', db.majors),
                format = '%(name)s',
               )

#
# List of students signed up
#
db.define_table('students',
                Field('user_id', db.auth_user, readable = False),
                Field('first_name', default = get_first_name() ),
                Field('last_name', default = get_last_name() ),
                Field('class_level', requires = IS_IN_SET(CLASS_LEVEL)),
                Field('major', db.majors),
                Field('minor', db.majors),
                Field('email', requires=IS_EMAIL()),
                Field('class_list', 'list:reference ucsc_classes'),
                Field('bio', 'text')
               )
db.students.id.readable = False;

#
# Posts associated with each student
#
db.define_table('student_posts',
                Field('student_id', db.students),
                Field('last_updated', 'datetime'),
                Field('looking_for_tutor', 'list:reference ucsc_classes'),
                Field('can_tutor', 'list:reference ucsc_classes'),
                Field('study_group', 'list:reference ucsc_classes'),
                Field('body', 'text')
               )
#
# Matches
# This keeps track of matches between students
#
# A match being active for a particular student means that their most recent post
# is what matched with the other person. If the student is active in a conversation
# with the other person and they change their post such that they no longer match, the
# match is still considered active. If there is no conversation and the match no longer
# exists, it will be considered inactive and can only be accessed from the "Matches" page.
# A match is only removed if the user manually selects to remove the match.
#
db.define_table('matches',
                Field('student1_id', db.students),
                Field('student2_id', db.students),
                Field('student1_active', 'boolean'),
                Field('student2_active', 'boolean')
               )

#
# Threads
# This keeps conversations in the same chain together
#
db.define_table('threads',
                Field('subject'),
                Field('match_id', db.matches)
               )

#
# Messages
#
db.define_table('messages',
                Field('thread_id', db.threads),
                Field('num_in_thread','integer' , default = 1 ), # 1 is first message, 2 is first reply, etc
                Field('sender_id', db.students),
                Field('recipient_id', db.students),
                Field('send_time', 'datetime',default = datetime.utcnow()),
                Field('body'),
                Field('viewed', 'boolean')
               )

db.define_table('reviews',
                Field('class_name', db.ucsc_classes),
                Field('review_text', 'list:string'), # Review only max of 512 characters
                )
