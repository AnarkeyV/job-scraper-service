from app.providers.remotive import RemotiveProvider
from app.providers.arbeitnow import ArbeitnowProvider
from app.providers.remoteok import RemoteOKProvider
from app.providers.mock import MockProvider
from app.providers.link_sources import SearchLinkProvider
from app.providers.jora_sg import JoraSGProvider

PROVIDERS = {
    "remotive": RemotiveProvider(),
    "arbeitnow": ArbeitnowProvider(),
    "remoteok": RemoteOKProvider(),
    "mock": MockProvider(),
    "search_links": SearchLinkProvider(),
    "jora_sg": JoraSGProvider(),
}
