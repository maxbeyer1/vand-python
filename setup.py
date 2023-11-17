from setuptools import setup

setup(
    name="vand-python",
    packages=["vand-python"],  # this must be the same as the name above
    version="0.1.0",
    description="A Python package for easily finding and using tools (functions) to augment AI models (LLM)",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Vand",
    author_email="info@vand.io",
    url="https://github.com/vand-io/vand-python",
    keywords=["chatgpt", "openai", "ai", "vand", "functions", "tools"],
    classifiers=[],
    license="MIT",
    entry_points={},
    python_requires=">=3.10",
    install_requires=[
        "orjson>=3.9.0",
    ],
)