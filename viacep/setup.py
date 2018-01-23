from distutils.core import setup

setup(
    name='viacep',
    version='1.2.0',
    author='Leonardo Gregianin',
    author_email='leogregianin@gmail.com',
    scripts=['viacep.py', 'test_viacep.py', 'sample.py', 'README.md'],
    url='https://github.com/leogregianin/viacep-python',
    license='LICENSE',
    description='Consulta CEP pelo webservice do ViaCEP.com.br',
    long_description=open('README.md').read(),
    platforms = 'any',
    classifiers = [
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],	
)