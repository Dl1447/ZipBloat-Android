--unicode

from jnius import autoclass

PythonActivity = autoclass('org.kivy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
Environment = autoclass('android.os.Environment')

def primary_external_storage_path():
    return Environment.getExternalStorageDirectory().getAbsolutePath()

def open_file_dialog():
    intent = Intent(Intent.ACTION_GET_CONTENT)
    intent.setType("*/*")
    intent.addCategory(Intent.CATEGORY_OPENABLE)
    PythonActivity.mActivity.startActivityForResult(intent, 1)

def save_file_dialog():
    intent = Intent(Intent.ACTION_CREATE_DOCUMENT)
    intent.setType("application/zip")
    intent.addCategory(Intent.CATEGORY_OPENABLE)
    PythonActivity.mActivity.startActivityForResult(intent, 2)
