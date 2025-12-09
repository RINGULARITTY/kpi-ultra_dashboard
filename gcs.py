from google.cloud import storage
from google.api_core import exceptions

from db import LOCAL_DB_PATH

DEV = True

BUCKET_NAME = 'bucket_lwi'
DB_BLOB_PATH = 'kpi-ultra-booster/data.db'

storage_client = None

def get_storage_client():
    """Retourne le client Storage (crée une seule fois)"""
    global storage_client
    if storage_client is None:
        storage_client = storage.Client()
    return storage_client

def download_db_from_storage():
    """
    Télécharge la base de données depuis Cloud Storage.
    Retourne True si le fichier existe, False sinon.
    """
    if DEV:
        return False
    
    try:
        client = get_storage_client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(DB_BLOB_PATH)

        # Vérifier si le blob existe
        if not blob.exists():
            print(f"[INFO] DB non trouvée dans gs://{BUCKET_NAME}/{DB_BLOB_PATH}, création d'une nouvelle DB")
            return False

        # Télécharger le fichier
        blob.download_to_filename(LOCAL_DB_PATH)
        print(f"[INFO] DB téléchargée depuis gs://{BUCKET_NAME}/{DB_BLOB_PATH}")
        return True

    except exceptions.NotFound:
        print(f"[INFO] Bucket ou blob non trouvé, création d'une nouvelle DB")
        return False
    except Exception as e:
        print(f"[ERROR] Erreur lors du téléchargement: {e}")
        return False

def upload_db_to_storage():
    if DEV:
        return
    
    """Upload la base de données vers Cloud Storage"""
    try:
        client = get_storage_client()
        bucket = client.bucket(BUCKET_NAME)
        blob = bucket.blob(DB_BLOB_PATH)

        # Upload avec content-type approprié
        blob.upload_from_filename(
            LOCAL_DB_PATH,
            content_type='application/x-sqlite3',
            timeout=60
        )
        print(f"[INFO] DB uploadée vers gs://{BUCKET_NAME}/{DB_BLOB_PATH}")

    except Exception as e:
        print(f"[ERROR] Erreur lors de l'upload: {e}")
        raise