from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

def utc_now():
    return datetime.now(timezone.utc)

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(25), nullable=True)
    role = db.Column(db.String(20), default='tenant', nullable=False) # 'tenant', 'owner', 'agent', 'admin'
    agency_name = db.Column(db.String(150), nullable=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    # Relationships
    properties = db.relationship('Property', backref='owner_rel', lazy='dynamic', cascade='all, delete-orphan')
    enquiries_sent = db.relationship('Enquiry', backref='sender_rel', lazy='dynamic')
    visit_requests_sent = db.relationship('VisitRequest', backref='visitor_rel', lazy='dynamic')
    favorites = db.relationship('Favorite', backref='user_rel', lazy='dynamic', cascade='all, delete-orphan')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_owner_or_agent(self):
        return self.role in ['owner', 'agent', 'admin']

    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class Property(db.Model):
    __tablename__ = 'properties'

    id = db.Column(db.Integer, primary_key=True)
    property_code = db.Column(db.String(30), unique=True, nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    slug = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=False)
    property_type = db.Column(db.String(60), nullable=False) # Independent Villa, Traditional Kerala Nalukettu, Modern Apartment, etc.
    
    # Core Specs
    bhk = db.Column(db.Integer, nullable=False) # 1, 2, 3, 4, 5
    bathrooms = db.Column(db.Integer, nullable=False)
    balconies = db.Column(db.Integer, default=1)
    sqft_area = db.Column(db.Integer, nullable=False)
    
    # Financials
    monthly_rent = db.Column(db.Integer, nullable=False, index=True) # INR
    security_deposit = db.Column(db.Integer, nullable=False) # INR
    maintenance_charges = db.Column(db.Integer, default=0) # INR / month

    # Features & Amenities
    furnishing = db.Column(db.String(40), nullable=False) # Fully Furnished, Semi-Furnished, Unfurnished
    parking = db.Column(db.String(60), nullable=False) # Covered Car Parking, Open Car Parking, Two-Wheeler Only, Multiple Covered Cars
    water_supply = db.Column(db.String(120), nullable=False) # KWA + Open Well, Dedicated Open Well, 24x7 KWA, etc.
    electricity = db.Column(db.String(120), nullable=False) # 3-Phase KSEB with Inverter, Solar Rooftop + KSEB, etc.
    kitchen_type = db.Column(db.String(60), nullable=False) # Modular Kitchen with Work Area, Modular Kitchen, Traditional with Chimney
    pet_policy = db.Column(db.String(60), default='Pets Allowed') # Pets Allowed, Small Pets Only, Not Allowed
    tenant_preference = db.Column(db.String(60), default='Any Suitable Tenant') # Family Preferred, Bachelors Welcome, etc.
    availability_date = db.Column(db.String(60), default='Immediate') # 'Immediate', 'Ready to Move', or specific date

    # Status & Badges
    status = db.Column(db.String(30), default='Available', index=True) # Available, Under Negotiation, Rented
    approval_status = db.Column(db.String(30), default='approved', index=True) # approved, pending, rejected
    is_verified = db.Column(db.Boolean, default=False)
    is_featured = db.Column(db.Boolean, default=False)
    is_sample_demo = db.Column(db.Boolean, default=False)

    # Location
    district = db.Column(db.String(60), nullable=False, index=True) # One of 14 Kerala Districts
    city_town = db.Column(db.String(100), nullable=False, index=True)
    locality = db.Column(db.String(150), nullable=False)
    full_address = db.Column(db.Text, nullable=False)
    pin_code = db.Column(db.String(15), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    nearby_landmarks = db.Column(db.Text, nullable=True) # Formatted landmarks with distances

    # Owner / Contact
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    owner_name = db.Column(db.String(120), nullable=False)
    owner_contact_type = db.Column(db.String(40), default='Individual Owner') # Individual Owner, Authorized Agent, Property Manager
    contact_phone = db.Column(db.String(25), nullable=True)
    whatsapp_number = db.Column(db.String(25), nullable=True)
    contact_email = db.Column(db.String(120), nullable=True)
    owner_verified = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=utc_now)
    updated_at = db.Column(db.DateTime, default=utc_now, onupdate=utc_now)

    # Relationships
    images = db.relationship('PropertyImage', backref='property_rel', lazy='dynamic', cascade='all, delete-orphan', order_by='PropertyImage.image_order')
    enquiries = db.relationship('Enquiry', backref='property_rel', lazy='dynamic', cascade='all, delete-orphan')
    visit_requests = db.relationship('VisitRequest', backref='property_rel', lazy='dynamic', cascade='all, delete-orphan')
    favorites = db.relationship('Favorite', backref='property_rel', lazy='dynamic', cascade='all, delete-orphan')
    reports = db.relationship('PropertyReport', backref='property_rel', lazy='dynamic', cascade='all, delete-orphan')
    feedbacks = db.relationship('PropertyFeedback', backref='property_rel', lazy='dynamic', cascade='all, delete-orphan')

    @property
    def primary_image_url(self):
        primary = self.images.filter_by(is_primary=True).first()
        if primary:
            return primary.image_url
        first_img = self.images.first()
        if first_img:
            return first_img.image_url
        return '/static/images/hero-kerala.jpg'

    @property
    def formatted_rent(self):
        return f"₹{self.monthly_rent:,}"

    @property
    def formatted_deposit(self):
        return f"₹{self.security_deposit:,}"

    @property
    def formatted_maintenance(self):
        if self.maintenance_charges > 0:
            return f"₹{self.maintenance_charges:,}/mo"
        return "Included in Rent"

    @property
    def average_rating(self):
        all_fb = self.feedbacks.filter_by(is_approved=True).all()
        if not all_fb:
            return 0.0
        return round(sum(f.rating for f in all_fb) / len(all_fb), 1)

    @property
    def feedback_count(self):
        return self.feedbacks.filter_by(is_approved=True).count()

    def get_landmarks_parsed(self):
        """Returns list of dicts with name, distance, and category icon."""
        if not self.nearby_landmarks:
            return []
        items = []
        for line in self.nearby_landmarks.split('|'):
            line = line.strip()
            if not line:
                continue
            parts = line.split(':')
            if len(parts) >= 2:
                name = parts[0].strip()
                dist = ':'.join(parts[1:]).strip()
            else:
                name = line
                dist = "Nearby"
            
            # Simple icon classification
            name_lower = name.lower()
            if any(k in name_lower for k in ['school', 'college', 'vidyalaya', 'campus', 'university']):
                icon = 'school'
            elif any(k in name_lower for k in ['hospital', 'clinic', 'medical', 'health']):
                icon = 'hospital'
            elif any(k in name_lower for k in ['metro', 'railway', 'station', 'bus', 'airport']):
                icon = 'transit'
            elif any(k in name_lower for k in ['supermarket', 'mall', 'market', 'hypermarket']):
                icon = 'shopping'
            elif any(k in name_lower for k in ['park', 'infopark', 'technopark', 'cyberpark']):
                icon = 'tech'
            else:
                icon = 'pin'
            
            items.append({
                'name': name,
                'distance': dist,
                'icon': icon
            })
        return items

    def __repr__(self):
        return f'<Property {self.property_code}: {self.title}>'


class PropertyImage(db.Model):
    __tablename__ = 'property_images'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(100), default='Property View') # e.g. Front Exterior, Living Room, Master Bedroom, etc.
    image_order = db.Column(db.Integer, default=0)
    is_primary = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<PropertyImage {self.id} for Prop {self.property_id}>'


class Enquiry(db.Model):
    __tablename__ = 'enquiries'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    sender_name = db.Column(db.String(120), nullable=False)
    sender_email = db.Column(db.String(120), nullable=False)
    sender_phone = db.Column(db.String(25), nullable=False)
    message = db.Column(db.Text, nullable=False)
    move_in_date = db.Column(db.String(50), nullable=True)
    tenant_type = db.Column(db.String(50), default='Family')
    
    status = db.Column(db.String(30), default='pending') # 'pending', 'read', 'replied', 'closed'
    created_at = db.Column(db.DateTime, default=utc_now)

    def __repr__(self):
        return f'<Enquiry from {self.sender_name} for Prop {self.property_id}>'


class VisitRequest(db.Model):
    __tablename__ = 'visit_requests'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    visitor_name = db.Column(db.String(120), nullable=False)
    visitor_phone = db.Column(db.String(25), nullable=False)
    visitor_email = db.Column(db.String(120), nullable=False)
    preferred_date = db.Column(db.String(50), nullable=False)
    preferred_time_slot = db.Column(db.String(60), nullable=False) # Morning, Afternoon, Evening
    notes = db.Column(db.Text, nullable=True)
    
    status = db.Column(db.String(30), default='pending') # 'pending', 'confirmed', 'declined', 'completed'
    owner_reply = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def __repr__(self):
        return f'<VisitRequest for Prop {self.property_id} on {self.preferred_date}>'


class Favorite(db.Model):
    __tablename__ = 'favorites'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=utc_now)

    __table_args__ = (db.UniqueConstraint('user_id', 'property_id', name='uq_user_property_favorite'),)


class PropertyReport(db.Model):
    __tablename__ = 'property_reports'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    
    reporter_name = db.Column(db.String(120), nullable=False)
    reporter_email = db.Column(db.String(120), nullable=False)
    reason = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text, nullable=False)
    
    status = db.Column(db.String(30), default='pending') # 'pending', 'reviewed', 'resolved'
    created_at = db.Column(db.DateTime, default=utc_now)

    def __repr__(self):
        return f'<Report for Prop {self.property_id}: {self.reason}>'


class PropertyFeedback(db.Model):
    __tablename__ = 'property_feedbacks'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)

    reviewer_name = db.Column(db.String(120), nullable=False)
    reviewer_email = db.Column(db.String(120), nullable=True)
    rating = db.Column(db.Integer, nullable=False, default=5) # 1 to 5 stars
    visit_type = db.Column(db.String(60), default='Visited Property') # 'Visited in Person', 'Previous Tenant', 'Neighborhood Resident', 'Prospective Seeker'
    headline = db.Column(db.String(200), nullable=True)
    comment = db.Column(db.Text, nullable=False)

    # Kerala-specific ratings
    water_rating = db.Column(db.Integer, default=5) # 1 to 5
    location_rating = db.Column(db.Integer, default=5) # 1 to 5
    landlord_rating = db.Column(db.Integer, default=5) # 1 to 5

    is_approved = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=utc_now)

    def __repr__(self):
        return f'<PropertyFeedback {self.id} for Property {self.property_id} ({self.rating} stars)>'

