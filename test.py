from cgitb import text
import re

text='[] () []() test![[[[test](http://www.baidu.com/test.png)dsfsdfs![test](http://www.baidu.com/ok.png)dsf'

name_regex = "[^]]+"
# http:// or https:// followed by anything but a closing paren
url_regex = "http[s]?://[^)]+"

markup_regex = '!\[({0})]\(\s*({1})\s*\)'.format(name_regex, url_regex)

print([i[:-1].split('/')[-1] for i in re.findall('!\\[[^\\]]+\\]\\([^\\)]+\\)', text)])