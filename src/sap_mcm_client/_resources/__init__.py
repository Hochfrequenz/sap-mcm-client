"""Resource classes that map to the SAP MCM OData V4 API endpoints.

Each resource class encapsulates HTTP interactions for a single entity set
(instances, classes, models, time series, or migration). They are not
intended for direct construction — use
:class:`~sap_mcm_client.MCMClient` instead, which exposes them as
``client.instances``, ``client.classes``, ``client.models``,
``client.time_series`` and ``client.migration``.

The implementations live in dedicated submodules; this package re-exports
them so the historical ``from sap_mcm_client._resources import ...``
imports continue to work.
"""

from sap_mcm_client._resources._base import _raise_for_status
from sap_mcm_client._resources._classes import ClassResource
from sap_mcm_client._resources._instances import InstanceResource
from sap_mcm_client._resources._migration import MigrationResource
from sap_mcm_client._resources._models import ModelResource
from sap_mcm_client._resources._timeseries import TimeSeriesResource

__all__ = [
    "ClassResource",
    "InstanceResource",
    "MigrationResource",
    "ModelResource",
    "TimeSeriesResource",
    "_raise_for_status",
]
