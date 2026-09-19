"""
NetScan — Setup & Installation Script
Author: Mohamed Reda QIYAOUI
Unsupervised Machine Learning Network Intrusion Detection System (NIDS)
"""

from setuptools import setup, find_packages
import os

readme_path = os.path.join(os.path.dirname(__file__), "README.md")
long_description = ""
if os.path.exists(readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        long_description = f.read()

setup(
    name="netscan",
    version="1.0.0",
    author="Mohamed Reda QIYAOUI",
    author_email="m.qiyaoui@student.est.ma",
    description="Unsupervised Machine Learning Network Intrusion Detection System (NIDS)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Medreda-q/NetScan",
    packages=find_packages(),
    py_modules=[
        "detection_engine",
        "dashboard",
        "netscan",
        "alerting",
        "report_generator",
    ],
    install_requires=[
        "pandas",
        "scapy",
        "pyshark",
        "scikit-learn",
        "matplotlib",
        "streamlit",
    ],
    entry_points={
        "console_scripts": [
            "netscan=netscan:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Topic :: System :: Networking :: Monitoring",
    ],
    python_requires=">=3.8",
)
