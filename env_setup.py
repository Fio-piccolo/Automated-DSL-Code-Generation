# install_env.py

import os

packages = [
    "PyYAML==6.0.2",
    "absl-py==2.2.2",
    "aiohappyeyeballs==2.6.1",
    "aiohttp==3.11.16",
    "aiosignal==1.3.2",
    "annotated-types==0.7.0",
    "anyio==4.9.0",
    "attrs==25.3.0",
    "certifi==2025.1.31",
    "charset-normalizer==3.4.1",
    "click==8.1.8",
    "codebleu==0.7.0",
    "colorama==0.4.6",
    "datasets==3.5.0",
    "dill==0.3.8",
    "distro==1.9.0",
    "evaluate==0.4.3",
    "filelock==3.18.0",
    "frozenlist==1.5.0",
    "fsspec==2024.12.0",
    "h11==0.14.0",
    "httpcore==1.0.7",
    "httpx==0.28.1",
    "huggingface-hub==0.30.2",
    "idna==3.10",
    "jiter==0.9.0",
    "joblib==1.4.2",
    "multidict==6.2.0",
    "multiprocess==0.70.16",
    "nltk==3.9.1",
    "numpy==2.2.4",
    "openai==1.71.0",
    "packaging==24.2",
    "pandas==2.2.3",
    "pip==23.2.1",
    "propcache==0.3.1",
    "pyarrow==19.0.1",
    "pydantic==2.11.2",
    "pydantic_core==2.33.1",
    "python-dateutil==2.9.0.post0",
    "pytz==2025.2",
    "regex==2024.11.6",
    "requests==2.32.3",
    "rouge_score==0.1.2",
    "setuptools==78.1.0",
    "six==1.17.0",
    "sniffio==1.3.1",
    "tqdm==4.67.1",
    "tree-sitter==0.23.1",
    "tree-sitter-python==0.23.6",
    "typing-inspection==0.4.0",
    "typing_extensions==4.13.1",
    "tzdata==2025.2",
    "urllib3==2.3.0",
    "xxhash==3.5.0",
    "yarl==1.19.0"
]

for package in packages:
    print(f"🔧 Installing {package}...")
    os.system(f"pip install {package}")

print("\n✅ All packages installed successfully!")
