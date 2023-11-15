def api_controller(app):
    from controller.admin_auth_router import admin_auth_router
    from controller.auth_router import auth_router

    app.include_router(auth_router, prefix='/auth', tags=['Auth'])
    app.include_router(admin_auth_router, prefix='/admin/auth', tags=['Admin Auth'])
