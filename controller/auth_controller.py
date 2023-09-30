def api_controller(app):
    from controller.auth_router import auth_router

    app.include_router(auth_router)
