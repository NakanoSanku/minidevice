from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fp:
    long_description = fp.read()

setup(
    name="minidevice-mumuapi",
    version="0.0.1",
    description="基于minidevice的dlc拓展mumu12操作api工具",
    author="KateTseng",
    author_email="Kate.TsengK@outlook.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NakanoSanku/minidevice-mumuapi",
    license="MIT",
    keywords="Android",
    project_urls={},
    packages=find_packages(),
    include_package_data=True,
    install_requires=["opencv-python", "minidevice"],
    python_requires=">=3",
)
