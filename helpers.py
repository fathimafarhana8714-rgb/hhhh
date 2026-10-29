import os
import uuid
from functools import wraps
from flask import session, redirect, url_for, flash, request
from werkzeug.utils import secure_filename
from models import User, Property

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, upload_folder):
    if not file or file.filename == '':
        return None
    if allowed_file(file.filename):
        ext = file.filename.rsplit('.', 1)[1].lower()
        unique_name = f"{uuid.uuid4().hex[:12]}_{secure_filename(file.filename)}"
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, unique_name)
        file.save(file_path)
        # Return web accessible relative path
        return f"/static/uploads/properties/{unique_name}"
    return None

def get_current_user():
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Please sign in to access this page.", "warning")
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash("Please sign in to continue.", "warning")
                return redirect(url_for('login', next=request.url))
            user = User.query.get(session['user_id'])
            if not user or (user.role not in roles and user.role != 'admin'):
                flash("You do not have permission to access that resource.", "danger")
                return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Neighboring/Regional district affinity for smart location similarity
DISTRICT_NEIGHBORS = {
    "Ernakulam": ["Thrissur", "Kottayam", "Alappuzha", "Idukki"],
    "Thiruvananthapuram": ["Kollam"],
    "Kollam": ["Thiruvananthapuram", "Pathanamthitta", "Alappuzha"],
    "Pathanamthitta": ["Kollam", "Alappuzha", "Kottayam", "Idukki"],
    "Alappuzha": ["Ernakulam", "Kottayam", "Pathanamthitta", "Kollam"],
    "Kottayam": ["Ernakulam", "Idukki", "Alappuzha", "Pathanamthitta"],
    "Idukki": ["Ernakulam", "Kottayam", "Thrissur", "Pathanamthitta"],
    "Thrissur": ["Ernakulam", "Palakkad", "Malappuram", "Idukki"],
    "Palakkad": ["Thrissur", "Malappuram"],
    "Malappuram": ["Kozhikode", "Palakkad", "Thrissur", "Wayanad"],
    "Kozhikode": ["Kannur", "Malappuram", "Wayanad"],
    "Wayanad": ["Kozhikode", "Kannur", "Malappuram"],
    "Kannur": ["Kasaragod", "Kozhikode", "Wayanad"],
    "Kasaragod": ["Kannur"]
}

def get_smart_recommendations(criteria, exclude_ids=None, limit=4):
    """
    Ranks properties based on:
    - District / Neighboring District affinity
    - Budget proximity (closest to target rent)
    - BHK match
    - Property type match
    - Furnishing match
    """
    if exclude_ids is None:
        exclude_ids = []

    target_district = criteria.get('district')
    target_rent = criteria.get('rent') # could be max_rent or avg of min/max
    target_bhk = criteria.get('bhk')
    target_type = criteria.get('property_type')
    target_furnishing = criteria.get('furnishing')

    # Candidate pool: all approved and available properties not in exclude_ids
    query = Property.query.filter(
        Property.approval_status == 'approved',
        Property.status == 'Available'
    )
    if exclude_ids:
        query = query.filter(~Property.id.in_(exclude_ids))

    all_candidates = query.all()
    if not all_candidates:
        return []

    scored_candidates = []
    for prop in all_candidates:
        score = 0
        reasons = []

        # 1. Location match
        if target_district:
            if prop.district.lower() == target_district.lower():
                score += 40
                reasons.append("Same district")
            elif prop.district in DISTRICT_NEIGHBORS.get(target_district, []):
                score += 20
                reasons.append("Neighboring district")

        # 2. BHK match
        if target_bhk:
            try:
                tbhk = int(target_bhk)
                if prop.bhk == tbhk:
                    score += 25
                    reasons.append(f"Matching {prop.bhk} BHK")
                elif abs(prop.bhk - tbhk) == 1:
                    score += 12
                    reasons.append(f"Close BHK ({prop.bhk} BHK)")
            except (ValueError, TypeError):
                pass

        # 3. Budget match
        if target_rent:
            try:
                trent = float(target_rent)
                diff_pct = abs(prop.monthly_rent - trent) / trent
                if diff_pct <= 0.15:
                    score += 25
                    reasons.append("Similar budget range")
                elif diff_pct <= 0.35:
                    score += 15
                    reasons.append("Moderate budget variance")
            except (ValueError, TypeError):
                pass

        # 4. Property type match
        if target_type and prop.property_type.lower() == target_type.lower():
            score += 10
            reasons.append(prop.property_type)

        # 5. Furnishing match
        if target_furnishing and prop.furnishing.lower() == target_furnishing.lower():
            score += 8
            reasons.append(prop.furnishing)

        scored_candidates.append({
            'property': prop,
            'score': score,
            'reasons': reasons
        })

    # Sort descending by score
    scored_candidates.sort(key=lambda x: x['score'], reverse=True)
    return [item['property'] for item in scored_candidates[:limit]]
