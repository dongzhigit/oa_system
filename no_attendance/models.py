# -*- coding: utf-8 -*-
from django.db import models
# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
#
# Also note: You'll have to insert the output of 'django-admin sqlcustom [app_label]'
# into your database.
# from __future__ import unicode_literals

from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=80)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup)
    permission = models.ForeignKey('AuthPermission')

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType')
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=30)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser)
    group = models.ForeignKey(AuthGroup)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser)
    permission = models.ForeignKey(AuthPermission)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


#oa

class OaUser(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, blank=True, null=True)
    cn_name = models.CharField(max_length=100, blank=True, null=True)
    mail = models.CharField(max_length=50, blank=True, null=True)
    department = models.CharField(max_length=50, blank=True, null=True)
    position = models.CharField(max_length=50, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'oa_user'

class OaOrg(models.Model):
    id = models.IntegerField(primary_key=True)
    uid = models.ForeignKey('OaUser', db_column='uid', blank=True, null=True)
    # uid = models.ManyToManyField(OaUser, through='OaUserOrg',through_fields=('oauser', 'oaorg'))
    up_id = models.IntegerField(blank=True, null=True)
    org_name = models.CharField(max_length=100, blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'oa_org'

class OaUserOrg(models.Model):
    id = models.IntegerField(primary_key=True)
    # uid = models.ForeignKey(OaUser)
    # org = models.ForeignKey(OaOrg)
    uid = models.ForeignKey(OaUser, db_column='uid', blank=True, null=True)
    orgid = models.ForeignKey(OaOrg, db_column='orgid', blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'oa_user_org'

class OaApplyType(models.Model):
    type = models.CharField(max_length=25, blank=True, null=True)
    min_time = models.CharField(max_length=25, blank=True, null=True)
    max_time = models.CharField(max_length=25, blank=True, null=True)
    time_company = models.IntegerField(blank=True, null=True)
    enclosure = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'oa_apply_type'

class OaLeave(models.Model):
    uid = models.IntegerField(blank=True, null=True)
    department = models.CharField(max_length=25, blank=True, null=True)
    position = models.CharField(max_length=25, blank=True, null=True)
    leave_type = models.CharField(max_length=25, blank=True, null=True)
    begin_time = models.CharField(max_length=25, blank=True, null=True)
    end_time = models.CharField(max_length=25, blank=True, null=True)
    reason = models.CharField(max_length=25, blank=True, null=True)
    submit_time = models.CharField(max_length=25, blank=True, null=True)
    leave_time = models.CharField(max_length=25,blank=True, null=True)
    entry_time = models.CharField(max_length=25, blank=True, null=True)
    examine_status = models.CharField(max_length=25, blank=True, null=True)
    examine_level = models.IntegerField(blank=True, null=True)
    superior = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'oa_leave'

class OaLeaveLog(models.Model):
    log = models.ForeignKey(OaLeave, models.DO_NOTHING, blank=True, null=True)
    uid = models.IntegerField(blank=True, null=True)
    status = models.IntegerField(blank=True, null=True)
    datetime = models.DateTimeField(blank=True, null=True)
    last_uid = models.IntegerField(blank=True, null=True)
    outgoing_cause = models.CharField(max_length=25, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'oa_leave_log'

class OaEnclosure(models.Model):
    log = models.ForeignKey('OaLeave', models.DO_NOTHING, blank=True, null=True)
    filename = models.CharField(max_length=125, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'oa_enclosure'