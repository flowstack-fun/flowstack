from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="flowstack",
    version="1.0.0",
    author="FlowStack",
    author_email="hello@flowstack.ai",
    description="AI Agent Platform SDK with built-in billing management",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/flowstack/python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
        ],
    },
    entry_points={
        "console_scripts": [
            "flowstack=flowstack.cli:main",
        ],
    },
    keywords="ai, agents, llm, openai, anthropic, bedrock, aws",
    project_urls={
        "Bug Reports": "https://github.com/flowstack/python-sdk/issues",
        "Source": "https://github.com/flowstack/python-sdk",
        "Documentation": "https://docs.flowstack.ai",
    },
)