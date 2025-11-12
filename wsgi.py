from app import create_app
from flask import redirect, url_for

app = create_app()

# Add root route redirect - this is what Render uses
@app.route('/')
def home():
    return redirect(url_for('auth.login'))

if __name__ == "__main__":
    app.run()

