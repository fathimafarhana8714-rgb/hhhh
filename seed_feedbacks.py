from app import app, db
from models import Property, PropertyFeedback

sample_feedbacks = [
    {
        "prop_code": "NK-EKM-2024-001",
        "reviewer_name": "Suresh Kumar",
        "reviewer_email": "suresh.kumar@infopark.org",
        "rating": 5,
        "visit_type": "Previous Tenant",
        "headline": "Sweet well water & super close to Infopark",
        "comment": "Lived here with my family for 18 months before relocation. The open well water is exceptionally sweet and abundant even in peak April summers. Infopark Phase 1 is a breezy 6-minute drive. Mr. Menon is an extremely courteous and cooperative landlord.",
        "water_rating": 5,
        "location_rating": 5,
        "landlord_rating": 5
    },
    {
        "prop_code": "NK-EKM-2024-001",
        "reviewer_name": "Anjali Nair",
        "reviewer_email": "anjali.nair@rajagiri.edu",
        "rating": 5,
        "visit_type": "Visited in Person",
        "headline": "Breezy architecture with ample car parking",
        "comment": "Visited the villa last weekend with my husband. The double-height living room ensures cool natural ventilation. The covered car porch comfortably accommodates two cars plus two-wheelers. The neighborhood is serene and safe for children.",
        "water_rating": 5,
        "location_rating": 5,
        "landlord_rating": 5
    },
    {
        "prop_code": "NK-TVM-2024-002",
        "reviewer_name": "Dr. K. P. Ramachandran",
        "reviewer_email": "kp.ramachandran@gmail.com",
        "rating": 5,
        "visit_type": "Visited in Person",
        "headline": "Rare traditional Kerala home with modern luxury",
        "comment": "The central Nadumuttam brings in fresh rain and morning sunlight. Beautiful woodwork, peaceful royal precinct in Kowdiar, and crystal clean water. Dr. Jayasree Varma was remarkably polite during our viewing.",
        "water_rating": 5,
        "location_rating": 5,
        "landlord_rating": 5
    },
    {
        "prop_code": "NK-EKM-2024-003",
        "reviewer_name": "Vivek Gopinath",
        "reviewer_email": "vivek.gopinath@realtykerala.com",
        "rating": 5,
        "visit_type": "Previous Tenant",
        "headline": "Unrivaled Vembanad lake sunset views",
        "comment": "The 14th floor balcony overlooks Bolgatty Island and sunset over backwaters. 100% generator backup was flawless during heavy monsoon rains. Walking distance to High Court and metro.",
        "water_rating": 5,
        "location_rating": 5,
        "landlord_rating": 5
    },
    {
        "prop_code": "NK-TVM-2024-009",
        "reviewer_name": "Neha Pradeep",
        "reviewer_email": "neha.pradeep@technopark.in",
        "rating": 5,
        "visit_type": "Visited in Person",
        "headline": "Perfect home for IT professionals at Technopark",
        "comment": "900 meters from Technopark Phase 1 gate so you save hours in traffic. Gym, power backup, and high-speed broadband ready. Highly recommended for young couples or IT executives.",
        "water_rating": 5,
        "location_rating": 5,
        "landlord_rating": 5
    }
]

with app.app_context():
    db.create_all()
    count_added = 0
    for fb_data in sample_feedbacks:
        pcode = fb_data.pop("prop_code")
        prop = Property.query.filter_by(property_code=pcode).first()
        if prop:
            existing = PropertyFeedback.query.filter_by(property_id=prop.id, reviewer_name=fb_data["reviewer_name"]).first()
            if not existing:
                fb = PropertyFeedback(property_id=prop.id, is_approved=True, **fb_data)
                db.session.add(fb)
                count_added += 1

    db.session.commit()
    print(f"Successfully seeded {count_added} initial property reviews.")
