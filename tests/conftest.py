pytest_plugins = (
    "tests.plugins.factories.movie",
    "tests.plugins.factories.user",
    "tests.plugins.instances.config",
    "tests.plugins.instances.rest",
    "tests.plugins.instances.s3",
    "tests.plugins.use_cases.user",
    "tests.plugins.use_cases.movie",
    "tests.plugins.use_cases.file",
    "tests.plugins.storages.database",
    "tests.plugins.instances.database.database",
    "tests.plugins.instances.database.uow",
)
