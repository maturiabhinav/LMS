from app import create_app
import os
from flask import redirect, url_for

app = create_app()

# Add root route at application level
@app.route('/')
def home():
    return redirect(url_for('auth.login'))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)