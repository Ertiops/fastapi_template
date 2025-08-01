pytest_plugins = (
    "tests.plugins.factories.movie",
    "tests.plugins.factories.user",
    "tests.plugins.instances.config",
    "tests.plugins.instances.rest",
    "tests.plugins.instances.services",
    "tests.plugins.use_cases.user",
    "tests.plugins.use_cases.movie",
    "tests.plugins.storages.database",
    "tests.plugins.adapters.database",
)
