from app import create_app

app = create_app()

if __name__ == '__main__':
    # Use 'stat' reloader to avoid watchdog scanning all of site-packages
    app.run(debug=True, reloader_type='stat')
