from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Consignment, MovementEvent, Outbreak, VaccinationEvent, Vehicle
from app.models.core import LocationDataSource, MovementEventType, VaccinationEvidence, VerificationLevel
from app.repositories.core import OperationsRepository
from app.schemas.core import ConsignmentCreate, OutbreakCreate


class OperationsService:
    def __init__(self, repository: OperationsRepository | None = None) -> None:
        self.repository = repository or OperationsRepository()

    def create_outbreak(self, db: Session, payload: OutbreakCreate) -> Outbreak:
        location = self.repository.get_location(db, payload.location_id)
        self._validate_location_context(location, payload.data_source, "Outbreak")
        if payload.review_radius_km is not None and payload.data_source != LocationDataSource.PILOT_ENTERED:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Review radius is available only for pilot-entered outbreaks.")
        return self.repository.add_outbreak(db, Outbreak(**payload.model_dump()))

    def create_consignment(self, db: Session, payload: ConsignmentCreate) -> Consignment:
        origin = self.repository.get_location(db, payload.origin_location_id)
        destination = self.repository.get_location(db, payload.destination_location_id)
        if not origin or not destination:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Origin and destination must exist")
        self._validate_location_context(origin, payload.data_source, "Origin")
        self._validate_location_context(destination, payload.data_source, "Destination")
        vehicle = self.repository.get_vehicle_by_reference(db, payload.vehicle_reference)
        if not vehicle:
            vehicle = self.repository.add_vehicle(db, Vehicle(vehicle_reference=payload.vehicle_reference.upper()))
        consignment = Consignment(
            origin_location_id=payload.origin_location_id,
            destination_location_id=payload.destination_location_id,
            data_source=payload.data_source,
            species=payload.species,
            animal_count=payload.animal_count,
            vehicle_id=vehicle.id,
            departure_at=payload.departure_at,
            vaccination_evidence=payload.vaccination_evidence,
        )
        consignment.movement_events.append(MovementEvent(location_id=origin.id, event_type=MovementEventType.DEPARTURE, occurred_at=payload.departure_at))
        consignment.vaccination_events.append(VaccinationEvent(
            evidence=payload.vaccination_evidence,
            recorded_at=payload.departure_at,
            verification_level=VerificationLevel.VETERINARY_VERIFIED if payload.vaccination_evidence == VaccinationEvidence.VERIFIED else VerificationLevel.REPORTED,
            notes="Synthetic local registration evidence.",
        ))
        return self.repository.add_consignment(db, consignment)

    @staticmethod
    def _validate_location_context(location: object | None, record_source: LocationDataSource, label: str) -> None:
        if not location:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{label} location does not exist")
        if not getattr(location, "is_active"):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"{label} location is archived and cannot be used")
        if getattr(location, "data_source") != record_source:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Record context must match active location sources; mixed-source locations are not allowed.",
            )
