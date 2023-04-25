from app import app, api

if __name__ == '__main__':
    app.register_blueprint(api.blueprint)
    app.run(host='0.0.0.0', port=80, debug=True)
