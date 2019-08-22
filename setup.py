from distutils.core import setup

setup(
    name='scrapegaff',
    description='Giffgaff web scraper',
    version='1.0',
    author='Jamie Lentin',
    author_email='jm@lentin.co.uk',
    license='MIT',
    py_modules=['scrapegaff'],

    install_requires=[
        'docopt',
        'lxml',
        'requests',
    ],

    entry_points={
        'console_scripts': [
            'scrapegaff=scrapegaff:script',
        ],
    },
)
