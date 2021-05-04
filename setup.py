from distutils.core import setup


setup(
    name='bender',
    version='0.20.5b0',
    packages=['bender', 'bender.utils', 'bender.modules'],
    url='',
    license='',
    author='matousss',
    author_email='jaroslav.matous@student.gyarab.cz',
    description='Bender - Multipurpose Discord bot',
    entry_points={
        'console_scripts': [
            'bender = bender.__main__:main',
        ],
    },
    data_files=[('resources/locales/en/LC_MESSAGES', ['bender/resources/locales/en/LC_MESSAGES/messages.mo']),
                ('bender', ['bender/token.token'])],
)
