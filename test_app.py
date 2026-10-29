from app import app, db
from models import Property, User, Enquiry, VisitRequest

def run_tests():
    print("Testing NestKerala Platform...")
    client = app.test_client()

    # 1. Test Homepage
    resp = client.get('/')
    assert resp.status_code == 200, f"Homepage failed with {resp.status_code}"
    assert b"NestKerala" in resp.data, "NestKerala branding missing on homepage"
    assert b"Find Your" in resp.data
    print("✓ Homepage test passed (200 OK)")

    # 2. Test Properties Explore Page
    resp = client.get('/properties')
    assert resp.status_code == 200, f"Properties page failed with {resp.status_code}"
    assert b"Verified Rental Properties" in resp.data
    print("✓ Properties explore page test passed (200 OK)")

    # 3. Test District Filter (Ernakulam)
    resp = client.get('/properties?district=Ernakulam')
    assert resp.status_code == 200
    assert b"Ernakulam" in resp.data
    print("✓ District filter test passed (200 OK)")

    # 4. Test Smart Recommendation System (Search with extreme filters that return 0 exact matches)
    resp = client.get('/properties?district=Wayanad&min_rent=80000')
    assert resp.status_code == 200
    assert b"No Exact Matches" in resp.data or b"Similar Homes" in resp.data, "Smart recommendation banner not rendered when 0 exact matches"
    print("✓ Smart Recommendation System test passed (200 OK)")

    # 5. Test Property Detail Page
    with app.app_context():
        prop = Property.query.first()
        prop_id = prop.id
        prop_slug = prop.slug

    resp = client.get(f'/property/{prop_id}/{prop_slug}')
    assert resp.status_code == 200, f"Property detail failed with {resp.status_code}"
    assert b"Call Owner" in resp.data or b"tel:" in resp.data
    assert b"WhatsApp" in resp.data
    assert b"Key Nearby Landmarks" in resp.data
    assert b"propertyMap" in resp.data
    print(f"✓ Property Details page test passed for ID {prop_id} (200 OK)")

    # 6. Test Enquiry Submission
    resp = client.post(f'/property/{prop_id}/enquiry', data={
        'sender_name': 'Test Seeker',
        'sender_phone': '+91 98470 99999',
        'sender_email': 'test@seeker.com',
        'message': 'Hello, interested in this rental villa.',
        'tenant_type': 'Family',
        'move_in_date': 'Immediate'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Your enquiry has been delivered directly" in resp.data
    print("✓ Direct Enquiry submission test passed (200 OK)")

    # 7. Test Property Visit Scheduling
    resp = client.post(f'/property/{prop_id}/schedule-visit', data={
        'visitor_name': 'Test Visitor',
        'visitor_phone': '+91 98470 88888',
        'visitor_email': 'visitor@test.com',
        'preferred_date': '2026-11-15',
        'preferred_time_slot': 'Morning (9:00 AM - 12:00 PM)',
        'notes': 'Visiting with spouse.'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Property visit appointment requested" in resp.data
    print("✓ Property Visit Scheduling test passed (200 OK)")

    # 8. Test Comparison Page
    resp = client.get('/compare')
    assert resp.status_code == 200
    print("✓ Comparison page test passed (200 OK)")

    # 9. Test Saved Homes Page
    resp = client.get('/saved-homes')
    assert resp.status_code == 200
    print("✓ Saved Homes page test passed (200 OK)")

    # 10. Test Login Page & Demo Login
    resp = client.post('/login', data={
        'email': 'admin@nestkerala.com',
        'password': 'Admin@123'
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Admin Control Center" in resp.data
    print("✓ Admin Login & Control Center test passed (200 OK)")

    # 11. Test List Property Page
    resp = client.get('/list-property')
    assert resp.status_code == 200
    assert b"List Your Rental Property" in resp.data
    print("✓ List Property page test passed (200 OK)")

    # 12. Test Owner Dashboard
    resp = client.get('/dashboard/owner')
    assert resp.status_code == 200
    assert b"Owner & Agent Dashboard" in resp.data
    print("✓ Owner Dashboard test passed (200 OK)")

    # 13. Test Bilingual Language Toggle (Malayalam)
    resp = client.get('/set-language/ml', follow_redirects=True)
    assert resp.status_code == 200
    print("✓ Bilingual language toggle test passed (200 OK)")

    # 14. Test Property Feedback Page (GET)
    resp = client.get(f'/property/{prop_id}/feedback')
    assert resp.status_code == 200
    assert b"Tenant & Visitor Feedback" in resp.data
    assert b"Add Your Feedback" in resp.data
    print("✓ Property Feedback page GET test passed (200 OK)")

    # 15. Test Property Feedback Submission (POST)
    resp = client.post(f'/property/{prop_id}/feedback', data={
        'reviewer_name': 'Devika Pillai',
        'reviewer_email': 'devika@gmail.com',
        'rating': 5,
        'visit_type': 'Visited in Person',
        'headline': 'Spacious and highly peaceful home',
        'comment': 'Visited this property last week. Road access is wide and neighborhood is very quiet.',
        'water_rating': 5,
        'location_rating': 5,
        'landlord_rating': 5
    }, follow_redirects=True)
    assert resp.status_code == 200
    assert b"Thank you for sharing your feedback" in resp.data
    print("✓ Property Feedback Submission test passed (200 OK)")

    print("\n🎉 ALL 15 TEST SUITES PASSED FLAWLESSLY!")

if __name__ == '__main__':
    run_tests()
