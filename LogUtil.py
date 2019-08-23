#  Author : yanke
#  Date   : 2019-08-22

def error(msg):
    msg = '\033[0;31;47m' + 'Error: ' + msg + '\033[0m'
    print(msg)


def warning(msg):
    msg = '\033[0;31;47m' + 'Warning: ' + msg + '\033[0m'
    print(msg)
