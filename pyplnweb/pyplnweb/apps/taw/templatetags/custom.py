#-*- coding:utf-8 -*-
u"""

Module to define custom tags and filters

Created on 24/07/12
by fccoelho
license: GPL V3 or Later
"""

__docformat__ = 'restructuredtext en'

from django import template
from django.contrib.auth.models import User

register = template.Library()

@register.filter
def username_from_id(id):
    return User.objects.get(id=id).username
