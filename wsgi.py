import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

from blog import create_app  # noqa

if not os.path.exists('logs'):
        os.mkdir('logs')
        if not os.path.exists('logs/blog.log'):
            open('logs/blog.log', 'w').close()
            
app = create_app()

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )
