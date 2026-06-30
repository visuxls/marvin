from agent.deps import CFODeps, build_deps, with_db
from config import Settings
from storage import queries


def test_build_deps(test_settings: Settings):
    deps = build_deps(test_settings)
    assert isinstance(deps, CFODeps)
    assert deps.db_path == test_settings.db_path


def test_with_db(test_settings: Settings):
    from ingestion.importer import import_all

    import_all(settings=test_settings)
    deps = build_deps(test_settings)
    with with_db(deps) as connection:
        assert len(queries.list_accounts(connection)) == 2
