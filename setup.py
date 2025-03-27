from setuptools import setup, find_packages

setup(
    name="bohoc",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi==0.109.2",
        "uvicorn==0.22.0",
        "sqlalchemy==2.0.23",
        "pydantic==2.6.1",
        "python-jose==3.3.0",
        "passlib==1.7.4",
        "python-multipart==0.0.6",
        "psycopg2-binary==2.9.6",
        "python-dotenv==1.0.0",
        "email-validator==2.0.0",
    ],
    extras_require={
        "test": [
            "pytest==8.0.2",
            "pytest-asyncio==0.23.5",
            "httpx==0.27.0",
            "pytest-cov==4.1.0",
        ],
    },
) 