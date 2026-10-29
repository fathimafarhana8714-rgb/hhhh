# NestKerala – Find Your Perfect Home in Kerala

**NestKerala** is a premium, modern, realistic, and fully functional real estate rental marketplace designed specifically for Kerala. Inspired by platforms such as Housing.com, 99acres, and Magicbricks, NestKerala brings authentic Kerala architecture, genuine property specifications, direct owner contact credentials, and verified listings across all 14 districts of Kerala.

---

## 🌟 Key Features

### 1. Premium Kerala Architectural Design & Identity
- **Brand Palette:** Deep emerald green (`#0F4C3A`), warm temple gold (`#C89B3C`), crisp white, and cream (`#FDFBF7`).
- **Custom NestKerala Logo:** Integrated Kerala sloping eaves (*Charupadi / Poomukham*) roof and nest motif.
- **Bilingual Interface:** Instant language toggle between English and മലയാളം (Malayalam) across navigation and headers.
- **Fully Responsive:** Smooth experience across mobile, tablet, and desktop screens with an interactive mobile drawer navigation.

### 2. All 14 Districts of Kerala Supported
Comprehensive coverage with realistic geographic data, local towns, PIN codes, coordinates, and landmarks for all districts:
1. **Thiruvananthapuram** (Kowdiar, Technopark Kazhakkoottam, Pattom)
2. **Kollam** (Asramam, Tangasseri)
3. **Pathanamthitta** (Thiruvalla NRI Villas, Muthoor)
4. **Alappuzha** (Mullakkal Canal-side homes, Cherthala)
5. **Kottayam** (Kanjikuzhi, Pala)
6. **Idukki** (Thodupuzha foothills, Munnar bypass)
7. **Ernakulam** (Kakkanad Infopark, Marine Drive Waterfront, Panampilly Nagar)
8. **Thrissur** (Punkunnam Heritage, Swaraj Round)
9. **Palakkad** (Kalpathy Heritage Village, Chandranagar)
10. **Malappuram** (Manjeri, Perinthalmanna)
11. **Kozhikode** (Nadakkavu, Cyberpark, Calicut Beach)
12. **Wayanad** (Kalpetta Highland Plantation Villas)
13. **Kannur** (Payyambalam Coastal Residences)
14. **Kasaragod** (Vidyanagar, Northern Kerala)

### 3. Real Kerala Rental Property Specifications
Every listing includes detailed housing attributes tailored to Kerala realities:
- **Property ID:** Structured code (e.g., `NK-EKM-2024-001`)
- **Photographs Gallery:** Multi-angle photographs (Exterior, Living Room, Master Bedroom, Secondary Bedroom, Modular Kitchen, Bathrooms, Balcony, Covered Car Porch)
- **Monthly Rent & Security Deposit:** Transparent Kerala deposit norms
- **Water Source:** KWA (Kerala Water Authority) connection, perennial open well sweet water, borewell, and rainwater harvesting
- **Electricity & Power:** 3-Phase KSEB, solar hybrid rooftop power, inverter battery backup
- **Parking Facilities:** Covered car porch (single/multiple cars + two-wheelers)
- **Kitchen Type:** Modular kitchen with separate work area, smoke chimney, traditional hearths
- **Pet Policy & Tenant Preferences:** Family preferred, bachelors allowed, corporate lease

### 4. Direct Owner & Agent Communication (Zero Middleman)
- **Call Owner Button:** Initiates phone calls directly to authorized numbers (`tel:+91...`).
- **WhatsApp Owner Button:** Opens pre-filled WhatsApp chat with the property title and ID (`https://wa.me/...`).
- **Send Direct Enquiry:** Stored in database, accessible in owner dashboard.
- **Request Property Visit:** Prospective tenants can schedule viewing appointments (date + time slot: Morning / Afternoon / Evening).

### 5. Advanced Search & Smart Recommendation Engine
- **Search Filters:** District, City/Town, Locality keyword, BHK (1, 2, 3, 4+ BHK), Min/Max Rent, Property Type, Furnishing, Parking, Pet-friendly, Verified only.
- **Smart Recommendations:** When exact criteria return low or zero results, the algorithm ranks and recommends alternative homes based on neighboring districts, budget proximity (±15-35%), and BHK affinity under the header *"No Exact Matches – Similar Homes You May Like"*.

### 6. Side-by-Side Property Comparison
- Select up to 3 properties from any card or details page.
- Sticky floating compare bar at the bottom of the viewport with live counter.
- Comprehensive matrix comparing rent, deposit, maintenance, BHK, baths, area, furnishing, parking, water, electricity, kitchen, pet policy, location, and owner contacts.

### 7. Interactive Location & Google Maps
- Integrated **Leaflet.js / OpenStreetMap** with custom emerald map pins.
- **View on Google Maps** direct external navigation button.
- Categorized Nearby Landmarks table with verified travel distances (Metro, IT Parks, Hospitals, Schools, Supermarkets).

### 8. Role-Based Dashboards & Moderation
- **Tenants:** Saved Homes shortlist, recently viewed listings, enquiry history, scheduled visit status.
- **Owners & Agents:** Add properties, upload multi-angle photos, edit listings, quick rent update, toggle status (Available / Rented), manage incoming tenant inquiries, confirm or decline visit requests.
- **Super Administrator (`/admin`):** Review pending submissions, Approve/Reject listings, assign "Verified by NestKerala" badge, feature properties, review reported listings, and monitor user accounts.

---

## 🔑 Demonstration One-Click Login Credentials

The database is pre-seeded with verified test accounts across all roles:

| Role | Email | Password | Description |
|---|---|---|---|
| **Admin** | `admin@nestkerala.com` | `Admin@123` | Full access to Admin Control Center, Approvals & Moderation |
| **Owner 1** | `kr.menon@keralahomes.in` | `Owner@123` | Homeowner with listings in Kakkanad (Kochi), Kozhikode, etc. |
| **Owner 2** | `dr.varma@heritagekerala.com` | `Owner@123` | Homeowner with Nalukettu in Kowdiar (Trivandrum), Thrissur, etc. |
| **Agent** | `mathew.kurian@malabarproperties.com` | `Agent@123` | Real estate agent with listings in Wayanad, Marine Drive, etc. |
| **Tenant** | `rahul.nair@techkerala.com` | `Tenant@123` | Active seeker with saved homes and sent visit requests |

---

## 🚀 How to Run the Application

1. Open PowerShell / Command Prompt in the project folder:
   ```powershell
   cd c:\Users\Dell\Documents\nestkerala
   ```

2. Start the application:
   ```powershell
   .\.venv\Scripts\python.exe app.py
   ```
   *Or simply double-click `run.bat`.*

3. Open your browser and visit:
   ```
   http://127.0.0.1:5000
   ```

---

## 🧪 Automated Test Suite

A complete test suite covering all 13 core functional areas is included:
```powershell
.\.venv\Scripts\python.exe test_app.py
```
Test suite verifies:
- Homepage rendering and branding
- Properties search and query filtering
- District filtering
- Smart Recommendation engine on low matches
- Property details page with Leaflet map and landmarks
- Direct Enquiry form database submission
- Property Visit booking workflow
- Saved Homes & Favorites system
- Side-by-side comparison matrix
- User authentication and role-based access
- List Your Property submission pipeline
- Owner & Agent dashboard
- Bilingual language toggle
