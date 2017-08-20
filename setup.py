from setuptools import setup

setup(name='pySerialMonitor',
      version="0.1",
      url="https://github.com/RationalAsh/tk_serial_monitor",
      author="Ashwin Narayan",
      author_email="ashwinnarayan1994@gmail.com",
      license="MIT",
      packages=["pySerialMonitor"],
      install_requires=['rx', 'pyserial'],
      # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        #Type of program
        'Topic :: Terminals :: Serial',
        'Topic :: Communications',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
      ],
      entry_points = {
        'gui_scripts': ['tk-serial-monitor=pySerialMonitor.serial_monitor:main']
      },
      zip_safe=False)

