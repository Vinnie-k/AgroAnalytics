from app import app  # noqa: F401

if __name__ == '__main__':
    # Run the Flask application on port 5000 as specified in guidelines
    app.run(host='0.0.0.0', port=5000, debug=True)
