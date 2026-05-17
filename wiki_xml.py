import xml.etree.ElementTree as ET

MW_NS = "http://www.mediawiki.org/xml/export-0.11/"
ET.register_namespace("", MW_NS)


def q(tag: str) -> str:
    """Qualify a tag name with the MediaWiki export namespace.

    ElementTree represents namespaced elements internally as ``{uri}localname``,
    so ``page.find("revision")`` won't match — we have to pass ``{...}revision``.
    This wrapper keeps call sites readable: ``page.find(q("revision"))``.
    """
    return f"{{{MW_NS}}}{tag}"
