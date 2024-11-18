from importlib import import_module

router_modules = [
    import_module(".image_upload", package=__name__),
    import_module(".transformations", package=__name__)
]