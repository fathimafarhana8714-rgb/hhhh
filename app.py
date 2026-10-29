import os
from datetime import datetime, timezone
from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, jsonify, abort, send_from_directory
)
from werkzeug.security import check_password_hash
from models import (
    db, User, Property, PropertyImage, Enquiry,
    VisitRequest, Favorite, PropertyReport, PropertyFeedback
)
from seed_data import seed_database, KERALA_DISTRICTS
from districts_data import KERALA_DISTRICTS_INFO
from helpers import (
    get_current_user, login_required, role_required,
    save_uploaded_file, get_smart_recommendations
)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'nestkerala-super-secure-production-secret-2024')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///nestkerala.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads', 'properties')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16 MB max upload

db.init_app(app)

# Inject current user, language, districts, and favorites into all Jinja templates
@app.context_processor
def inject_global_vars():
    curr_user = get_current_user()
    lang = session.get('lang', 'en')
    
    # User's favorited property IDs
    fav_ids = set()
    if curr_user:
        fav_ids = {f.property_id for f in Favorite.query.filter_by(user_id=curr_user.id).all()}
    else:
        fav_ids = set(session.get('guest_favorites', []))
        
    compare_ids = session.get('compare_ids', [])

    return {
        'current_user': curr_user,
        'current_lang': lang,
        'districts_info': KERALA_DISTRICTS_INFO,
        'kerala_districts': KERALA_DISTRICTS,
        'fav_ids': fav_ids,
        'compare_ids': compare_ids,
        'now': datetime.now(timezone.utc)
    }


# -------------------------------------------------------------
# Static & Utility Routes
# -------------------------------------------------------------

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, 'static', 'images'),
        'logo.svg',
        mimetype='image/svg+xml'
    )

@app.route('/saved')
def saved_redirect():
    return redirect(url_for('saved_homes'))

@app.route('/owner/dashboard')
def owner_dashboard_redirect():
    return redirect(url_for('owner_dashboard'))

@app.route('/admin/dashboard')
def admin_dashboard_redirect():
    return redirect(url_for('admin_dashboard'))


# -------------------------------------------------------------
# Public & Exploration Routes
# -------------------------------------------------------------

@app.route('/')
def index():
    # Featured properties for hero carousel
    featured_properties = Property.query.filter_by(
        approval_status='approved',
        status='Available',
        is_featured=True
    ).order_by(Property.id.desc()).limit(6).all()

    # Fallback to recent if not enough featured
    if len(featured_properties) < 3:
        featured_properties = Property.query.filter_by(
            approval_status='approved',
            status='Available'
        ).order_by(Property.id.desc()).limit(6).all()

    # Recent properties
    recent_properties = Property.query.filter_by(
        approval_status='approved',
        status='Available'
    ).order_by(Property.id.desc()).limit(6).all()

    # Budget-friendly rental homes (< Rs 22,000)
    budget_properties = Property.query.filter(
        Property.approval_status == 'approved',
        Property.status == 'Available',
        Property.monthly_rent <= 22000
    ).order_by(Property.monthly_rent.asc()).limit(6).all()

    # Calculate actual listing count for each district
    district_counts = {}
    for d in KERALA_DISTRICTS:
        cnt = Property.query.filter_by(district=d, approval_status='approved', status='Available').count()
        district_counts[d] = cnt

    return render_template(
        'index.html',
        featured_properties=featured_properties,
        recent_properties=recent_properties,
        budget_properties=budget_properties,
        district_counts=district_counts
    )


@app.route('/properties')
def properties():
    query_text = request.args.get('q', '').strip()
    district = request.args.get('district', '').strip()
    property_type = request.args.get('property_type', '').strip()
    bhk = request.args.get('bhk', '').strip()
    min_rent = request.args.get('min_rent', '').strip()
    max_rent = request.args.get('max_rent', '').strip()
    furnishing = request.args.get('furnishing', '').strip()
    parking = request.args.get('parking', '').strip()
    pet_friendly = request.args.get('pet_friendly', '').strip()
    verified_only = request.args.get('verified_only', '').strip()
    sort_by = request.args.get('sort', 'newest').strip()

    base_query = Property.query.filter_by(approval_status='approved')

    # Status: default to available or show all approved
    show_all_status = request.args.get('include_rented', '0')
    if show_all_status != '1':
        base_query = base_query.filter(Property.status == 'Available')

    # Apply filters
    if district:
        base_query = base_query.filter(Property.district.ilike(f"%{district}%"))

    if property_type:
        base_query = base_query.filter(Property.property_type.ilike(f"%{property_type}%"))

    if bhk:
        try:
            bhk_val = int(bhk)
            if bhk_val >= 4:
                base_query = base_query.filter(Property.bhk >= 4)
            else:
                base_query = base_query.filter(Property.bhk == bhk_val)
        except ValueError:
            pass

    if min_rent:
        try:
            base_query = base_query.filter(Property.monthly_rent >= int(min_rent))
        except ValueError:
            pass

    if max_rent:
        try:
            base_query = base_query.filter(Property.monthly_rent <= int(max_rent))
        except ValueError:
            pass

    if furnishing:
        base_query = base_query.filter(Property.furnishing.ilike(f"%{furnishing}%"))

    if parking:
        base_query = base_query.filter(Property.parking.ilike(f"%{parking}%"))

    if pet_friendly == '1':
        base_query = base_query.filter(Property.pet_policy.ilike('%allowed%'))

    if verified_only == '1':
        base_query = base_query.filter(Property.is_verified == True)

    if query_text:
        term = f"%{query_text}%"
        base_query = base_query.filter(
            db.or_(
                Property.title.ilike(term),
                Property.city_town.ilike(term),
                Property.locality.ilike(term),
                Property.full_address.ilike(term),
                Property.property_code.ilike(term),
                Property.nearby_landmarks.ilike(term)
            )
        )

    # Sorting
    if sort_by == 'lowest_rent':
        base_query = base_query.order_by(Property.monthly_rent.asc())
    elif sort_by == 'highest_rent':
        base_query = base_query.order_by(Property.monthly_rent.desc())
    elif sort_by == 'area_desc':
        base_query = base_query.order_by(Property.sqft_area.desc())
    else: # newest
        base_query = base_query.order_by(Property.id.desc())

    properties_list = base_query.all()
    exact_matches_count = len(properties_list)

    # Smart Recommendation System:
    # If exact matches are zero or very low (< 2), rank and recommend alternative homes!
    recommended_properties = []
    if exact_matches_count < 2:
        calc_rent = None
        if min_rent and max_rent:
            calc_rent = (int(min_rent) + int(max_rent)) / 2
        elif max_rent:
            calc_rent = int(max_rent)
        elif min_rent:
            calc_rent = int(min_rent)

        criteria = {
            'district': district if district else None,
            'rent': calc_rent,
            'bhk': bhk if bhk else None,
            'property_type': property_type if property_type else None,
            'furnishing': furnishing if furnishing else None
        }
        exclude_ids = [p.id for p in properties_list]
        recommended_properties = get_smart_recommendations(criteria, exclude_ids=exclude_ids, limit=4)

    return render_template(
        'properties.html',
        properties=properties_list,
        exact_matches_count=exact_matches_count,
        recommended_properties=recommended_properties,
        selected_district=district,
        selected_bhk=bhk,
        selected_type=property_type,
        min_rent=min_rent,
        max_rent=max_rent,
        selected_furnishing=furnishing,
        selected_parking=parking,
        pet_friendly=pet_friendly,
        verified_only=verified_only,
        query_text=query_text,
        sort_by=sort_by
    )


@app.route('/property/<int:property_id>')
@app.route('/property/<int:property_id>/<slug>')
def property_detail(property_id, slug=None):
    prop = Property.query.get_or_404(property_id)

    # Track recently viewed in session
    recent = session.get('recently_viewed', [])
    if property_id in recent:
        recent.remove(property_id)
    recent.insert(0, property_id)
    session['recently_viewed'] = recent[:6] # keep top 6

    # Similar properties in the same or nearby district
    similar_properties = Property.query.filter(
        Property.approval_status == 'approved',
        Property.status == 'Available',
        Property.id != prop.id,
        Property.district == prop.district
    ).limit(3).all()

    if len(similar_properties) < 3:
        more_props = Property.query.filter(
            Property.approval_status == 'approved',
            Property.status == 'Available',
            Property.id != prop.id,
            Property.id.notin_([p.id for p in similar_properties])
        ).limit(3 - len(similar_properties)).all()
        similar_properties.extend(more_props)

    # All photos ordered
    images = prop.images.order_by(PropertyImage.image_order.asc()).all()

    return render_template(
        'property_detail.html',
        property=prop,
        images=images,
        landmarks=prop.get_landmarks_parsed(),
        similar_properties=similar_properties
    )


# -------------------------------------------------------------
# Interactions: Enquiry, Visit Scheduling, Reporting
# -------------------------------------------------------------

@app.route('/property/<int:property_id>/enquiry', methods=['POST'])
def submit_enquiry(property_id):
    prop = Property.query.get_or_404(property_id)
    curr_user = get_current_user()

    sender_name = request.form.get('sender_name', '').strip()
    sender_phone = request.form.get('sender_phone', '').strip()
    sender_email = request.form.get('sender_email', '').strip()
    message = request.form.get('message', '').strip()
    move_in_date = request.form.get('move_in_date', 'Immediate').strip()
    tenant_type = request.form.get('tenant_type', 'Family').strip()

    if not sender_name or not sender_phone or not message:
        flash("Please provide your name, contact phone number, and enquiry message.", "danger")
        return redirect(url_for('property_detail', property_id=prop.id))

    enquiry = Enquiry(
        property_id=prop.id,
        user_id=curr_user.id if curr_user else None,
        sender_name=sender_name,
        sender_phone=sender_phone,
        sender_email=sender_email if sender_email else (curr_user.email if curr_user else "N/A"),
        message=message,
        move_in_date=move_in_date,
        tenant_type=tenant_type,
        status='pending'
    )
    db.session.add(enquiry)
    db.session.commit()

    flash(f"Your enquiry has been delivered directly to {prop.owner_name}. The owner will contact you shortly on {sender_phone}.", "success")
    return redirect(url_for('property_detail', property_id=prop.id))


@app.route('/property/<int:property_id>/schedule-visit', methods=['POST'])
def schedule_visit(property_id):
    prop = Property.query.get_or_404(property_id)
    curr_user = get_current_user()

    visitor_name = request.form.get('visitor_name', '').strip()
    visitor_phone = request.form.get('visitor_phone', '').strip()
    visitor_email = request.form.get('visitor_email', '').strip()
    preferred_date = request.form.get('preferred_date', '').strip()
    preferred_time_slot = request.form.get('preferred_time_slot', 'Morning (9:00 AM - 12:00 PM)').strip()
    notes = request.form.get('notes', '').strip()

    if not visitor_name or not visitor_phone or not preferred_date:
        flash("Please provide your name, phone number, and preferred visit date.", "danger")
        return redirect(url_for('property_detail', property_id=prop.id))

    visit = VisitRequest(
        property_id=prop.id,
        user_id=curr_user.id if curr_user else None,
        visitor_name=visitor_name,
        visitor_phone=visitor_phone,
        visitor_email=visitor_email if visitor_email else (curr_user.email if curr_user else "N/A"),
        preferred_date=preferred_date,
        preferred_time_slot=preferred_time_slot,
        notes=notes,
        status='pending'
    )
    db.session.add(visit)
    db.session.commit()

    flash(f"Property visit appointment requested for {preferred_date} ({preferred_time_slot}). The owner has been notified.", "success")
    return redirect(url_for('property_detail', property_id=prop.id))


@app.route('/property/<int:property_id>/report', methods=['POST'])
def report_property(property_id):
    prop = Property.query.get_or_404(property_id)
    curr_user = get_current_user()

    reporter_name = request.form.get('reporter_name', '').strip()
    reporter_email = request.form.get('reporter_email', '').strip()
    reason = request.form.get('reason', 'Inaccurate Details').strip()
    details = request.form.get('details', '').strip()

    if not reporter_name or not details:
        flash("Please provide your name and details of the report.", "danger")
        return redirect(url_for('property_detail', property_id=prop.id))

    report = PropertyReport(
        property_id=prop.id,
        user_id=curr_user.id if curr_user else None,
        reporter_name=reporter_name,
        reporter_email=reporter_email if reporter_email else "N/A",
        reason=reason,
        details=details,
        status='pending'
    )
    db.session.add(report)
    db.session.commit()

    flash("Thank you for your vigilance. Our quality team will inspect this listing promptly.", "info")
    return redirect(url_for('property_detail', property_id=prop.id))


@app.route('/property/<int:property_id>/feedback', methods=['GET', 'POST'])
def property_feedback(property_id):
    prop = Property.query.get_or_404(property_id)
    curr_user = get_current_user()

    if request.method == 'POST':
        reviewer_name = request.form.get('reviewer_name', '').strip()
        reviewer_email = request.form.get('reviewer_email', '').strip()
        rating = request.form.get('rating', 5, type=int)
        visit_type = request.form.get('visit_type', 'Visited in Person').strip()
        headline = request.form.get('headline', '').strip()
        comment = request.form.get('comment', '').strip()
        
        water_rating = request.form.get('water_rating', 5, type=int)
        location_rating = request.form.get('location_rating', 5, type=int)
        landlord_rating = request.form.get('landlord_rating', 5, type=int)

        if not reviewer_name or not comment:
            flash("Please provide your name and your feedback comments.", "danger")
            return redirect(url_for('property_feedback', property_id=prop.id))

        fb = PropertyFeedback(
            property_id=prop.id,
            user_id=curr_user.id if curr_user else None,
            reviewer_name=reviewer_name,
            reviewer_email=reviewer_email if reviewer_email else (curr_user.email if curr_user else None),
            rating=max(1, min(5, rating)),
            visit_type=visit_type,
            headline=headline,
            comment=comment,
            water_rating=max(1, min(5, water_rating)),
            location_rating=max(1, min(5, location_rating)),
            landlord_rating=max(1, min(5, landlord_rating)),
            is_approved=True
        )
        db.session.add(fb)
        db.session.commit()

        flash(f"Thank you for sharing your feedback on {prop.title}! Your review helps Kerala tenants make informed decisions.", "success")
        return redirect(url_for('property_feedback', property_id=prop.id))

    # GET: fetch all approved feedbacks
    feedbacks = prop.feedbacks.filter_by(is_approved=True).order_by(PropertyFeedback.id.desc()).all()

    # Calculate sub-averages
    water_avg = round(sum(f.water_rating for f in feedbacks) / len(feedbacks), 1) if feedbacks else 0.0
    location_avg = round(sum(f.location_rating for f in feedbacks) / len(feedbacks), 1) if feedbacks else 0.0
    landlord_avg = round(sum(f.landlord_rating for f in feedbacks) / len(feedbacks), 1) if feedbacks else 0.0

    return render_template(
        'feedback.html',
        property=prop,
        feedbacks=feedbacks,
        water_avg=water_avg,
        location_avg=location_avg,
        landlord_avg=landlord_avg
    )



# -------------------------------------------------------------
# Favourites & Side-by-Side Comparison
# -------------------------------------------------------------

@app.route('/favorite/toggle/<int:property_id>', methods=['POST'])
def toggle_favorite(property_id):
    prop = Property.query.get_or_404(property_id)
    curr_user = get_current_user()

    if curr_user:
        fav = Favorite.query.filter_by(user_id=curr_user.id, property_id=prop.id).first()
        if fav:
            db.session.delete(fav)
            db.session.commit()
            status = 'removed'
        else:
            new_fav = Favorite(user_id=curr_user.id, property_id=prop.id)
            db.session.add(new_fav)
            db.session.commit()
            status = 'added'
    else:
        # Guest favorites in session
        guest_favs = session.get('guest_favorites', [])
        if property_id in guest_favs:
            guest_favs.remove(property_id)
            status = 'removed'
        else:
            guest_favs.append(property_id)
            status = 'added'
        session['guest_favorites'] = guest_favs

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        return jsonify({'status': status, 'property_id': property_id})
    
    flash("Favourites updated.", "success")
    return redirect(request.referrer or url_for('properties'))


@app.route('/saved-homes')
def saved_homes():
    curr_user = get_current_user()
    if curr_user:
        favs = Favorite.query.filter_by(user_id=curr_user.id).order_by(Favorite.id.desc()).all()
        saved_props = [f.property_rel for f in favs if f.property_rel]
    else:
        guest_ids = session.get('guest_favorites', [])
        saved_props = Property.query.filter(Property.id.in_(guest_ids)).all() if guest_ids else []

    # Recently viewed
    recent_ids = session.get('recently_viewed', [])
    recently_viewed = Property.query.filter(Property.id.in_(recent_ids)).all() if recent_ids else []

    return render_template(
        'saved_homes.html',
        saved_properties=saved_props,
        recently_viewed=recently_viewed
    )


@app.route('/compare')
def compare():
    compare_ids = session.get('compare_ids', [])
    # Allow url query param override e.g. /compare?ids=1,2,3
    query_ids = request.args.get('ids')
    if query_ids:
        try:
            compare_ids = [int(i.strip()) for i in query_ids.split(',') if i.strip()]
        except ValueError:
            pass

    properties = Property.query.filter(Property.id.in_(compare_ids)).limit(3).all() if compare_ids else []
    return render_template('compare.html', properties=properties)


@app.route('/compare/toggle/<int:property_id>', methods=['POST'])
def toggle_compare(property_id):
    compare_ids = session.get('compare_ids', [])
    if property_id in compare_ids:
        compare_ids.remove(property_id)
        status = 'removed'
        msg = "Removed from comparison."
    else:
        if len(compare_ids) >= 3:
            return jsonify({'status': 'full', 'message': 'You can compare up to 3 homes at once. Please remove one first.'}), 400
        compare_ids.append(property_id)
        status = 'added'
        msg = "Added to comparison."
    
    session['compare_ids'] = compare_ids
    return jsonify({'status': status, 'message': msg, 'count': len(compare_ids), 'compare_ids': compare_ids})


@app.route('/compare/clear', methods=['POST'])
def clear_compare():
    session['compare_ids'] = []
    flash("Comparison list cleared.", "info")
    return redirect(url_for('compare'))


# -------------------------------------------------------------
# List Your Property (Submission Workflow)
# -------------------------------------------------------------

@app.route('/list-property', methods=['GET', 'POST'])
def list_property():
    curr_user = get_current_user()

    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        district = request.form.get('district', '').strip()
        city_town = request.form.get('city_town', '').strip()
        locality = request.form.get('locality', '').strip()
        full_address = request.form.get('full_address', '').strip()
        pin_code = request.form.get('pin_code', '').strip()
        property_type = request.form.get('property_type', '').strip()
        bhk = request.form.get('bhk', type=int)
        bathrooms = request.form.get('bathrooms', type=int)
        balconies = request.form.get('balconies', 1, type=int)
        sqft_area = request.form.get('sqft_area', type=int)
        monthly_rent = request.form.get('monthly_rent', type=int)
        security_deposit = request.form.get('security_deposit', type=int)
        maintenance = request.form.get('maintenance_charges', 0, type=int)
        furnishing = request.form.get('furnishing', '').strip()
        parking = request.form.get('parking', '').strip()
        water_supply = request.form.get('water_supply', '').strip()
        electricity = request.form.get('electricity', '').strip()
        kitchen_type = request.form.get('kitchen_type', '').strip()
        pet_policy = request.form.get('pet_policy', 'Pets Allowed').strip()
        tenant_preference = request.form.get('tenant_preference', 'Family Preferred').strip()
        availability_date = request.form.get('availability_date', 'Immediate').strip()
        description = request.form.get('description', '').strip()
        nearby_landmarks = request.form.get('nearby_landmarks', '').strip()

        # Contact Info
        owner_name = request.form.get('owner_name', '').strip()
        owner_contact_type = request.form.get('owner_contact_type', 'Individual Owner').strip()
        contact_phone = request.form.get('contact_phone', '').strip()
        whatsapp_number = request.form.get('whatsapp_number', '').strip()
        contact_email = request.form.get('contact_email', '').strip()

        # Validation
        if not title or not district or not monthly_rent or not security_deposit or not bhk or not sqft_area or not contact_phone:
            flash("Please fill in all mandatory property, pricing, and contact fields.", "danger")
            return render_template('list_property.html')

        # Auto-generate unique property code e.g. NK-EKM-2024-912
        now_utc = datetime.now(timezone.utc)
        dist_code = district[:3].upper()
        prop_code = f"NK-{dist_code}-{now_utc.strftime('%y%m')}-{int(now_utc.timestamp()) % 10000}"

        # Generate slug
        slug = f"{title.lower().replace(' ', '-')[:50]}"

        # Coordinates approximation based on district if not explicitly provided
        dist_meta = next((d for d in KERALA_DISTRICTS_INFO if d['name'].lower() == district.lower()), None)
        lat = dist_meta['lat'] if dist_meta else 10.0
        lng = dist_meta['lng'] if dist_meta else 76.3

        new_prop = Property(
            property_code=prop_code,
            title=title,
            slug=slug,
            description=description,
            property_type=property_type,
            bhk=bhk,
            bathrooms=bathrooms or 1,
            balconies=balconies or 0,
            sqft_area=sqft_area,
            monthly_rent=monthly_rent,
            security_deposit=security_deposit,
            maintenance_charges=maintenance or 0,
            furnishing=furnishing,
            parking=parking,
            water_supply=water_supply,
            electricity=electricity,
            kitchen_type=kitchen_type,
            pet_policy=pet_policy,
            tenant_preference=tenant_preference,
            availability_date=availability_date,
            status='Available',
            # Registered owners get auto-approved or pending based on admin policy
            approval_status='approved' if (curr_user and curr_user.is_verified) else 'pending',
            is_verified=False,
            is_featured=False,
            is_sample_demo=False,
            district=district,
            city_town=city_town,
            locality=locality,
            full_address=full_address,
            pin_code=pin_code,
            latitude=lat,
            longitude=lng,
            nearby_landmarks=nearby_landmarks,
            owner_id=curr_user.id if curr_user else None,
            owner_name=owner_name if owner_name else (curr_user.full_name if curr_user else "Authorized Owner"),
            owner_contact_type=owner_contact_type,
            contact_phone=contact_phone,
            whatsapp_number=whatsapp_number if whatsapp_number else contact_phone,
            contact_email=contact_email if contact_email else (curr_user.email if curr_user else ""),
            owner_verified=bool(curr_user and curr_user.is_verified)
        )
        db.session.add(new_prop)
        db.session.flush()

        # Handle Photo Uploads
        uploaded_files = request.files.getlist('property_photos')
        saved_count = 0
        for idx, file in enumerate(uploaded_files):
            file_url = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
            if file_url:
                caption = "Exterior View" if idx == 0 else f"Interior View {idx}"
                img = PropertyImage(
                    property_id=new_prop.id,
                    image_url=file_url,
                    caption=caption,
                    image_order=idx,
                    is_primary=(idx == 0)
                )
                db.session.add(img)
                saved_count += 1

        # If no photos were uploaded, attach default verified exterior placeholder
        if saved_count == 0:
            default_img = PropertyImage(
                property_id=new_prop.id,
                image_url="/static/images/hero-kerala.jpg",
                caption="Exterior Preview",
                image_order=0,
                is_primary=True
            )
            db.session.add(default_img)

        db.session.commit()

        if new_prop.approval_status == 'pending':
            flash(f"Property '{title}' submitted successfully! Our administrative team will review your photos and contact info before publishing.", "success")
        else:
            flash(f"Property '{title}' is now live on NestKerala!", "success")

        if curr_user and curr_user.is_owner_or_agent():
            return redirect(url_for('owner_dashboard'))
        return redirect(url_for('property_detail', property_id=new_prop.id))

    return render_template('list_property.html')


# -------------------------------------------------------------
# User & Owner Authentication Routes
# -------------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        phone = request.form.get('phone', '').strip()
        role = request.form.get('role', 'tenant').strip()
        agency_name = request.form.get('agency_name', '').strip()

        if not full_name or not email or not password or not phone:
            flash("Please fill in all mandatory registration fields.", "danger")
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash("An account with that email address already exists. Please sign in.", "warning")
            return redirect(url_for('login'))

        user = User(
            full_name=full_name,
            email=email,
            phone=phone,
            role=role if role in ['tenant', 'owner', 'agent'] else 'tenant',
            agency_name=agency_name if role == 'agent' else None,
            is_verified=(role == 'tenant') # Owners/Agents reviewed or verified
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Log user in
        session['user_id'] = user.id
        session['user_role'] = user.role
        session['user_name'] = user.full_name
        flash(f"Welcome to NestKerala, {user.full_name}! Your account is active.", "success")

        if user.is_owner_or_agent():
            return redirect(url_for('owner_dashboard'))
        return redirect(url_for('index'))

    return render_template('auth/register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('index'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        next_url = request.args.get('next')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_role'] = user.role
            session['user_name'] = user.full_name
            flash(f"Welcome back, {user.full_name}!", "success")

            if next_url:
                return redirect(next_url)
            if user.is_admin():
                return redirect(url_for('admin_dashboard'))
            if user.is_owner_or_agent():
                return redirect(url_for('owner_dashboard'))
            return redirect(url_for('index'))

        flash("Invalid email or password. Please try again.", "danger")

    return render_template('auth/login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_role', None)
    session.pop('user_name', None)
    flash("You have successfully signed out.", "info")
    return redirect(url_for('index'))


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = get_current_user()
    if request.method == 'POST':
        user.full_name = request.form.get('full_name', user.full_name).strip()
        user.phone = request.form.get('phone', user.phone).strip()
        if user.role == 'agent':
            user.agency_name = request.form.get('agency_name', user.agency_name).strip()

        new_password = request.form.get('new_password', '')
        if new_password:
            user.set_password(new_password)
            flash("Password updated successfully.", "success")

        db.session.commit()
        session['user_name'] = user.full_name
        flash("Your profile details have been updated.", "success")

    # Inquiries sent by this user
    sent_enquiries = Enquiry.query.filter_by(user_id=user.id).order_by(Enquiry.id.desc()).all()
    # Visit requests sent by this user
    sent_visits = VisitRequest.query.filter_by(user_id=user.id).order_by(VisitRequest.id.desc()).all()

    return render_template(
        'auth/profile.html',
        user=user,
        sent_enquiries=sent_enquiries,
        sent_visits=sent_visits
    )


# -------------------------------------------------------------
# Owner & Agent Management Dashboard
# -------------------------------------------------------------

@app.route('/dashboard/owner')
@login_required
@role_required('owner', 'agent', 'admin')
def owner_dashboard():
    user = get_current_user()

    # Admin can see all, owners see their own properties
    if user.is_admin():
        properties = Property.query.order_by(Property.id.desc()).all()
    else:
        properties = Property.query.filter_by(owner_id=user.id).order_by(Property.id.desc()).all()

    prop_ids = [p.id for p in properties]

    # Incoming enquiries for owner's properties
    enquiries = Enquiry.query.filter(Enquiry.property_id.in_(prop_ids)).order_by(Enquiry.id.desc()).all() if prop_ids else []
    # Incoming visit requests for owner's properties
    visit_requests = VisitRequest.query.filter(VisitRequest.property_id.in_(prop_ids)).order_by(VisitRequest.id.desc()).all() if prop_ids else []

    total_properties = len(properties)
    available_count = sum(1 for p in properties if p.status == 'Available')
    rented_count = sum(1 for p in properties if p.status == 'Rented')
    pending_visits = sum(1 for v in visit_requests if v.status == 'pending')

    return render_template(
        'dashboard/owner.html',
        user=user,
        properties=properties,
        enquiries=enquiries,
        visit_requests=visit_requests,
        total_properties=total_properties,
        available_count=available_count,
        rented_count=rented_count,
        pending_visits=pending_visits
    )


@app.route('/property/<int:property_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_property(property_id):
    user = get_current_user()
    prop = Property.query.get_or_404(property_id)

    # Check authorization
    if not user.is_admin() and prop.owner_id != user.id:
        flash("You do not have permission to edit this listing.", "danger")
        return redirect(url_for('owner_dashboard'))

    if request.method == 'POST':
        prop.title = request.form.get('title', prop.title).strip()
        prop.district = request.form.get('district', prop.district).strip()
        prop.city_town = request.form.get('city_town', prop.city_town).strip()
        prop.locality = request.form.get('locality', prop.locality).strip()
        prop.full_address = request.form.get('full_address', prop.full_address).strip()
        prop.monthly_rent = request.form.get('monthly_rent', prop.monthly_rent, type=int)
        prop.security_deposit = request.form.get('security_deposit', prop.security_deposit, type=int)
        prop.maintenance_charges = request.form.get('maintenance_charges', prop.maintenance_charges, type=int)
        prop.bhk = request.form.get('bhk', prop.bhk, type=int)
        prop.bathrooms = request.form.get('bathrooms', prop.bathrooms, type=int)
        prop.sqft_area = request.form.get('sqft_area', prop.sqft_area, type=int)
        prop.furnishing = request.form.get('furnishing', prop.furnishing).strip()
        prop.parking = request.form.get('parking', prop.parking).strip()
        prop.water_supply = request.form.get('water_supply', prop.water_supply).strip()
        prop.electricity = request.form.get('electricity', prop.electricity).strip()
        prop.kitchen_type = request.form.get('kitchen_type', prop.kitchen_type).strip()
        prop.pet_policy = request.form.get('pet_policy', prop.pet_policy).strip()
        prop.tenant_preference = request.form.get('tenant_preference', prop.tenant_preference).strip()
        prop.status = request.form.get('status', prop.status).strip()
        prop.description = request.form.get('description', prop.description).strip()
        prop.contact_phone = request.form.get('contact_phone', prop.contact_phone).strip()
        prop.whatsapp_number = request.form.get('whatsapp_number', prop.whatsapp_number).strip()

        # Handle any new photo uploads
        new_photos = request.files.getlist('new_photos')
        for file in new_photos:
            file_url = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
            if file_url:
                img = PropertyImage(
                    property_id=prop.id,
                    image_url=file_url,
                    caption="Additional View",
                    image_order=prop.images.count() + 1,
                    is_primary=False
                )
                db.session.add(img)

        db.session.commit()
        flash(f"Listing '{prop.title}' has been successfully updated.", "success")
        return redirect(url_for('owner_dashboard'))

    return render_template('dashboard/edit_property.html', property=prop)


@app.route('/property/<int:property_id>/delete', methods=['POST'])
@login_required
def delete_property(property_id):
    user = get_current_user()
    prop = Property.query.get_or_404(property_id)

    if not user.is_admin() and prop.owner_id != user.id:
        flash("You are not authorized to delete this property.", "danger")
        return redirect(url_for('owner_dashboard'))

    title = prop.title
    db.session.delete(prop)
    db.session.commit()
    flash(f"Property '{title}' has been permanently deleted.", "info")
    return redirect(url_for('owner_dashboard'))


@app.route('/property/<int:property_id>/toggle-status', methods=['POST'])
@login_required
def toggle_property_status(property_id):
    user = get_current_user()
    prop = Property.query.get_or_404(property_id)

    if not user.is_admin() and prop.owner_id != user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for('owner_dashboard'))

    prop.status = 'Rented' if prop.status == 'Available' else 'Available'
    db.session.commit()
    flash(f"Status for '{prop.title}' changed to {prop.status}.", "success")
    return redirect(request.referrer or url_for('owner_dashboard'))


@app.route('/property/<int:property_id>/update-rent', methods=['POST'])
@login_required
def update_property_rent(property_id):
    user = get_current_user()
    prop = Property.query.get_or_404(property_id)

    if not user.is_admin() and prop.owner_id != user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for('owner_dashboard'))

    new_rent = request.form.get('monthly_rent', type=int)
    new_deposit = request.form.get('security_deposit', type=int)
    if new_rent:
        prop.monthly_rent = new_rent
    if new_deposit:
        prop.security_deposit = new_deposit

    db.session.commit()
    flash(f"Pricing updated for '{prop.title}'.", "success")
    return redirect(request.referrer or url_for('owner_dashboard'))


@app.route('/dashboard/visit/<int:visit_id>/status', methods=['POST'])
@login_required
def update_visit_status(visit_id):
    visit = VisitRequest.query.get_or_404(visit_id)
    prop = db.session.get(Property, visit.property_id)
    user = get_current_user()

    if not user.is_admin() and prop.owner_id != user.id:
        flash("Unauthorized.", "danger")
        return redirect(url_for('owner_dashboard'))

    new_status = request.form.get('status', 'confirmed')
    reply_msg = request.form.get('owner_reply', '')
    if new_status in ['confirmed', 'declined', 'completed']:
        visit.status = new_status
        if reply_msg:
            visit.owner_reply = reply_msg
        db.session.commit()
        flash(f"Visit request marked as {new_status.capitalize()}.", "success")

    return redirect(url_for('owner_dashboard'))


# -------------------------------------------------------------
# Admin Control Panel
# -------------------------------------------------------------

@app.route('/admin')
@login_required
@role_required('admin')
def admin_dashboard():
    # Platform stats
    total_properties = Property.query.count()
    available_count = Property.query.filter_by(status='Available', approval_status='approved').count()
    rented_count = Property.query.filter_by(status='Rented').count()
    pending_approvals = Property.query.filter_by(approval_status='pending').all()
    pending_count = len(pending_approvals)
    
    total_users = User.query.count()
    owners_count = User.query.filter_by(role='owner').count()
    agents_count = User.query.filter_by(role='agent').count()
    tenants_count = User.query.filter_by(role='tenant').count()

    total_enquiries = Enquiry.query.count()
    reports = PropertyReport.query.order_by(PropertyReport.id.desc()).all()
    all_properties = Property.query.order_by(Property.id.desc()).all()
    all_users = User.query.order_by(User.id.desc()).all()

    return render_template(
        'dashboard/admin.html',
        total_properties=total_properties,
        available_count=available_count,
        rented_count=rented_count,
        pending_count=pending_count,
        pending_approvals=pending_approvals,
        total_users=total_users,
        owners_count=owners_count,
        agents_count=agents_count,
        tenants_count=tenants_count,
        total_enquiries=total_enquiries,
        reports=reports,
        properties=all_properties,
        users=all_users
    )


@app.route('/admin/property/<int:property_id>/approve', methods=['POST'])
@login_required
@role_required('admin')
def admin_approve_property(property_id):
    prop = Property.query.get_or_404(property_id)
    prop.approval_status = 'approved'
    db.session.commit()
    flash(f"Listing '{prop.title}' has been approved and published live.", "success")
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/property/<int:property_id>/reject', methods=['POST'])
@login_required
@role_required('admin')
def admin_reject_property(property_id):
    prop = Property.query.get_or_404(property_id)
    prop.approval_status = 'rejected'
    db.session.commit()
    flash(f"Listing '{prop.title}' has been rejected.", "warning")
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/property/<int:property_id>/toggle-verify', methods=['POST'])
@login_required
@role_required('admin')
def admin_toggle_verify(property_id):
    prop = Property.query.get_or_404(property_id)
    prop.is_verified = not prop.is_verified
    db.session.commit()
    status_str = "Verified by NestKerala badge added" if prop.is_verified else "Verification badge removed"
    flash(f"{status_str} for '{prop.title}'.", "success")
    return redirect(request.referrer or url_for('admin_dashboard'))


@app.route('/admin/property/<int:property_id>/toggle-featured', methods=['POST'])
@login_required
@role_required('admin')
def admin_toggle_featured(property_id):
    prop = Property.query.get_or_404(property_id)
    prop.is_featured = not prop.is_featured
    db.session.commit()
    status_str = "marked as Featured" if prop.is_featured else "removed from Featured"
    flash(f"Listing '{prop.title}' {status_str}.", "success")
    return redirect(request.referrer or url_for('admin_dashboard'))


@app.route('/admin/report/<int:report_id>/resolve', methods=['POST'])
@login_required
@role_required('admin')
def admin_resolve_report(report_id):
    rep = PropertyReport.query.get_or_404(report_id)
    action = request.form.get('action', 'resolved')
    if action == 'remove_listing':
        prop = db.session.get(Property, rep.property_id)
        if prop:
            prop.approval_status = 'rejected'
            rep.status = 'resolved'
            db.session.commit()
            flash(f"Report resolved: Listing '{prop.title}' removed from active view.", "warning")
            return redirect(url_for('admin_dashboard'))
    
    rep.status = 'resolved'
    db.session.commit()
    flash("Report marked as resolved.", "info")
    return redirect(url_for('admin_dashboard'))


# -------------------------------------------------------------
# Utility, Error Handlers & Bilingual Switcher
# -------------------------------------------------------------

@app.route('/set-language/<lang>')
def set_language(lang):
    if lang in ['en', 'ml']:
        session['lang'] = lang
    return redirect(request.referrer or url_for('index'))


@app.errorhandler(404)
def page_not_found(e):
    return render_template(
        'error.html',
        error_code='404',
        error_title='Property or Page Not Found',
        error_message='The property listing or URL you are trying to visit is not available or has been unlisted.'
    ), 404


@app.errorhandler(500)
def server_error(e):
    return render_template(
        'error.html',
        error_code='500',
        error_title='Internal Server Notice',
        error_message='An unexpected error occurred while processing your request. Please try again shortly.'
    ), 500


# -------------------------------------------------------------
# Application Initialization & CLI commands
# -------------------------------------------------------------

with app.app_context():
    db.create_all()
    seed_database(app)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
