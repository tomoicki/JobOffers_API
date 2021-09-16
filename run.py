from JobOffers_API.app import create_app

if __name__ == '__main__':
    # app.run(debug=False, host='192.168.222.116')
    app = create_app()
    app.run(debug=False)
