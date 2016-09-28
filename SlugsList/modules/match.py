#!/usr/bin/env python
# -*- coding: utf-8 -*-
from gluon import *

#
# Both parameters must be database entries from the db.students table
#
# Members:
#  * looking_for_tutor: student1 needs a tutor in one of student2's classes
#  * can_tutor: student1 can tutor classes for student2
#  * study_group: both students want a study group for this class
#
class looking_for_id_lists():
    def __init__(self, db, student1, student2):
        student1_post = db(db.student_posts.student_id == student1.id).select().first()
        student2_post = db(db.student_posts.student_id == student2.id).select().first()

        self.looking_for_tutor = list(set(student1_post.looking_for_tutor) & set(student2_post.can_tutor))
        self.can_tutor = list(set(student1_post.can_tutor) & set(student2_post.looking_for_tutor))
        self.study_group = list(set(student1_post.study_group) & set(student2_post.study_group))
        self.students_match = (len(self.looking_for_tutor) > 0 or len(self.can_tutor) > 0 or len(self.study_group) > 0)

#
# Returns the links to a particular user's profile, post, the conversation with them, and the page
# to unmatch with them. This only works if the student matches the logged-in user; if not, all links
# are made to be done.
#
# Members:
#  * name_link:    link to default/profile, with db.student.user_id as a var
#  * post_link:    link to default/post, with db.student.id as a var
#  * chat_link:    link to default/conversation, with db.match.id as a var
#  * unmatch_link: link to default/unmatch, with db.match.id as a var
#
class match_links():
    def __init__(self, db, auth, student_id):
        me = db(db.students.user_id == auth.user_id).select().first() or None
        if me == None:
            self.name_link = None
            self.post_link = None
            self.chat_link = None
            self.unmatch_link = None
        else:
            match = db((db.matches.student1_id == student_id) & (db.matches.student2_id == me.id)).select().first() or None
            if match == None:
                match = db((db.matches.student1_id == me.id) & (db.matches.student2_id == student_id)).select().first() or None
            if match == None:
                self.name_link = None
                self.post_link = None
                self.chat_link = None
                self.unmatch_link = None
            else:
                student = db.students(student_id) or None
                if student == None:
                    self.name_link = None
                    self.post_link = None
                    self.chat_link = None
                    self.unmatch_link = None
                else:
                    student_name = student.first_name
                    self.name_link = A(student_name, _href=URL('default', 'profile', vars=dict(id=student.user_id)))
                    self.post_link = A('View Post', _href=URL('default', 'post', vars=dict(id=student.id)))
                    self.chat_link = A('Chat', _href=URL('default', 'conversation', vars=dict(id=match.id)))
                    self.unmatch_link = A('X', _href=URL('default', 'unmatch', vars=dict(id=match.id)))

#
# Return all information associated with the student with the given ID. Only works for users with whom
# you match.
#
# Members:
#  * me: db.students entry for logged-in user
#  * other_student: db.students entry for student with given ID
#  * links: match_links instance for student with given ID
#  * match_classes: looking_for_id_lists between yourself and student with given ID
#  * looking_for_tutor_str: list of classes for which you are looking for a tutor, separated by commas
#  * can_tutor_str: list of classes you can tutor, separated by commas
#  * study_group_str: list of class for which you are looking for a study group, separated by commas
#
# Functions:
#  * get_class_string: take in a list of class ID's and return a string of their names, separated by commas
#
class matched_student():
    def __init__(self, db, auth, student_id):
        self.me = db(db.students.user_id == auth.user_id).select().first() or None
        self.other_student = db.students(student_id) or None
        self.links = match_links(db, auth, student_id)
        if self.me == None or self.other_student == None:
            self.match_classes = None
            self.looking_for_tutor_str = None
            self.can_tutor_str = None
            self.study_group_str = None
            self.looking_for_tutor_ul = None
            self.can_tutor_ul = None
            self.study_group_ul = None
        else:
            self.match_classes = looking_for_id_lists(db, self.me, self.other_student)
            self.looking_for_tutor_str = self.get_class_string(db, self.match_classes.looking_for_tutor)
            self.can_tutor_str = self.get_class_string(db, self.match_classes.can_tutor)
            self.study_group_str = self.get_class_string(db, self.match_classes.study_group)
            self.looking_for_tutor_ul = self.get_class_UL(db, self.match_classes.looking_for_tutor)
            self.can_tutor_ul = self.get_class_UL(db, self.match_classes.can_tutor)
            self.study_group_ul = self.get_class_UL(db, self.match_classes.study_group)

    def get_class_string(self, db, id_list):
        class_string = ""
        for id in id_list:
            class_string += "%s, " % db(db.ucsc_classes.id == id).select().first().name
        class_string = class_string[:-2]
        return class_string

    def get_class_UL(self, db, id_list):
        ul = UL()
        for num,id in enumerate(id_list):
            ul.insert(num, db(db.ucsc_classes.id == id).select().first().name)
        return ul
