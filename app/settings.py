import environ

# Initialize environment variables
env = environ.Env(
    DEBUG=(bool, False)
)

# Read .env file
environ.Env.read_env()

# General settings
DEBUG = env('DEBUG')
SECRET_KEY = env('MYSQL_SECRET_KEY')

# Database configuration
DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default=f"mysql://{env('MYSQL_USERNAME')}:{env('MYSQL_PASSWORD')}@{env('MYSQL_HOST')}:{env('MYSQL_PORT')}/{env('MYSQL_DATABASE')}"
    )
}

# Timezone
TIME_ZONE = env('TZ', default='UTC')