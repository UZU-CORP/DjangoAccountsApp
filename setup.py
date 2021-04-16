from setuptools import setup, find_packages
import pathlib

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

setup(
    name = 'uzu-django-accounts',  
    version = '0.1.1',      
    license='MIT',        
    description = 'Uzu-django-accounts is a generic django application tailored to Single Page Applications that abstracts user authentication and verification from the rest of your project.',
    long_description_content_type = "text/markdown",
    long_description = README,
    author = 'Darlington Onyemere',                   
    author_email = 'DarlingtonOnyemere@uzucorp.com',      
    url = 'https://github.com/UZU-CORP/DjangoAccountsApp.git',       
    keywords = ['Authentication', 'Django', 'Account Verification'],   
    classifiers=[
        'Development Status :: 3 - Alpha',      
        'Intended Audience :: Developers',      
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',   
        'Programming Language :: Python :: 3',      
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=["django", "htmailer", "djangorestframework", "pyotp"],
    packages=find_packages(exclude=("AccountsApp.tests",)),
    package_data = {
        '': ['*.html', '*.txt'],
    },
)
