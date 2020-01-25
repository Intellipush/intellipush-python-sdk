from setuptools import setup

install_requires = [
    'requests',
]

tests_require = [
    'pytest',
    'pytest-mock',
]

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name='intellipush',
    version='0.2.0',
    author='Mats Lindh',
    description='Client for accessing the intellipush message service.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    package_dir={'intellipush': 'intellipush'},
    packages=['intellipush'],
    url='https://www.intellipush.com/',
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require={
        'dev': [
            'sphinx',
            'sphinx-rtd-theme',
            'twine',
        ]
    }
)
