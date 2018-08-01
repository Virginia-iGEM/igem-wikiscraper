import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = 'igemwikiscraper',
    version = '0.5.0',
    description = 'GUI+CLI+Library webscraper built specifically for iGEM team wiki pages',
    long_description = long_description,
    long_description_content_type='text/markdown',
    url = 'https://github.com/Virginia-iGEM/igem-wikiscraper',
    author='Dylan Culfogienis',
    author_email='dtc9bb@virginia.edu',
    license='MIT',
    packages=['igemwikiscraper'],
    classifiers=(
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Science/Research',
        'Operating System :: OS Independent'
    ),
    install_requires = [
        'requests', 
        'beautifulsoup4',
        'lxml',
        'gooey>=1.0.1'
    ],
    entry_points = {
        'console_scripts': [
            'wikiscraper=igemwikiscraper.__main__:main',
            'wikiscraper-gui=igemwikiscraper.__main__:gui'
        ]
    }
)
