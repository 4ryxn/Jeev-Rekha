"""Populate the local database with clearly labelled synthetic Phase 2 demo data."""

from datetime import UTC, datetime, timedelta

from geoalchemy2.elements import WKTElement
from sqlalchemy import select

from app.db.session import SessionLocal
from app.models import Advisory, Consignment, Location, MovementEvent, Outbreak, RouteSegment, SurveillanceUpdate, VaccinationEvent, Vehicle
from app.models.core import (
    LocationType,
    LocationDataSource,
    MovementEventType,
    OutbreakStatus,
    VaccinationEvidence,
    VerificationLevel,
)
from app.services.advisory import AdvisoryService


def seed() -> str:
    """Insert a small fictional dataset; safe to run repeatedly without duplicating records."""
    db = SessionLocal()
    try:
        if db.scalar(select(Location.id).limit(1)):
            if db.scalar(select(SurveillanceUpdate.id).limit(1)):
                if not db.scalar(select(RouteSegment.id).limit(1)):
                    add_phase_four_routes(db)
                return ensure_trace_demonstration_connections(db)
            locations = list(db.scalars(select(Location)))
            by_name = {location.name: location for location in locations}
            now = datetime.now(UTC).replace(microsecond=0)
            add_phase_three_synthetic_data(db, by_name, now)
            return ensure_trace_demonstration_connections(db)

        # All names, places, vehicle references, and events below are fictional synthetic demo data.
        location_data = [
            ("Sundargram", LocationType.VILLAGE, 13.028, 77.512),
            ("Haritpur", LocationType.VILLAGE, 13.063, 77.547),
            ("Nandipur", LocationType.VILLAGE, 13.011, 77.563),
            ("Kaveri Hamlet", LocationType.VILLAGE, 12.979, 77.538),
            ("Madhavpura", LocationType.VILLAGE, 13.087, 77.591),
            ("Asha Nagar", LocationType.VILLAGE, 12.951, 77.502),
            ("Bhoomi Village", LocationType.VILLAGE, 13.104, 77.515),
            ("Navjeevan", LocationType.VILLAGE, 12.995, 77.603),
            ("Sampoorna Livestock Market", LocationType.MARKET, 13.044, 77.576),
            ("Kaveri Cattle Market", LocationType.MARKET, 12.966, 77.525),
            ("North Gate Checkpost", LocationType.CHECKPOST, 13.075, 77.568),
            ("East Route Checkpost", LocationType.CHECKPOST, 13.019, 77.609),
            ("District Veterinary Centre", LocationType.VETERINARY_CENTRE, 13.041, 77.532),
        ]
        locations = [
            Location(
                name=name,
                type=kind,
                district="Jeev Rekha District",
                state="Sampoorna State",
                latitude=latitude,
                longitude=longitude,
                geometry=WKTElement(f"POINT({longitude} {latitude})", srid=4326),
                data_source=LocationDataSource.DEMO_SEED,
                is_active=True,
            )
            for name, kind, latitude, longitude in location_data
        ]
        db.add_all(locations)
        db.flush()
        by_name = {location.name: location for location in locations}

        vehicles = [Vehicle(vehicle_reference=reference) for reference in ["KA-01-JR-1042", "KA-01-JR-2187", "KA-01-JR-3324", "KA-01-JR-4471"]]
        db.add_all(vehicles)
        db.flush()
        now = datetime.now(UTC).replace(microsecond=0)

        db.add_all([
            Outbreak(disease_name="Foot-and-mouth disease", species="Cattle", status=OutbreakStatus.CONFIRMED, location_id=by_name["Haritpur"].id, detected_at=now - timedelta(days=3), confirmed_at=now - timedelta(days=2), suspected_cases=18, confirmed_cases=12, mortality_count=1, verification_level=VerificationLevel.LABORATORY_CONFIRMED, notes="Synthetic demonstration record; no live disease feed."),
            Outbreak(disease_name="Peste des petits ruminants", species="Goat", status=OutbreakStatus.SUSPECTED, location_id=by_name["Madhavpura"].id, detected_at=now - timedelta(days=1), suspected_cases=9, confirmed_cases=0, mortality_count=0, verification_level=VerificationLevel.REPORTED, notes="Synthetic demonstration record pending fictional verification."),
            Outbreak(disease_name="Haemorrhagic septicaemia", species="Buffalo", status=OutbreakStatus.CLOSED, location_id=by_name["Kaveri Hamlet"].id, detected_at=now - timedelta(days=28), confirmed_at=now - timedelta(days=26), suspected_cases=7, confirmed_cases=5, mortality_count=0, verification_level=VerificationLevel.VETERINARY_VERIFIED, notes="Synthetic closed demonstration record."),
        ])
        consignments = [
            Consignment(origin_location_id=by_name["Sundargram"].id, destination_location_id=by_name["Sampoorna Livestock Market"].id, species="Cattle", animal_count=14, vehicle_id=vehicles[0].id, departure_at=now - timedelta(days=5), vaccination_evidence=VaccinationEvidence.VERIFIED),
            Consignment(origin_location_id=by_name["Asha Nagar"].id, destination_location_id=by_name["Kaveri Cattle Market"].id, species="Goat", animal_count=32, vehicle_id=vehicles[1].id, departure_at=now - timedelta(days=3), vaccination_evidence=VaccinationEvidence.DECLARED),
            Consignment(origin_location_id=by_name["Navjeevan"].id, destination_location_id=by_name["Madhavpura"].id, species="Buffalo", animal_count=8, vehicle_id=vehicles[2].id, departure_at=now - timedelta(days=1), vaccination_evidence=VaccinationEvidence.UNKNOWN),
        ]
        db.add_all(consignments)
        db.flush()
        db.add_all([
            MovementEvent(consignment_id=consignments[0].id, location_id=by_name["Sundargram"].id, event_type=MovementEventType.DEPARTURE, occurred_at=consignments[0].departure_at),
            MovementEvent(consignment_id=consignments[0].id, location_id=by_name["North Gate Checkpost"].id, event_type=MovementEventType.CHECKPOINT, occurred_at=consignments[0].departure_at + timedelta(hours=2)),
            MovementEvent(consignment_id=consignments[0].id, location_id=by_name["Sampoorna Livestock Market"].id, event_type=MovementEventType.MARKET_ENTRY, occurred_at=consignments[0].departure_at + timedelta(hours=4)),
            MovementEvent(consignment_id=consignments[1].id, location_id=by_name["Asha Nagar"].id, event_type=MovementEventType.DEPARTURE, occurred_at=consignments[1].departure_at),
            MovementEvent(consignment_id=consignments[1].id, location_id=by_name["Kaveri Cattle Market"].id, event_type=MovementEventType.MARKET_ENTRY, occurred_at=consignments[1].departure_at + timedelta(hours=3)),
            MovementEvent(consignment_id=consignments[2].id, location_id=by_name["Navjeevan"].id, event_type=MovementEventType.DEPARTURE, occurred_at=consignments[2].departure_at),
            MovementEvent(consignment_id=consignments[2].id, location_id=by_name["Madhavpura"].id, event_type=MovementEventType.ARRIVAL, occurred_at=consignments[2].departure_at + timedelta(hours=2)),
        ])
        db.commit()
        add_phase_three_synthetic_data(db, by_name, now)
        return ensure_trace_demonstration_connections(db)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def add_phase_three_synthetic_data(db, by_name: dict[str, Location], now: datetime) -> str:
    """Add synthetic evidence and four deterministic advisory demonstrations exactly once."""
    if db.scalar(select(SurveillanceUpdate.id).limit(1)):
        return "Synthetic Phase 3 demo data already exists; no changes made."

    # These evidence records and movements are entirely fictional and designed only for deterministic demonstrations.
    grey_locations = {"Bhoomi Village", "Navjeevan"}
    for location in by_name.values():
        is_grey_endpoint = location.name in grey_locations
        db.add(SurveillanceUpdate(
            location_id=location.id,
            updated_at=now - timedelta(days=30 if is_grey_endpoint else 2),
            verification_level=VerificationLevel.REPORTED if is_grey_endpoint else VerificationLevel.VETERINARY_VERIFIED,
            notes="Synthetic surveillance freshness record for Phase 3 demonstration.",
        ))
    db.flush()
    vehicles = list(db.scalars(select(Vehicle).order_by(Vehicle.id)))
    while len(vehicles) < 4:
        vehicle = Vehicle(vehicle_reference=f"KA-01-JR-{5500 + len(vehicles)}")
        db.add(vehicle)
        db.flush()
        vehicles.append(vehicle)
    demo_specs = [
        ("Green", "Asha Nagar", "Kaveri Cattle Market", "Cattle", 10, vehicles[3], VaccinationEvidence.VERIFIED),
        ("Amber", "Navjeevan", "Madhavpura", "Goat", 18, vehicles[0], VaccinationEvidence.VERIFIED),
        ("Red", "Haritpur", "Nandipur", "Cattle", 12, vehicles[1], VaccinationEvidence.VERIFIED),
        ("Grey", "Bhoomi Village", "Navjeevan", "Buffalo", 7, vehicles[2], VaccinationEvidence.VERIFIED),
    ]
    demonstrations: list[Consignment] = []
    for state_name, origin_name, destination_name, species, animal_count, vehicle, evidence in demo_specs:
        consignment = Consignment(
            origin_location_id=by_name[origin_name].id,
            destination_location_id=by_name[destination_name].id,
            species=species,
            animal_count=animal_count,
            vehicle_id=vehicle.id,
            departure_at=now - timedelta(hours=4),
            vaccination_evidence=evidence,
        )
        consignment.movement_events.append(MovementEvent(location_id=by_name[origin_name].id, event_type=MovementEventType.DEPARTURE, occurred_at=consignment.departure_at))
        consignment.vaccination_events.append(VaccinationEvent(
            evidence=evidence,
            recorded_at=now - timedelta(days=4),
            verification_level=VerificationLevel.VETERINARY_VERIFIED,
            notes=f"Synthetic {state_name} advisory demonstration vaccination evidence.",
        ))
        db.add(consignment)
        demonstrations.append(consignment)
    db.commit()
    service = AdvisoryService()
    for consignment in demonstrations:
        service.evaluate(db, consignment.id, now=now)
    return add_phase_four_routes(db)


def add_phase_four_routes(db) -> str:
    """Fictional controlled graph; not real-road navigation or live traffic."""
    if db.scalar(select(RouteSegment.id).limit(1)): return "Synthetic Phase 4 route network already exists; no changes made."
    locations={x.name:x for x in db.scalars(select(Location))}
    edges=[("Asha Nagar","Kaveri Cattle Market",8,18), ("Haritpur","Nandipur",6,14), ("Haritpur","North Gate Checkpost",4,9), ("North Gate Checkpost","Nandipur",7,16), ("Navjeevan","Madhavpura",5,12), ("Bhoomi Village","Navjeevan",7,16), ("Sundargram","North Gate Checkpost",5,11), ("North Gate Checkpost","Sampoorna Livestock Market",5,11), ("Sundargram","Haritpur",4,9), ("Haritpur","Sampoorna Livestock Market",5,10)]
    for a,b,d,m in edges:
        x,y=locations[a],locations[b]
        db.add(RouteSegment(start_location_id=x.id,end_location_id=y.id,distance_km=d,estimated_minutes=m,path=[[x.longitude,x.latitude],[y.longitude,y.latitude]],active=True))
    db.commit(); return "Synthetic Phase 4 route network created: 10 controlled fictional route segments."


def ensure_trace_demonstration_connections(db) -> str:
    """Add only persisted synthetic movement links needed for Phase 5A.2 tracing."""
    fmd = db.scalar(select(Outbreak).where(Outbreak.disease_name == "Foot-and-mouth disease", Outbreak.status == OutbreakStatus.CONFIRMED))
    if not fmd:
        return "Synthetic trace demonstration data requires the fictional FMD outbreak."
    locations = {location.name: location for location in db.scalars(select(Location))}
    reference_time = fmd.confirmed_at or fmd.detected_at
    rewind_consignment = db.scalar(
        select(Consignment).where(
            Consignment.origin_location_id == locations["Sundargram"].id,
            Consignment.destination_location_id == locations["Sampoorna Livestock Market"].id,
        ).order_by(Consignment.id).limit(1)
    )
    forward_consignment = db.scalar(
        select(Consignment).where(
            Consignment.origin_location_id == locations["Haritpur"].id,
            Consignment.destination_location_id == locations["Nandipur"].id,
        ).order_by(Consignment.id).limit(1)
    )
    if rewind_consignment is None or forward_consignment is None:
        return "Synthetic trace demonstration data requires the existing fictional consignments."

    added = 0
    has_rewind_link = db.scalar(select(MovementEvent.id).where(
        MovementEvent.consignment_id == rewind_consignment.id,
        MovementEvent.location_id == locations["Haritpur"].id,
    ))
    if not has_rewind_link:
        db.add(MovementEvent(
            consignment_id=rewind_consignment.id,
            location_id=locations["Haritpur"].id,
            event_type=MovementEventType.CHECKPOINT,
            occurred_at=rewind_consignment.departure_at + timedelta(hours=1),
        ))
        added += 1
    has_forward_link = db.scalar(select(MovementEvent.id).where(
        MovementEvent.consignment_id == forward_consignment.id,
        MovementEvent.location_id == locations["Nandipur"].id,
    ))
    if not has_forward_link:
        db.add(MovementEvent(
            consignment_id=forward_consignment.id,
            location_id=locations["Nandipur"].id,
            event_type=MovementEventType.ARRIVAL,
            occurred_at=forward_consignment.departure_at + timedelta(hours=2),
        ))
        added += 1
    for location_name, event_type, offset in [("North Gate Checkpost", MovementEventType.CHECKPOINT, 1), ("Sampoorna Livestock Market", MovementEventType.MARKET_ENTRY, 2)]:
        if not db.scalar(select(MovementEvent.id).where(MovementEvent.consignment_id == forward_consignment.id, MovementEvent.location_id == locations[location_name].id)):
            db.add(MovementEvent(consignment_id=forward_consignment.id, location_id=locations[location_name].id, event_type=event_type, occurred_at=forward_consignment.departure_at + timedelta(hours=offset)))
            added += 1
    if added:
        db.commit()
        return "Synthetic Phase 5A.2 trace demonstration connections created."
    return "Synthetic Phase 5A.2 trace demonstration connections already exist; no changes made."


if __name__ == "__main__":
    print(seed())
