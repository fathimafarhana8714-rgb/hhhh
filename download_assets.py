import os
import urllib.request
import ssl

# Ensure SSL context allows valid certificates
ctx = ssl.create_default_context()

ASSETS = {
    "static/images/hero-kerala.jpg": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1920&q=80",
    "static/images/kerala-tradition.jpg": "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1200&q=80",
    
    # 14 Districts
    "static/images/districts/ernakulam.jpg": "https://images.unsplash.com/photo-1590050752117-238cb0fb12b1?auto=format&fit=crop&w=600&q=80",
    "static/images/districts/thiruvananthapuram.jpg": "https://images.unsplash.com/photo-1602216056096-3b40cc0c9944?auto=format&fit=crop&w=600&q=80",
    "static/images/districts/kozhikode.jpg": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=600&q=80",
    "static/images/districts/thrissur.jpg": "https://images.unsplash.com/photo-1613490493576-7fde63acd811?auto=format&fit=crop&w=600&q=80",
    "static/images/districts/kottayam.jpg": "https://images.unsplash.com/photo-1544735716-392fe2489ffa?auto=format&fit=crop&w=600&q=80",
    "static/images/districts/alappuzha.jpg": "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=600&q=80",
    "static/images/districts/kollam.jpg": "https://images.unsplash.com/photo-1507089947368-19c1da9775ae?auto=format&fit=crop&w=600&q=80",
    "static/images/districts/palakkad.jpg": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=600&q=80",
    "static/images/districts/malappuram.jpg": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=600&q=80",
    "static/images/districts/kannur.jpg": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=600&q=80",
    "static/images/districts/wayanad.jpg": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?auto=format&fit=crop&w=600&q=80",
    "static/images/districts/idukki.jpg": "https://images.unsplash.com/photo-1501785888041-af3ef285b470?auto=format&fit=crop&w=600&q=80",
    "static/images/districts/pathanamthitta.jpg": "https://images.unsplash.com/photo-1518780664697-55e3ad937233?auto=format&fit=crop&w=600&q=80",
    "static/images/districts/kasaragod.jpg": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=600&q=80",

    # Property Photographs (Interiors & Exteriors)
    # House 1: Luxury Villa Kakkanad Kochi
    "static/uploads/properties/prop1_ext.jpg": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop1_living.jpg": "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop1_bed1.jpg": "https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop1_bed2.jpg": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop1_kitchen.jpg": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop1_bath.jpg": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop1_balcony.jpg": "https://images.unsplash.com/photo-1512915922686-57c11dde9b6b?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop1_parking.jpg": "https://images.unsplash.com/photo-1590381105924-c72589b9ef3f?auto=format&fit=crop&w=1000&q=80",

    # House 2: Traditional Nalukettu Style Villa, Kowdiar Trivandrum
    "static/uploads/properties/prop2_ext.jpg": "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop2_living.jpg": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop2_bed1.jpg": "https://images.unsplash.com/photo-1616594039964-ae9021a400a0?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop2_bed2.jpg": "https://images.unsplash.com/photo-1540518614846-7ede433c4570?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop2_kitchen.jpg": "https://images.unsplash.com/photo-1507089947368-19c1da9775ae?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop2_bath.jpg": "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop2_balcony.jpg": "https://images.unsplash.com/photo-1513694203232-719a280e022f?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop2_parking.jpg": "https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=1000&q=80",

    # House 3: Waterfront Marine Drive Apartment, Ernakulam
    "static/uploads/properties/prop3_ext.jpg": "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop3_living.jpg": "https://images.unsplash.com/photo-1502005229762-ee1b2b8ab32f?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop3_bed1.jpg": "https://images.unsplash.com/photo-1522771739844-6a9f6d5f14af?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop3_kitchen.jpg": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop3_bath.jpg": "https://images.unsplash.com/photo-1620626011761-996317b8d101?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop3_balcony.jpg": "https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?auto=format&fit=crop&w=1000&q=80",

    # House 4: Serene Independent House, Nadakkavu Kozhikode
    "static/uploads/properties/prop4_ext.jpg": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop4_living.jpg": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop4_bed1.jpg": "https://images.unsplash.com/photo-1617325247661-675ab4b64ae2?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop4_kitchen.jpg": "https://images.unsplash.com/photo-1507089947368-19c1da9775ae?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop4_bath.jpg": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?auto=format&fit=crop&w=1000&q=80",

    # House 5: Gated Villa in Punkunnam, Thrissur
    "static/uploads/properties/prop5_ext.jpg": "https://images.unsplash.com/photo-1613490493576-7fde63acd811?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop5_living.jpg": "https://images.unsplash.com/photo-1600566753376-12c8ab7fb75b?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop5_bed1.jpg": "https://images.unsplash.com/photo-1595526114035-0d45ed16cfbf?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop5_kitchen.jpg": "https://images.unsplash.com/photo-1556911220-e15b29be8c8f?auto=format&fit=crop&w=1000&q=80",

    # House 6: Plantation Valley House, Kalpetta Wayanad
    "static/uploads/properties/prop6_ext.jpg": "https://images.unsplash.com/photo-1518780664697-55e3ad937233?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop6_living.jpg": "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop6_bed1.jpg": "https://images.unsplash.com/photo-1616594039964-ae9021a400a0?auto=format&fit=crop&w=1000&q=80",

    # House 7: Canal-side Home in Mullakkal, Alappuzha
    "static/uploads/properties/prop7_ext.jpg": "https://images.unsplash.com/photo-1593693397690-362cb9666fc2?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop7_living.jpg": "https://images.unsplash.com/photo-1502005229762-ee1b2b8ab32f?auto=format&fit=crop&w=1000&q=80",

    # House 8: Scenic Hill Villa, Thodupuzha Idukki
    "static/uploads/properties/prop8_ext.jpg": "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop8_living.jpg": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1000&q=80",

    # House 9: Modern 2 BHK Flat, Kazhakkoottam Technopark Trivandrum
    "static/uploads/properties/prop9_ext.jpg": "https://images.unsplash.com/photo-1574362848149-11496d93a7c7?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop9_living.jpg": "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1000&q=80",

    # House 10: Elegant Family Residence, Kanjikuzhi Kottayam
    "static/uploads/properties/prop10_ext.jpg": "https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop10_living.jpg": "https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1000&q=80",

    # House 11: Heritage Traditional Home, Kalpathy Palakkad
    "static/uploads/properties/prop11_ext.jpg": "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop11_living.jpg": "https://images.unsplash.com/photo-1618221195710-dd6b41faaea6?auto=format&fit=crop&w=1000&q=80",

    # House 12: Coastal House, Payyambalam Kannur
    "static/uploads/properties/prop12_ext.jpg": "https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?auto=format&fit=crop&w=1000&q=80",
    "static/uploads/properties/prop12_living.jpg": "https://images.unsplash.com/photo-1600210492486-724fe5c67fb0?auto=format&fit=crop&w=1000&q=80",
}

print(f"Downloading {len(ASSETS)} assets...")
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

for path, url in ASSETS.items():
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        continue
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp, open(path, 'wb') as out_file:
            out_file.write(resp.read())
        print(f"Downloaded: {path}")
    except Exception as e:
        print(f"Error downloading {path}: {e}")

print("Asset preparation completed.")
