#!/usr/bin/env python

import setuptools


setuptools.setup(
  name='memory-tools',
  version='1.0.3',

  author='Max Zheng',
  author_email='maxzheng.os @t gmail.com',

  description='A set of simple yet effective tools to troubleshoot memory leaks.',
  long_description=open('README.rst').read(),

  url='https://github.com/maxzheng/memory-tools',

  entry_points={
    'console_scripts': [
      'show-mem = memorytools.show_mem:main',
      'loop = memorytools.loop:main',
    ],
  },

  install_requires=open('requirements.txt').read(),

  license='MIT',

  package_dir={'': 'src'},
  packages=setuptools.find_packages('src'),
  include_package_data=True,

  setup_requires=['setuptools-git'],

  classifiers=[
    'Development Status :: 5 - Production/Stable',

    'Intended Audience :: Developers',
    'Topic :: Software Development',

    'License :: OSI Approved :: MIT License',

    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
  ],

  keywords='memory tools leaks profiler simple easy to use process usage private rss total',
)
