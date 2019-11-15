from setuptools import setup

install_requires = [
    'requests',
]

tests_require = [
    'pytest',
    'pytest-mock',
]

setup(
    name='intellipush',
    version='0.1.0',
    description='Client for accessing intellipush services.',
    package_dir={'intellipush': 'intellipush'},
    install_requires=install_requires,
    tests_require=tests_require,
)
