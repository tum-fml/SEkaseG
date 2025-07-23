import shutil
import os

def save_version(directory, back_button):
    src = os.path.join(directory, 'current')
    dst = os.path.join(directory, 'back')
    shutil.rmtree(dst)
    shutil.copytree(src, dst)
    back_button['state'] = 'enabled'

def go_back(directory, back_button, forth_button):
    back = os.path.join(directory, 'back')
    forth = os.path.join(directory, 'forth')
    current = os.path.join(directory, 'current')
    shutil.rmtree(forth)
    shutil.copytree(current, forth)
    shutil.rmtree(current)
    shutil.copytree(back, current)
    shutil.rmtree(back)
    os.makedirs(os.path.join(directory, 'back'))
    back_button['state'] = 'disabled'
    forth_button['state'] = 'enabled'

def go_forth(directory, back_button, forth_button):
    back = os.path.join(directory, 'back')
    forth = os.path.join(directory, 'forth')
    current = os.path.join(directory, 'current')
    shutil.rmtree(back)
    shutil.copytree(current, back)
    shutil.rmtree(current)
    shutil.copytree(forth, current)
    shutil.rmtree(forth)
    os.makedirs(os.path.join(directory, 'forth'))
    back_button['state'] = 'enabled'
    forth_button['state'] = 'disabled'