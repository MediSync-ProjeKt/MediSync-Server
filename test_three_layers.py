import asyncio
from httpx import AsyncClient, ASGITransport
from backend.main import app

async def run_tests():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        print("\n=== [1/4] Testing Authentication & Profiles ===")
        # Test login
        res = await client.post("/api/auth/login", json={"email": "patient@medisync.health", "password": "patient123"})
        assert res.status_code == 200, f"Patient login failed: {res.text}"
        data = res.json()
        assert data["user"]["role"] == "patient"
        print("  ✓ Patient login verified:", data["user"]["name"])

        res = await client.post("/api/auth/login", json={"email": "doctor@medisync.health", "password": "doctor123"})
        assert res.status_code == 200
        print("  ✓ Doctor login verified:", res.json()["user"]["name"])

        res = await client.post("/api/auth/login", json={"email": "admin@hospital.health", "password": "admin123"})
        assert res.status_code == 200
        print("  ✓ Hospital Admin login verified:", res.json()["user"]["name"])

        print("\n=== [2/4] Testing Layer 1: Personal AI Health Assistant & Vault ===")
        # Inject sample report into vault
        res = await client.post("/api/sample-report?sample_type=cbc&patient_name=Sarah%20Connor")
        assert res.status_code == 200, res.text
        report_data = res.json()
        report_id = report_data["report_id"]
        token = report_data["token"]
        print(f"  ✓ Sample CBC report saved into Centralized Vault (ID: {report_id}, Token: {token})")

        # List reports in vault
        res = await client.get("/api/reports?patient_name=Sarah")
        assert res.status_code == 200
        reports = res.json()
        assert len(reports) >= 1
        print(f"  ✓ Vault listing verified: {len(reports)} reports found")

        # Chat with RAG
        res = await client.post("/api/chat", json={"message": "What is my hemoglobin level?", "report_id": report_id})
        assert res.status_code == 200
        chat_res = res.json()
        assert "11.4" in chat_res.get("reply", "") or "11.4" in chat_res.get("response", "")
        print("  ✓ RAG Chatbot verified: cited exact lab parameter 11.4 g/dL")

        print("\n=== [3/4] Testing Layer 2: Patient-Doctor Ecosystem & Pairing ===")
        # Doctor listing
        res = await client.get("/api/doctors")
        assert res.status_code == 200
        doctors = res.json()
        assert len(doctors) >= 4
        doc_id = doctors[0]["id"]
        print(f"  ✓ Doctor directory verified: {len(doctors)} specialists available")

        # Create Pairing
        res = await client.post("/api/pairings", json={"patient_name": "Sarah Connor", "doctor_id": doc_id, "notes": "Primary cardiologist pairing"})
        assert res.status_code == 200
        print(f"  ✓ Patient-Doctor pairing created with {doctors[0]['name']}")

        # Book Appointment
        res = await client.post("/api/appointments", json={
            "patient_name": "Sarah Connor",
            "patient_phone": "+1 555-0192",
            "doctor_id": doc_id,
            "date": "2026-11-28",
            "time": "10:30 AM",
            "reason": "Cardiovascular followup on CBC and lipid profile",
            "report_token": token
        })
        assert res.status_code == 200
        appt = res.json()["appointment"]
        appt_id = appt["id"]
        print(f"  ✓ Appointment booked (ID: {appt_id}) with token {token}")

        # Doctor adds notes
        res = await client.post(f"/api/reports/{report_id}/notes", json={
            "doctor_name": doctors[0]["name"],
            "notes": "Reviewed CBC parameters. Hemoglobin 11.4 warrants nutritional iron follow-up.",
            "prescription": "Ferrous sulfate 325 mg once daily with Vitamin C."
        })
        assert res.status_code == 200
        print("  ✓ Doctor consultation note and prescription signed and attached to patient chart")

        print("\n=== [4/4] Testing Layer 3: Hospital Administration Client ===")
        # List hospitals
        res = await client.get("/api/hospitals")
        assert res.status_code == 200
        hospitals = res.json()
        assert len(hospitals) >= 2
        hosp_id = hospitals[0]["id"]
        print(f"  ✓ Hospital directory verified: {len(hospitals)} hospital systems registered")

        # Pair patient with hospital
        res = await client.post(f"/api/hospitals/{hosp_id}/pair", json={"patient_name": "Sarah Connor"})
        assert res.status_code == 200
        hosp_pairing = res.json()["pairing"]
        print(f"  ✓ Patient paired with hospital: {hospitals[0]['name']} (MRN: {hosp_pairing['mrn']})")

        # Hospital Lab delivers official report directly to patient's vault
        res = await client.post(f"/api/hospitals/{hosp_id}/reports/deliver", json={
            "patient_name": "Sarah Connor",
            "sample_type": "lipid",
            "clinical_notes": "Official lipid profile processed by hospital pathology laboratory"
        })
        assert res.status_code == 200
        deliv = res.json()
        print(f"  ✓ Hospital delivered report to vault: {deliv['message']}")

        # Hospital analytics
        res = await client.get(f"/api/hospitals/{hosp_id}/analytics")
        assert res.status_code == 200
        stats = res.json()
        print("  ✓ Hospital Analytics verified:", stats)

        print("\n" + "="*60)
        print("🎉 ALL THREE LAYERS VERIFIED AND WORKING 100% SUCCESSFULLY!")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(run_tests())
