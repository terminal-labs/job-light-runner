from setuptools import setup

setup(
    name="jobrunner",
    version='0.1',
    py_modules=['app'],
    install_requires=[
        'requests',
        'flask',
        'Click',
        'cli-passthrough',
    ],
    entry_points='''
        [console_scripts]
        jobrunner=app:cli
    ''',
)
