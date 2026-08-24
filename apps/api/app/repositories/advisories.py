from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models import Advisory, Consignment, MovementEvent, Outbreak, SurveillanceUpdate, VaccinationEvent
from app.models.core import LocationDataSource, OutbreakStatus


class AdvisoryRepository:
    def get_consignment(self, db: Session, consignment_id: int) -> Consignment | None:
        query = select(Consignment).options(
            selectinload(Consignment.origin_location),
            selectinload(Consignment.destination_location),
            selectinload(Consignment.vehicle),
            selectinload(Consignment.movement_events).selectinload(MovementEvent.location),
            selectinload(Consignment.vaccination_events),
        ).where(Consignment.id == consignment_id)
        return db.scalar(query)

    def list_relevant_outbreaks(self, db: Session, since: datetime) -> list[Outbreak]:
        return list(db.scalars(select(Outbreak).options(selectinload(Outbreak.location)).where(
            Outbreak.status.in_([OutbreakStatus.CONFIRMED, OutbreakStatus.SUSPECTED]),
            Outbreak.detected_at >= since,
        )))

    def latest_surveillance(self, db: Session, location_id: int) -> SurveillanceUpdate | None:
        return db.scalar(select(SurveillanceUpdate).where(SurveillanceUpdate.location_id == location_id).order_by(SurveillanceUpdate.updated_at.desc()).limit(1))

    def latest_vaccination(self, db: Session, consignment_id: int) -> VaccinationEvent | None:
        return db.scalar(select(VaccinationEvent).where(VaccinationEvent.consignment_id == consignment_id).order_by(VaccinationEvent.recorded_at.desc()).limit(1))

    def add_advisory(self, db: Session, advisory: Advisory) -> Advisory:
        db.add(advisory)
        db.commit()
        db.refresh(advisory)
        return self.get_advisory(db, advisory.id)  # type: ignore[return-value]

    def get_advisory(self, db: Session, advisory_id: int) -> Advisory | None:
        return db.scalar(select(Advisory).options(
            selectinload(Advisory.consignment).selectinload(Consignment.origin_location),
            selectinload(Advisory.consignment).selectinload(Consignment.destination_location),
            selectinload(Advisory.consignment).selectinload(Consignment.vehicle),
            selectinload(Advisory.consignment).selectinload(Consignment.movement_events).selectinload(MovementEvent.location),
        ).where(Advisory.id == advisory_id))

    def list_consignments_advisories(self, db: Session, consignment_id: int) -> list[Advisory]:
        return list(db.scalars(select(Advisory).options(
            selectinload(Advisory.consignment).selectinload(Consignment.origin_location),
            selectinload(Advisory.consignment).selectinload(Consignment.destination_location),
            selectinload(Advisory.consignment).selectinload(Consignment.vehicle),
        ).where(Advisory.consignment_id == consignment_id).order_by(Advisory.evaluated_at.desc())))

    def list_recent_advisories(self, db: Session, source: LocationDataSource | None = None) -> list[Advisory]:
        query = select(Advisory).options(
            selectinload(Advisory.consignment).selectinload(Consignment.origin_location),
            selectinload(Advisory.consignment).selectinload(Consignment.destination_location),
        ).order_by(Advisory.evaluated_at.desc()).limit(12)
        if source:
            query = query.join(Advisory.consignment).where(Consignment.data_source == source)
        return list(db.scalars(query))
