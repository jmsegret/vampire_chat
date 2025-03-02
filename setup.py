from setuptools import setup, find_packages

# Read the contents of README file
with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="vampire-chat",
    version="0.1.0",
    packages=find_packages(exclude=["tests*", "docs*"]),
    install_requires=[
        "gradio>=4.0.0",
        "openai>=1.0.0",
        "python-dotenv>=1.0.0",
        "faiss-cpu>=1.7.4",
        "sentence-transformers>=2.2.2",
        "numpy>=1.24.0",
        "SpeechRecognition>=3.10.0",
        "sounddevice>=0.4.6",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "isort>=5.0.0",
            "mypy>=0.900",
        ],
        "docs": [
            "sphinx>=4.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "vampire-chat=vampire_chat.app.main:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A chat application featuring Lilly, the friendly teenage vampire",
    long_description=long_description,
    long_description_content_type="text/markdown",
    keywords="chat, ai, vampire, openai, gradio",
    url="https://github.com/yourusername/vampire-chat",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/vampire-chat/issues",
        "Documentation": "https://vampire-chat.readthedocs.io/",
        "Source Code": "https://github.com/yourusername/vampire-chat",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Communications :: Chat",
    ],
    python_requires=">=3.8",
    include_package_data=True,
    zip_safe=False,
) 