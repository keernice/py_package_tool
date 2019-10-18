import os
import shutil
import config

tmp_cache_path = config.baseAbsPath + 'generateAPK/tmp/'


def copycover(src, dst):
    if os.path.isdir(src):
        if os.path.exists(dst):
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
    if os.path.isfile(src):
        if os.path.exists(dst):
            os.remove(dst)
        shutil.copy2(src, dst)
    pass


def recovery(apkname):
    src = tmp_cache_path + apkname + os.sep + 'res'
    dst = config.local_config['drawable_path']
    copycover(src, dst)

    src = tmp_cache_path + apkname + os.sep + 'AndroidManifest.xml'
    dst = config.local_config['manifest_xml']
    copycover(src, dst)
    pass


def backup(apkname):
    src = config.local_config['drawable_path']
    dst = tmp_cache_path + apkname + os.sep + 'res'
    copycover(src, dst)
    src = config.local_config['manifest_xml']
    dst = tmp_cache_path + apkname + os.sep + 'AndroidManifest.xml'
    copycover(src, dst)


def clear_tmp():
    if os.path.exists(tmp_cache_path):
        shutil.rmtree(tmp_cache_path)
