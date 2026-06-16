from setuptools import setup, find_packages

setup(
    name="maritime_mcp_package",
    version="0.1.0",               
    packages=find_packages(),      
    install_requires=[
        "mcp>=1.0.0",
        "fastmcp>=0.4.1",
        "langgraph>=0.1.0",
        "langchain-core",
        "langchain-google-genai",
        "python-dotenv",
        "chromadb>=0.5.0",
        "sentence-transformers>=3.0.0",
        "langchain-community>=0.0.1",
    ],
)
