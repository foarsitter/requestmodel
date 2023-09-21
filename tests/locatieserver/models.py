from typing import List
from typing import Optional

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


class LocatieserverBaseModel(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)


class LookupDoc(LocatieserverBaseModel):
    """Lookup service document"""

    bron: Optional[str]
    woonplaatscode: Optional[str]
    type: Optional[str]
    woonplaatsnaam: Optional[str]
    huis_nlt: Optional[str]
    openbareruimtetype: Optional[str]
    gemeentecode: Optional[str]
    weergavenaam: Optional[str]
    straatnaam_verkort: Optional[str]
    id: Optional[str]
    gemeentenaam: Optional[str]
    identificatie: Optional[str]
    openbareruimte_id: Optional[str]
    provinciecode: Optional[str]
    postcode: Optional[str]
    provincienaam: Optional[str]
    nummeraanduiding_id: Optional[str]
    adresseerbaarobject_id: Optional[str]
    huisnummer: Optional[int]
    huisnummertoevoeging: Optional[str] = ""
    huisletter: Optional[str] = ""
    provincieafkorting: Optional[str]
    straatnaam: Optional[str]
    gekoppeld_perceel: Optional[List[str]]


class LookupInlineResponse(LocatieserverBaseModel):
    num_found: int = Field(..., alias="numFound")
    start: int
    docs: List[LookupDoc]


class LookupResponse(LocatieserverBaseModel):
    """Response for the lookup service"""

    response: LookupInlineResponse
