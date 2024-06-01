from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fp:
    long_description = fp.read()

setup(
    name="minidevice",
    version="0.0.1",
    description="Android Auto Pypi",
    author="KateTseng",
    author_email="Kate.TsengK@outlook.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NakanoSanku/minidevice",
    license="MIT",
    keywords="Android",
    project_urls={},
    packages=find_packages(),
    include_package_data=True,
    package_data={
        # 如果你的bin文件在minidevice包下，可以这样指定
        'minidevice': ['bin/*'],
        # 如果bin文件不在包内，也可以直接指定路径
        # '': ['bin/*'],
    },
    install_requires=["adbutils", "loguru>=0.6.0", "requests"],
    python_requires=">=3",
)
