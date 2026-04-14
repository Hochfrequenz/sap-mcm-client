"""Typed Python client for the SAP Cloud for Utilities Foundation MCM APIs."""

# Client
# Auth errors
from sap_mcm_client._auth import MCMAuthError
from sap_mcm_client._client import MCMClient

# Errors
from sap_mcm_client._errors import (
    MCMAPIError,
    MCMAuthenticationError,
    MCMForbiddenError,
    MCMNotFoundError,
    MCMValidationError,
)

# OData response container
from sap_mcm_client._odata import ListResponse

# Migration resource / types
from sap_mcm_client._resources import MigrationResource, TimeSeriesResource

# Enums
from sap_mcm_client.enums import (
    ActorType,
    ClassType,
    ConceptType,
    Direction,
    Division,
    ForecastBasis,
    MarketLocationType,
    MarketLocationUsage,
    MeasuringType,
    MeteringLocationPurpose,
    MeteringLocationType,
    MeteringProcedure,
    MeteringTaskType,
    ModelStatus,
    OverallStatus,
    ProcessType,
    Rate,
)

# Action request types
from sap_mcm_client.types_actions import (
    InitChangeRequest,
    InitMergeRequest,
    InitShutdownRequest,
    InitVersionCancelRequest,
)

# Class types
from sap_mcm_client.types_class import (
    ClassActor,
    ClassMeteringLocation,
    MeasurementConceptClass,
)

# Common types
from sap_mcm_client.types_common import (
    Address,
    Ancestor,
    CodeDescription,
    MCMBaseModel,
    MCMRequestModel,
    StatusEntry,
)

# Instance types
from sap_mcm_client.types_instance import (
    Actor,
    ActorUpdate,
    CalculationRule,
    CalculationRuleStep,
    ChangeProcess,
    InstanceCharacteristic,
    MarketLocation,
    MarketLocationUpdate,
    MarketLocationUsageEntry,
    MeasurementConceptInstance,
    MeasurementConceptInstanceCreate,
    MeasurementConceptInstanceUpdate,
    MeteringLocation,
    MeteringLocationUpdate,
    MeteringTask,
    MeteringTaskUpdate,
    OperandMapping,
    OperandMappingUpdate,
)
from sap_mcm_client.types_migration import (
    MigrationActor,
    MigrationAddress,
    MigrationCalculationRule,
    MigrationChangeProcess,
    MigrationInstance,
    MigrationInstanceResponse,
    MigrationInstancesRequest,
    MigrationMarketLocation,
    MigrationMarketLocationActor,
    MigrationMarketLocationUsage,
    MigrationMeteringLocation,
    MigrationMeteringTask,
    MigrationOperandMapping,
    MigrationResponse,
    MigrationStatus,
    StagedMigrationInstance,
)

# Model types
from sap_mcm_client.types_model import (
    MeasurementConceptModel,
    ModelCalculationRule,
    ModelFormula,
    ModelFormulaStep,
    ModelMarketLocation,
    ModelMarketLocationActor,
    ModelMarketLocationUsage,
    ModelMeteringLocationPurpose,
    ModelMeteringProcedure,
    ModelMeteringTask,
    ModelOperandMapping,
)

# Process data types
from sap_mcm_client.types_process_data import (
    ActorPD,
    ActorPDExternalReference,
    InstanceProcessData,
    MarketLocationPD,
    MarketLocationPDUpdate,
    MeteringLocationPD,
    MeteringLocationPDUpdate,
    MeteringTaskPD,
    MeteringTaskPDUpdate,
)
from sap_mcm_client.types_timeseries import (
    DeleteTimeSeriesRequest,
    TimeSeriesDataPoint,
)

__all__ = [
    # Client
    "MCMClient",
    # Errors
    "MCMAPIError",
    "MCMAuthenticationError",
    "MCMAuthError",
    "MCMForbiddenError",
    "MCMNotFoundError",
    "MCMValidationError",
    # Response container
    "ListResponse",
    # Enums
    "ActorType",
    "ClassType",
    "ConceptType",
    "Direction",
    "Division",
    "ForecastBasis",
    "MarketLocationType",
    "MarketLocationUsage",
    "MeasuringType",
    "MeteringLocationType",
    "MeteringLocationPurpose",
    "MeteringProcedure",
    "MeteringTaskType",
    "ModelStatus",
    "OverallStatus",
    "ProcessType",
    "Rate",
    # Common types
    "Address",
    "Ancestor",
    "CodeDescription",
    "MCMBaseModel",
    "MCMRequestModel",
    "StatusEntry",
    # Instance types
    "Actor",
    "ActorUpdate",
    "CalculationRule",
    "CalculationRuleStep",
    "ChangeProcess",
    "InstanceCharacteristic",
    "MarketLocation",
    "MarketLocationUpdate",
    "MarketLocationUsageEntry",
    "MeasurementConceptInstance",
    "MeasurementConceptInstanceCreate",
    "MeasurementConceptInstanceUpdate",
    "MeteringLocation",
    "MeteringLocationUpdate",
    "MeteringTask",
    "MeteringTaskUpdate",
    "OperandMapping",
    "OperandMappingUpdate",
    # Class types
    "ClassActor",
    "ClassMeteringLocation",
    "MeasurementConceptClass",
    # Model types
    "MeasurementConceptModel",
    "ModelCalculationRule",
    "ModelFormula",
    "ModelFormulaStep",
    "ModelMarketLocation",
    "ModelMarketLocationActor",
    "ModelMarketLocationUsage",
    "ModelMeteringLocationPurpose",
    "ModelMeteringProcedure",
    "ModelMeteringTask",
    "ModelOperandMapping",
    # Action request types
    "InitChangeRequest",
    "InitMergeRequest",
    "InitShutdownRequest",
    "InitVersionCancelRequest",
    # Process data types
    "ActorPD",
    "ActorPDExternalReference",
    "InstanceProcessData",
    "MarketLocationPD",
    "MarketLocationPDUpdate",
    "MeteringLocationPD",
    "MeteringLocationPDUpdate",
    "MeteringTaskPD",
    "MeteringTaskPDUpdate",
    # Migration
    "MigrationResource",
    "MigrationActor",
    "MigrationAddress",
    "MigrationCalculationRule",
    "MigrationChangeProcess",
    "MigrationInstance",
    "MigrationInstanceResponse",
    "MigrationInstancesRequest",
    "MigrationMarketLocation",
    "MigrationMarketLocationActor",
    "MigrationMarketLocationUsage",
    "MigrationMeteringLocation",
    "MigrationMeteringTask",
    "MigrationOperandMapping",
    "MigrationResponse",
    "MigrationStatus",
    "StagedMigrationInstance",
    # Time series
    "TimeSeriesResource",
    "TimeSeriesDataPoint",
    "DeleteTimeSeriesRequest",
]
