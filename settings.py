# Celery config cho async tasks 
CELERY_BROKER_URL = os.getenv('REDIS_URL')  # Sử dụng Redis làm broker cho Celery
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL') # Sử dụng Redis làm backend lưu kết quả task