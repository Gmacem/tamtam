from setuptools import setup, find_packages
from os.path import join, dirname
import tamtam

setup(
    name='tamtam',
    version=tamtam.__version__,
    description='intagration with TamTam',
    long_description=open(join(dirname(__file__), 'README.rst')).read(),
    classifiers=['Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3.7',
                 'Topic :: Inegration :: TamTam', ],
    keywords='REST confluence',
    url='http://github.com/xvlady/tamtam', author='Vladimir Khonin',
    author_email='xvlady5@gmail.com',
    license='MIT',
    packages=find_packages(),
    install_requires=['requests', 're'],
    include_package_data=True,
    zip_safe=False,
    test_suite='tests',
)
