import agent.initialize_agent as initialize_agent
import config
import ingestion.importer as ingestion
import models.finance as models
import services.analysis as analysis
import services.valuation as services
import storage.queries as storage
import web.app as web


def test_package_imports():
    assert config.get_settings is not None
    assert web.create_marvin_web_app is not None
    assert initialize_agent.build_agent is not None
    assert ingestion.import_all is not None
    assert models.AccountRow is not None
    assert services.value_holdings is not None
    assert analysis.summarize_liquidity is not None
    assert storage.list_accounts is not None
