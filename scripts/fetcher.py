# -*- coding: utf-8 -*-
#!/home/environments/natourpress/bin/python

from django_imports import User

#==============================================================================================
if __name__ == '__main__':

    for user in User.objects.all():
        print user.email


