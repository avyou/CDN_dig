import os
from setuptools import setup,find_packages


data_dir = ['/usr/local/cdn_dig/data','/usr/local/cdn_dig/etc']

for idir in data_dir:
    if not os.path.exists(idir):
        os.makedirs(idir)

s = '''[easy_install]
index-url=http://pypi.douban.com/simple
'''
s_file = os.path.join(os.environ['HOME'],'.pydistutils.cfg')

writed = 0
if not os.path.exists(s_file):
    writed = 1
    with open(s_file,'w') as f:
        f.write(s)

setup(
    name='cdn_dig',
    version='1.0',
    description='EDNS dig is used to query where the client IP of request is dispatched for CDN',
    long_description=open(
        os.path.join(
            os.path.dirname(__file__),
            'README.rst'
        )
    ).read(),
    author='avyou',
    author_email='avyou55@gmail.com',
    include_package_data = True,

    install_requires = [
        "prettytable>=0.7.2",
        "termcolor>=1.1.0",
        "simplejson>=3.13.2",
        "lxml>=4.1.1",
        "tqdm>=4.19.5",
    ],

    url='https://github.com/avyou/cdn_dig',

    packages = find_packages(),

    entry_points = {
        'console_scripts' : [
            'cdig = cdn_dig.cdig:main',
            'whereip = cdn_dig.whereip:main'
        ],
    },
    package_data = {'cdn_dig': ["data/*"]},

    data_files = [
                   ('/usr/local/cdn_dig/data/',['cdn_dig/data/ip_dns_isp.list']),
                   ('/usr/local/cdn_dig/data/',['cdn_dig/data/ipipdb.dat']),
                   ('/usr/local/cdn_dig/data/',['cdn_dig/data/qqwry.dat']),
                   ('/usr/local/cdn_dig/etc/',['cdn_dig/data/config.ini'])
    ],

    license='MIT'
)

if writed == 1:
    os.remove(s_file)
