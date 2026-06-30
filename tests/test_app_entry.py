def test_app_entrypoint():
    import app as app_module

    assert app_module.app is not None
