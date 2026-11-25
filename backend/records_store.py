import json
import os
import uuid
import io
import qrcode
from datetime import datetime
from typing import Dict, Any, List, Optional

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "db.json")

DEFAULT_HOSPITALS = [
    {
        "id": "hosp_1",
        "name": "MediSync Metro Health City",
        "address": "100 Healthcare Boulevard, Metro District",
        "phone": "+1 (800) 555-0100",
        "email": "records@metrohealthcity.org",
        "departments": [
            "Comprehensive Diagnostics & Laboratory",
            "Cardiovascular Institute",
            "Endocrine & Metabolic Clinic",
            "Pulmonary & Respiratory Care",
            "Internal Medicine & Acute Care"
        ],
        "doctor_ids": ["doc_1", "doc_2", "doc_3", "doc_4"],
        "rating": 4.9,
        "is_verified": True
    },
    {
        "id": "hosp_2",
        "name": "Apex University Medical Center",
        "address": "450 Academic Way, University Hills",
        "phone": "+1 (888) 555-0250",
        "email": "clinical@apexmed.edu",
        "departments": [
            "Advanced Clinical Pathology",
            "Cardiology Sciences",
            "Family & Preventive Medicine"
        ],
        "doctor_ids": ["doc_1", "doc_3"],
        "rating": 4.8,
        "is_verified": True
    }
]

DEFAULT_DOCTORS = [
    {
        "id": "doc_1",
        "name": "Dr. Sarah Jenkins",
        "specialty": "Cardiology",
        "qualification": "MD, FACC",
        "hospital": "MediSync Metro Health City",
        "hospital_id": "hosp_1",
        "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
        "available_time": "09:00 AM - 04:00 PM",
        "avatar": "👩‍⚕️",
        "email": "sjenkins@metrohealthcity.org"
    },
    {
        "id": "doc_2",
        "name": "Dr. Rajiv Mehta",
        "specialty": "Endocrinology & Diabetology",
        "qualification": "MD, DM (Endo)",
        "hospital": "MediSync Metro Health City",
        "hospital_id": "hosp_1",
        "available_days": ["Mon", "Wed", "Fri", "Sat"],
        "available_time": "10:00 AM - 05:00 PM",
        "avatar": "👨‍⚕️",
        "email": "rmehta@metrohealthcity.org"
    },
    {
        "id": "doc_3",
        "name": "Dr. Elena Rostova",
        "specialty": "General Internal Medicine",
        "qualification": "MBBS, MD",
        "hospital": "MediSync Metro Health City",
        "hospital_id": "hosp_1",
        "available_days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        "available_time": "08:30 AM - 03:30 PM",
        "avatar": "👩‍⚕️",
        "email": "erostova@metrohealthcity.org"
    },
    {
        "id": "doc_4",
        "name": "Dr. Marcus Chen",
        "specialty": "Pulmonology & Respiratory Care",
        "qualification": "MD, FCCP",
        "hospital": "MediSync Metro Health City",
        "hospital_id": "hosp_1",
        "available_days": ["Tue", "Thu", "Sat"],
        "available_time": "11:00 AM - 06:00 PM",
        "avatar": "👨‍⚕️",
        "email": "mchen@metrohealthcity.org"
    }
]

DEFAULT_USERS = [
    {
        "uid": "usr_patient_1",
        "email": "patient@medisync.health",
        "password": "patient123",
        "name": "Sarah Connor",
        "role": "patient",
        "phone": "+1 (555) 019-2834",
        "mrn": "MRN-78219"
    },
    {
        "uid": "usr_doctor_1",
        "email": "doctor@medisync.health",
        "password": "doctor123",
        "name": "Dr. Sarah Jenkins",
        "role": "doctor",
        "doctor_id": "doc_1",
        "phone": "+1 (555) 014-9981"
    },
    {
        "uid": "usr_admin_1",
        "email": "admin@hospital.health",
        "password": "admin123",
        "name": "Metro Health Administrator",
        "role": "hospital_admin",
        "hospital_id": "hosp_1",
        "phone": "+1 (800) 555-0100"
    }
]

class RecordsStore:
    def __init__(self):
        self._ensure_db()

    def _ensure_db(self):
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
        if not os.path.exists(DATA_FILE):
            initial_data = {
                "users": DEFAULT_USERS,
                "hospitals": DEFAULT_HOSPITALS,
                "doctors": DEFAULT_DOCTORS,
                "reports": {},
                "appointments": [],
                "pairings": [
                    {
                        "id": "pair_init_1",
                        "patient_name": "Sarah Connor",
                        "doctor_id": "doc_1",
                        "doctor_name": "Dr. Sarah Jenkins",
                        "specialty": "Cardiology",
                        "status": "Active",
                        "created_at": datetime.now().isoformat()
                    }
                ],
                "hospital_pairings": [
                    {
                        "id": "hosp_pair_1",
                        "patient_name": "Sarah Connor",
                        "hospital_id": "hosp_1",
                        "hospital_name": "MediSync Metro Health City",
                        "mrn": "MRN-78219",
                        "status": "Active",
                        "created_at": datetime.now().isoformat()
                    }
                ]
            }
            self._save(initial_data)

    def _load(self) -> Dict[str, Any]:
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "users" not in data:
                    data["users"] = DEFAULT_USERS
                if "hospitals" not in data:
                    data["hospitals"] = DEFAULT_HOSPITALS
                if "pairings" not in data:
                    data["pairings"] = []
                if "hospital_pairings" not in data:
                    data["hospital_pairings"] = []
                return data
        except Exception:
            return {
                "users": DEFAULT_USERS,
                "hospitals": DEFAULT_HOSPITALS,
                "doctors": DEFAULT_DOCTORS,
                "reports": {},
                "appointments": [],
                "pairings": [],
                "hospital_pairings": []
            }

    def _save(self, data: Dict[str, Any]):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ------------------ Auth & User Operations ------------------

    def authenticate_user(self, email: str, password: str, role: Optional[str] = None) -> Optional[Dict[str, Any]]:
        data = self._load()
        users = data.get("users", DEFAULT_USERS)
        for u in users:
            if u.get("email", "").lower() == email.strip().lower() and u.get("password") == password.strip():
                if role and u.get("role") != role:
                    continue
                safe_user = dict(u)
                safe_user.pop("password", None)
                return safe_user
        return None

    def register_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        data = self._load()
        users = data.get("users", [])
        email = user_data.get("email", "").strip().lower()
        for u in users:
            if u.get("email", "").lower() == email:
                raise ValueError("User with this email already exists")

        user_data["uid"] = f"usr_{uuid.uuid4().hex[:8]}"
        user_data["created_at"] = datetime.now().isoformat()
        if user_data.get("role") == "patient" and not user_data.get("mrn"):
            user_data["mrn"] = f"MRN-{uuid.uuid4().hex[:5].upper()}"

        users.append(user_data)
        data["users"] = users
        self._save(data)

        safe = dict(user_data)
        safe.pop("password", None)
        return safe

    # ------------------ Hospital Operations ------------------

    def get_hospitals(self) -> List[Dict[str, Any]]:
        data = self._load()
        return data.get("hospitals", DEFAULT_HOSPITALS)

    def get_hospital_by_id(self, hosp_id: str) -> Optional[Dict[str, Any]]:
        for h in self.get_hospitals():
            if h["id"] == hosp_id:
                return h
        return None

    def pair_patient_with_hospital(self, patient_name: str, hospital_id: str) -> Dict[str, Any]:
        data = self._load()
        hosp = self.get_hospital_by_id(hospital_id)
        if not hosp:
            raise ValueError("Hospital not found")

        # Check existing
        for hp in data.get("hospital_pairings", []):
            if hp.get("patient_name", "").lower() == patient_name.lower() and hp.get("hospital_id") == hospital_id:
                return hp

        pairing = {
            "id": f"hp_{uuid.uuid4().hex[:8]}",
            "patient_name": patient_name,
            "hospital_id": hospital_id,
            "hospital_name": hosp["name"],
            "mrn": f"MRN-{uuid.uuid4().hex[:5].upper()}",
            "status": "Active",
            "created_at": datetime.now().isoformat()
        }
        data.setdefault("hospital_pairings", []).append(pairing)
        self._save(data)
        return pairing

    def list_hospital_pairings(self, patient_name: Optional[str] = None) -> List[Dict[str, Any]]:
        data = self._load()
        hps = data.get("hospital_pairings", [])
        if patient_name:
            hps = [p for p in hps if patient_name.lower() in p.get("patient_name", "").lower()]
        return hps

    def get_hospital_analytics(self, hospital_id: str) -> Dict[str, Any]:
        data = self._load()
        hosp = self.get_hospital_by_id(hospital_id)
        appts = [a for a in data.get("appointments", []) if a.get("hospital") == (hosp["name"] if hosp else "")]
        paired_count = len([p for p in data.get("hospital_pairings", []) if p.get("hospital_id") == hospital_id])

        dept_counts = {}
        for a in appts:
            spec = a.get("doctor_specialty", "General")
            dept_counts[spec] = dept_counts.get(spec, 0) + 1

        return {
            "hospital_id": hospital_id,
            "hospital_name": hosp["name"] if hosp else "Hospital",
            "total_paired_patients": paired_count,
            "total_appointments": len(appts),
            "departmental_breakdown": dept_counts,
            "available_doctors": len(hosp.get("doctor_ids", [])) if hosp else 0,
            "active_telehealth_sessions": len([a for a in appts if a.get("status") == "In Consultation"])
        }

    # ------------------ Doctor Operations ------------------

    def get_doctors(self) -> List[Dict[str, Any]]:
        data = self._load()
        return data.get("doctors", DEFAULT_DOCTORS)

    def get_doctor_by_id(self, doc_id: str) -> Optional[Dict[str, Any]]:
        for d in self.get_doctors():
            if d["id"] == doc_id:
                return d
        return None

    def update_doctor_schedule(self, doc_id: str, available_days: List[str], available_time: Optional[str] = None, off_dates: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        data = self._load()
        doctors = data.get("doctors", DEFAULT_DOCTORS)
        for d in doctors:
            if d["id"] == doc_id:
                d["available_days"] = available_days
                if available_time:
                    d["available_time"] = available_time
                if off_dates is not None:
                    d["off_dates"] = off_dates
                data["doctors"] = doctors
                self._save(data)
                return d
        return None

    # ------------------ Pairing Operations (Layer 2) ------------------

    def create_pairing(self, patient_name: str, doctor_id: str, notes: Optional[str] = None) -> Dict[str, Any]:
        data = self._load()
        doc = self.get_doctor_by_id(doctor_id)
        if not doc:
            raise ValueError("Doctor not found")

        # Check existing
        for p in data.get("pairings", []):
            if p.get("patient_name", "").lower() == patient_name.lower() and p.get("doctor_id") == doctor_id:
                return p

        pairing = {
            "id": f"pair_{uuid.uuid4().hex[:8]}",
            "patient_name": patient_name,
            "doctor_id": doctor_id,
            "doctor_name": doc["name"],
            "specialty": doc["specialty"],
            "hospital": doc.get("hospital", "MediSync Health"),
            "status": "Active",
            "notes": notes or "Patient initiated primary care pairing",
            "created_at": datetime.now().isoformat()
        }
        data.setdefault("pairings", []).append(pairing)
        self._save(data)
        return pairing

    def list_pairings(self, doctor_id: Optional[str] = None, patient_name: Optional[str] = None) -> List[Dict[str, Any]]:
        data = self._load()
        pairs = data.get("pairings", [])
        if doctor_id:
            pairs = [p for p in pairs if p.get("doctor_id") == doctor_id]
        if patient_name:
            pairs = [p for p in pairs if patient_name.lower() in p.get("patient_name", "").lower()]
        return pairs

    # ------------------ Medical Reports Vault (Layer 1 & 3) ------------------

    def save_report(self, report_data: Dict[str, Any]) -> str:
        data = self._load()
        report_id = report_data.get("id") or f"rep_{uuid.uuid4().hex[:8]}"
        report_data["id"] = report_id
        report_data["token"] = report_data.get("token") or f"TK-{uuid.uuid4().hex[:6].upper()}"
        report_data["created_at"] = report_data.get("created_at") or datetime.now().isoformat()
        report_data["report_type"] = report_data.get("report_type") or "Laboratory Pathology"
        report_data["source"] = report_data.get("source") or "Uploaded by Patient"
        
        data["reports"][report_id] = report_data
        self._save(data)
        return report_id

    def get_report(self, report_id: str) -> Optional[Dict[str, Any]]:
        data = self._load()
        return data.get("reports", {}).get(report_id)

    def get_report_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        data = self._load()
        token_upper = token.strip().upper()
        for r_id, r in data.get("reports", {}).items():
            if r.get("token", "").upper() == token_upper or r_id == token:
                return r
        return None

    def list_reports(self, patient_name: Optional[str] = None, report_type: Optional[str] = None) -> List[Dict[str, Any]]:
        data = self._load()
        reports = list(data.get("reports", {}).values())
        if patient_name:
            reports = [r for r in reports if patient_name.lower() in r.get("patient_name", "").lower()]
        if report_type:
            reports = [r for r in reports if report_type.lower() in r.get("report_type", "").lower()]
        reports.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return reports

    def delete_report(self, report_id: str) -> bool:
        data = self._load()
        if report_id in data.get("reports", {}):
            del data["reports"][report_id]
            self._save(data)
            return True
        return False

    def add_doctor_notes(self, report_id: str, doctor_name: str, notes: str, prescription: Optional[str] = None) -> bool:
        data = self._load()
        if report_id in data.get("reports", {}):
            report = data["reports"][report_id]
            doctor_entries = report.get("doctor_notes", [])
            doctor_entries.append({
                "id": str(uuid.uuid4()),
                "doctor_name": doctor_name,
                "notes": notes,
                "prescription": prescription or "",
                "created_at": datetime.now().isoformat()
            })
            report["doctor_notes"] = doctor_entries
            self._save(data)
            return True
        return False

    # ------------------ Appointments ------------------

    def book_appointment(self, appointment_data: Dict[str, Any]) -> Dict[str, Any]:
        data = self._load()
        appt_id = f"apt_{uuid.uuid4().hex[:8]}"
        appointment_data["id"] = appt_id
        appointment_data["created_at"] = datetime.now().isoformat()
        appointment_data["status"] = appointment_data.get("status", "Confirmed")
        
        data.setdefault("appointments", []).append(appointment_data)
        self._save(data)
        return appointment_data

    def list_appointments(self, doctor_id: Optional[str] = None, patient_name: Optional[str] = None, hospital_id: Optional[str] = None) -> List[Dict[str, Any]]:
        data = self._load()
        appts = data.get("appointments", [])
        if doctor_id:
            appts = [a for a in appts if a.get("doctor_id") == doctor_id]
        if patient_name:
            appts = [a for a in appts if patient_name.lower() in a.get("patient_name", "").lower()]
        if hospital_id:
            hosp = self.get_hospital_by_id(hospital_id)
            if hosp:
                appts = [a for a in appts if a.get("hospital") == hosp["name"]]
        appts.sort(key=lambda x: (x.get("date", ""), x.get("time", "")))
        return appts

    def update_appointment_status(self, appt_id: str, new_status: str) -> bool:
        data = self._load()
        for a in data.get("appointments", []):
            if a.get("id") == appt_id:
                a["status"] = new_status
                self._save(data)
                return True
        return False

    def generate_qr_code(self, token: str, base_url: str = "http://127.0.0.1:8000") -> bytes:
        qr_url = f"{base_url}/?portal=doctor&token={token}"
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=3,
        )
        qr.add_data(qr_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#0D9488", back_color="#FFFFFF")
        
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer.getvalue()

records_store = RecordsStore()
