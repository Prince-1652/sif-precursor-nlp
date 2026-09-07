import os
import urllib.request
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_fasttext_model():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    models_dir = os.path.join(base_dir, "models")
    os.makedirs(models_dir, exist_ok=True)
    
    model_path = os.path.join(models_dir, "lid.176.ftz")
    url = "https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.ftz"
    
    if os.path.exists(model_path):
        logger.info(f"Model already exists at {model_path}")
        return
        
    logger.info(f"Downloading FastText language identification model from {url}...")
    try:
        urllib.request.urlretrieve(url, model_path)
        logger.info("Download completed successfully.")
    except Exception as e:
        logger.error(f"Failed to download model: {e}")
        raise

if __name__ == "__main__":
    download_fasttext_model()
