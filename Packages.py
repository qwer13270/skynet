import subprocess

# List of packages to be installed
packages = [
    "Flask",
    "Flask-CORS",
    "python-dotenv",
    "PyJWT",
    "psycopg2",
    "Flask-SQLAlchemy",
    "scrapy",
    "selenium",
    "beautifulsoup4",
    "pandas",
    "tqdm",
    "openpyxl"
]


# Function to install packages
def install_packages(packages):
    for package in packages:
        subprocess.run(["pip", "install", package])


# Run the installation
if __name__ == "__main__":
    install_packages(packages)
