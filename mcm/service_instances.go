package mcm

import (
	"context"
	"fmt"
	"net/http"
)

// InstanceService handles communication with the measurement concept instance
// related endpoints of the SAP MCM API.
type InstanceService struct {
	client *Client
}

// List retrieves a paginated list of measurement concept instances.
// Pass nil for opts to use default pagination.
func (s *InstanceService) List(ctx context.Context, opts *ListOptions) (*ListResponse[MeasurementConceptInstance], error) {
	qp := opts.queryParams()
	if qp == nil {
		qp = make(map[string][]string)
	}
	qp.Set("$expand", defaultInstanceExpand())

	path := "MCMInstances?" + qp.Encode()

	req, err := s.client.newRequest(ctx, http.MethodGet, path, nil)
	if err != nil {
		return nil, err
	}

	body, err := s.client.doRaw(req)
	if err != nil {
		return nil, err
	}

	return parseODataCollection[MeasurementConceptInstance](body)
}

// Get retrieves a single measurement concept instance by ID.
func (s *InstanceService) Get(ctx context.Context, id string) (*MeasurementConceptInstance, error) {
	path := fmt.Sprintf("MCMInstances(%s)?$expand=%s", id, defaultInstanceExpand())

	req, err := s.client.newRequest(ctx, http.MethodGet, path, nil)
	if err != nil {
		return nil, err
	}

	var result MeasurementConceptInstance
	if err := s.client.do(req, &result); err != nil {
		return nil, err
	}
	return &result, nil
}

// Create creates a new measurement concept instance.
func (s *InstanceService) Create(ctx context.Context, input *CreateInstanceInput) (*MeasurementConceptInstance, error) {
	req, err := s.client.newRequest(ctx, http.MethodPost, "MCMInstances", input)
	if err != nil {
		return nil, err
	}

	var result MeasurementConceptInstance
	if err := s.client.do(req, &result); err != nil {
		return nil, err
	}
	return &result, nil
}

// Update patches a measurement concept instance.
func (s *InstanceService) Update(ctx context.Context, id string, input *UpdateInstanceInput) (*MeasurementConceptInstance, error) {
	path := fmt.Sprintf("MCMInstances(%s)", id)

	req, err := s.client.newRequest(ctx, http.MethodPatch, path, input)
	if err != nil {
		return nil, err
	}

	var result MeasurementConceptInstance
	if err := s.client.do(req, &result); err != nil {
		return nil, err
	}
	return &result, nil
}

// --- Sub-entity updates ---

// UpdateMeteringLocation patches a metering location on a measurement concept instance.
func (s *InstanceService) UpdateMeteringLocation(ctx context.Context, instanceID, meloID string, input *UpdateMeteringLocationInput) error {
	path := fmt.Sprintf("MCMInstances(%s)/meteringLocations(%s)", instanceID, meloID)

	req, err := s.client.newRequest(ctx, http.MethodPatch, path, input)
	if err != nil {
		return err
	}
	return s.client.do(req, nil)
}

// UpdateMarketLocation patches a market location on a measurement concept instance.
func (s *InstanceService) UpdateMarketLocation(ctx context.Context, instanceID, maloID string, input *UpdateMarketLocationInput) error {
	path := fmt.Sprintf("MCMInstances(%s)/marketLocations(%s)", instanceID, maloID)

	req, err := s.client.newRequest(ctx, http.MethodPatch, path, input)
	if err != nil {
		return err
	}
	return s.client.do(req, nil)
}

// UpdateActor patches an actor on a measurement concept instance.
func (s *InstanceService) UpdateActor(ctx context.Context, instanceID, actorID string, input *UpdateActorInput) error {
	path := fmt.Sprintf("MCMInstances(%s)/actors(%s)", instanceID, actorID)

	req, err := s.client.newRequest(ctx, http.MethodPatch, path, input)
	if err != nil {
		return err
	}
	return s.client.do(req, nil)
}

// UpdateMeteringTask patches a metering task on a metering location of a
// measurement concept instance.
func (s *InstanceService) UpdateMeteringTask(ctx context.Context, instanceID, meloID, taskID string, input *UpdateMeteringTaskInput) error {
	path := fmt.Sprintf("MCMInstances(%s)/meteringLocations(%s)/meteringTasks(%s)", instanceID, meloID, taskID)

	req, err := s.client.newRequest(ctx, http.MethodPatch, path, input)
	if err != nil {
		return err
	}
	return s.client.do(req, nil)
}

// UpdateOperandMapping patches an operand mapping on a measurement concept instance.
func (s *InstanceService) UpdateOperandMapping(ctx context.Context, instanceID, mappingID string, input *UpdateOperandMappingInput) error {
	path := fmt.Sprintf("MCMInstances(%s)/operandMappings(%s)", instanceID, mappingID)

	req, err := s.client.newRequest(ctx, http.MethodPatch, path, input)
	if err != nil {
		return err
	}
	return s.client.do(req, nil)
}

// --- Lifecycle actions ---

// InitChange initiates a change process on a measurement concept instance,
// creating a new version of the instance.
func (s *InstanceService) InitChange(ctx context.Context, id string, input *InitChangeInput) (*MeasurementConceptInstance, error) {
	path := fmt.Sprintf("MCMInstances(%s)/MCMService.initChange", id)

	req, err := s.client.newRequest(ctx, http.MethodPost, path, input)
	if err != nil {
		return nil, err
	}

	var result MeasurementConceptInstance
	if err := s.client.do(req, &result); err != nil {
		return nil, err
	}
	return &result, nil
}

// InitMerge initiates a merge of measurement concept instances, creating a
// new combined instance version.
func (s *InstanceService) InitMerge(ctx context.Context, id string, input *InitMergeInput) (*MeasurementConceptInstance, error) {
	path := fmt.Sprintf("MCMInstances(%s)/MCMService.initMerge", id)

	req, err := s.client.newRequest(ctx, http.MethodPost, path, input)
	if err != nil {
		return nil, err
	}

	var result MeasurementConceptInstance
	if err := s.client.do(req, &result); err != nil {
		return nil, err
	}
	return &result, nil
}

// InitShutdown initiates a shutdown of a measurement concept instance.
func (s *InstanceService) InitShutdown(ctx context.Context, id string, input *InitShutdownInput) (*MeasurementConceptInstance, error) {
	path := fmt.Sprintf("MCMInstances(%s)/MCMService.initShutdown", id)

	req, err := s.client.newRequest(ctx, http.MethodPost, path, input)
	if err != nil {
		return nil, err
	}

	var result MeasurementConceptInstance
	if err := s.client.do(req, &result); err != nil {
		return nil, err
	}
	return &result, nil
}

// InitVersionCancel initiates a version cancellation of a measurement concept instance.
func (s *InstanceService) InitVersionCancel(ctx context.Context, id string, input *InitVersionCancelInput) (*MeasurementConceptInstance, error) {
	path := fmt.Sprintf("MCMInstances(%s)/MCMService.initVersionCancel", id)

	req, err := s.client.newRequest(ctx, http.MethodPost, path, input)
	if err != nil {
		return nil, err
	}

	var result MeasurementConceptInstance
	if err := s.client.do(req, &result); err != nil {
		return nil, err
	}
	return &result, nil
}

// --- Notifications ---

// NotifyDeviceRemoved notifies the API that a device has been removed from a
// metering location on a measurement concept instance.
func (s *InstanceService) NotifyDeviceRemoved(ctx context.Context, instanceID, meloID string) error {
	path := fmt.Sprintf("MCMInstances(%s)/meteringLocations(%s)/MCMService.notifySingleDeviceRemoved", instanceID, meloID)

	req, err := s.client.newRequest(ctx, http.MethodPost, path, nil)
	if err != nil {
		return err
	}
	return s.client.do(req, nil)
}

// NotifyMarketLocationRemoved notifies the API that a market location has been
// removed from a measurement concept instance.
func (s *InstanceService) NotifyMarketLocationRemoved(ctx context.Context, instanceID, maloID string) error {
	path := fmt.Sprintf("MCMInstances(%s)/marketLocations(%s)/MCMService.notifyMarketLocationRemoved", instanceID, maloID)

	req, err := s.client.newRequest(ctx, http.MethodPost, path, nil)
	if err != nil {
		return err
	}
	return s.client.do(req, nil)
}

// NotifyFinalDataEntryReady notifies the API that the final data entry is
// ready for a change process on a measurement concept instance.
func (s *InstanceService) NotifyFinalDataEntryReady(ctx context.Context, instanceID, changeProcessID string) error {
	path := fmt.Sprintf("MCMInstances(%s)/changeProcesses(%s)/processData/MCMService.notifyFinalDataEntryReady", instanceID, changeProcessID)

	req, err := s.client.newRequest(ctx, http.MethodPost, path, nil)
	if err != nil {
		return err
	}
	return s.client.do(req, nil)
}
