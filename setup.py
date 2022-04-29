from setuptools import setup, find_packages

setup(
    name="jobrunner",
    version='0.1',
    install_requires=[
        'pyyaml',
        'requests',
        'flask',
        'Click',
        'cli-passthrough',
    ],
    packages=find_packages(),
    entry_points='''
        [console_scripts]
        jobrunner=jobrunner.core:cli
    ''',
)
