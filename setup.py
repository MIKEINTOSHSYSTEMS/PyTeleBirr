from setuptools import setup

setup(
    name='pytelebirr',
    version='0.2.4',
    packages=['pytelebirr', 'pytelebirr.errors'],
    url='https://github.com/telebirrapi/pytelebirr',
    license='MIT License',
    author='wizkiye',
    author_email='wizkiye@gmail.com',
    description='Telebirr with python ',
    install_requires=[
        "asyncio",
        "requests",
        "websocket-client"
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
    ]
)
