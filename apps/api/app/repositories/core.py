from sqlalchemy import Select, select
from sqlalchemy.orm import Session, selectinload

from app.models import Consignment, Location, MovementEvent, Outbreak, Vehicle
from app.models.core import LocationDataSource, LocationType


class OperationsRepository:
    def list_locations(
        self,
        db: Session,
        location_type: LocationType | None = None,
        include_inactive: bool = False,
        source: LocationDataSource | None = None,
    ) -> list[Location]:
        query: Select[tuple[Location]] = select(Location).order_by(Location.name)
        if location_type:
            query = query.where(Location.type == location_type)
        if not include_inactive:
            query = query.where(Location.is_active.is_(True))
        if source:
            query = query.where(Location.data_source == source)
        return list(db.scalars(query))

    def get_location(self, db: Session, location_id: int) -> Location | None:
        return db.get(Location, location_id)

    def list_outbreaks(self, db: Session, source: LocationDataSource | None = None) -> list[Outbreak]:
        query = select(Outbreak).options(selectinload(Outbreak.location)).order_by(Outbreak.detected_at.desc())
        if source:
            query = query.where(Outbreak.data_source == source)
        return list(db.scalars(query))

    def get_outbreak(self, db: Session, outbreak_id: int) -> Outbreak | None:
        return db.scalar(select(Outbreak).options(selectinload(Outbreak.location)).where(Outbreak.id == outbreak_id))

    def add_outbreak(self, db: Session, outbreak: Outbreak) -> Outbreak:
        db.add(outbreak)
        db.commit()
        db.refresh(outbreak)
        return self.get_outbreak(db, outbreak.id)  # type: ignore[return-value]

    def get_vehicle_by_reference(self, db: Session, vehicle_reference: str) -> Vehicle | None:
        return db.scalar(select(Vehicle).where(Vehicle.vehicle_reference == vehicle_reference))

    def add_vehicle(self, db: Session, vehicle: Vehicle) -> Vehicle:
        db.add(vehicle)
        db.flush()
        return vehicle

    def list_consignments(self, db: Session, source: LocationDataSource | None = None) -> list[Consignment]:
        query = select(Consignment).options(
            selectinload(Consignment.origin_location),
            selectinload(Consignment.destination_location),
            selectinload(Consignment.vehicle),
            selectinload(Consignment.movement_events).selectinload(MovementEvent.location),
        ).order_by(Consignment.departure_at.desc())
        if source:
            query = query.where(Consignment.data_source == source)
        return list(db.scalars(query))

    def get_consignment(self, db: Session, consignment_id: int) -> Consignment | None:
        query = select(Consignment).options(
            selectinload(Consignment.origin_location),
            selectinload(Consignment.destination_location),
            selectinload(Consignment.vehicle),
            selectinload(Consignment.movement_events).selectinload(MovementEvent.location),
        ).where(Consignment.id == consignment_id)
        return db.scalar(query)

    def add_consignment(self, db: Session, consignment: Consignment) -> Consignment:
        db.add(consignment)
        db.commit()
        db.refresh(consignment)
        return self.get_consignment(db, consignment.id)  # type: ignore[return-value]
