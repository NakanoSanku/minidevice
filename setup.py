from setuptools import find_packages, setup

with open('README.md', 'r', encoding='utf-8') as fp:
    long_description = fp.read()

setup(name='minidevice',
      version='2.3.4',
      description='Android Auto Pypi',
      author='KateTseng',
      author_email='Kate.TsengK@outlook.com',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/NakanoSanku/minidevice',
      license='MIT',
      keywords='Android',
      project_urls={},
      packages=find_packages(),
      include_package_data=True,
      install_requires=['pyminitouch>=0.3.3',
                        "adbutils==1.2.9"
                        ],
      python_requires='>=3'
      )