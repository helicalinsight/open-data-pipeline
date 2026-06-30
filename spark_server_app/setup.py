from setuptools import setup, find_packages

if __name__ == '__main__':
    setup(
        name="spark_server",
        version="1.0",
        packages=find_packages(),
        install_requires=[
            "pyspark==3.3.3",
            "pymongo==4.6.1", 
            "mongomock==4.1.2",
            "bson==0.5.10",
            "pandas==2.0.3",
            "pyyaml==6.0.1",
        ],
        python_requires=">=3.8",
    )
