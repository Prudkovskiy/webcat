import os

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/"
    "537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
)
PROXY_URL = os.getenv(
    "PROXY_URL",
    "",
)
S3_ACCESS_KEY_ID = os.getenv("S3_ACCESS_KEY_ID", "")
S3_SECRET_ACCESS_KEY_ID = os.getenv("S3_SECRET_ACCESS_KEY_ID", "")
CONFIG_S3 = {
    "remote": {
        "mls3": {
            "access_key_id": S3_ACCESS_KEY_ID,
            "secret_access_key": S3_SECRET_ACCESS_KEY_ID,
        },
    },
}

MODEL_MYIP_URL_PATH = "models/my_ip_models/"

CATEGORIES_LIST = [
    "Internet and Telecom",
    "Arts and Entertainment",
    "Business and Industry",
    "Travel",
    "Health",
    "Games",
    "People and Society",
    "Finance",
    "Sports",
    "News and Media",
    "Career and Education",
    "Gambling",
    "Food and Drink",
    "Autos and Vehicles",
    "Law and Government",
    "Adult",
    "Reference",
    "Online Technologies",
    # "Malicious webpages",
    "Shopping",
    "Advertising",
    "Info Security",
    "Real Estate",
    "Religion",
    "Alcohol and Tobacco",
    "Hosting and Sharing",
    "Organizations",
    "Meaningless Content",
]
NUM_CATEGORIES = len(CATEGORIES_LIST)
