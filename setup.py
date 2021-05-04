import setuptools

setuptools.setup(
    name='bender',
    version='0.20.5b0',
    packages=['bender', 'bender.utils', 'bender.modules', 'bender.modules.music'],
    url='',
    license='',
    author='matousss',
    author_email='jaroslav.matous@student.gyarab.cz',
    description='Bender - Multipurpose Discord bot',
    zip_safe=False,
    install_requires=[
        'discord.py~=1.7.1',
        'PyNaCl~=1.4.0',
        'youtube_dl~=2021.4.7'
    ],
    entry_points={
        'console_scripts': [
            'bender = bender.__main__:main',
        ],
    },
    data_files=[('resources/locales/en/LC_MESSAGES', ['resources/locales/en/LC_MESSAGES/messages.mo']),
                ('resources/locales/cs/LC_MESSAGES', ['resources/locales/cs/LC_MESSAGES/messages.mo'])]

)
