--unicode

from jnius import autoclass

PythonActivity = autoclass('org.kivy.android.PythonActivity')
String = autoclass('java.lang.String')
ArrayList = autoclass('java.util.ArrayList')

Permission = autoclass('android.Manifest$permission')

def request_permissions(permissions):
    activity = PythonActivity.mActivity
    perm_list = ArrayList()
    
    for perm in permissions:
        if perm == 'WRITE_EXTERNAL_STORAGE':
            perm_list.add(Permission.WRITE_EXTERNAL_STORAGE)
        elif perm == 'READ_EXTERNAL_STORAGE':
            perm_list.add(Permission.READ_EXTERNAL_STORAGE)
    
    if perm_list.size() > 0:
        activity.requestPermissions(perm_list.toArray(), 1)
