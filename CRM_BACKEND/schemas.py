from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime, date
from decimal import Decimal

class SignupRequest(BaseModel):
    name: str
    email: str
    role: str
    phone: str
    password: str
    employee_id: Optional[str] = None

class LoginRequest(BaseModel):
    employee_id: str
    password: str

class LocationUpdate(BaseModel):
    lat: float
    lon: float
    checkout_note: Optional[str] = None

class PinLocationRequest(BaseModel):
    lat: float
    lon: float
    note: str


class LeadCreate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: str
    company_name: str
    status: Optional[str] = "pending"
    note: Optional[str] = None
    source: Optional[str] = "Manual"
    location: Optional[str] = None
    assigned_to: Optional[str] = None
    priority: Optional[str] = "Medium"
    product_type: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    gsm: Optional[str] = None
    quantity: Optional[int] = None
    handles: Optional[str] = None
    print_color: Optional[str] = None
    bag_type: Optional[str] = None
    followup_date: Optional[date] = None
    lead_value: Optional[Decimal] = None

class LeadUpdate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: str
    company_name: str
    status: str
    note: Optional[str] = None
    source: Optional[str] = "Manual"
    location: Optional[str] = None
    assigned_to: Optional[str] = None
    priority: Optional[str] = "Medium"
    product_type: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    gsm: Optional[str] = None
    quantity: Optional[int] = None
    handles: Optional[str] = None
    print_color: Optional[str] = None
    bag_type: Optional[str] = None
    followup_date: Optional[date] = None
    lead_value: Optional[Decimal] = None

class DealCreate(BaseModel):
    deal_name: str
    company_name: str
    contact_name: str
    phone: Optional[str] = ""
    email: Optional[str] = ""
    deal_value: Decimal = 0
    source: Optional[str] = ""
    note: Optional[str] = ""
    assigned_to: Optional[str] = None
    product_type: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    gsm: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None
    advance_received: Optional[Decimal] = None
    balance_amount: Optional[Decimal] = None
    expected_delivery_date: Optional[date] = None
    handles: Optional[str] = None
    print_color: Optional[str] = None
    bag_type: Optional[str] = None

class DealUpdate(BaseModel):
    deal_name: Optional[str] = None
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    phone: Optional[str] = ""
    email: Optional[str] = ""
    deal_value: Decimal = 0
    source: Optional[str] = ""
    note: Optional[str] = ""
    assigned_to: Optional[str] = None
    product_type: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    gsm: Optional[str] = None
    quantity: Optional[int] = None
    unit_price: Optional[Decimal] = None
    advance_received: Optional[Decimal] = None
    balance_amount: Optional[Decimal] = None
    expected_delivery_date: Optional[date] = None
    handles: Optional[str] = None
    print_color: Optional[str] = None
    bag_type: Optional[str] = None

class LeadConvertRequest(BaseModel):
    product_type: Optional[str] = None
    size: Optional[str] = None
    color: Optional[str] = None
    gsm: Optional[str] = None
    quantity: int
    unit_price: Decimal
    lead_value: Optional[Decimal] = None
    order_value: Optional[Decimal] = None
    handles: Optional[str] = None
    print_color: Optional[str] = None
    bag_type: Optional[str] = None

class InventoryItemCreate(BaseModel):
    item_name: str
    category: str
    unit: Optional[str] = None
    current_stock: Decimal = 0
    minimum_stock: Decimal = 0

class InventoryItemUpdate(BaseModel):
    item_name: str
    category: str
    unit: Optional[str] = None
    current_stock: Decimal
    minimum_stock: Decimal

class PurchaseRequestCreate(BaseModel):
    item_name: str
    quantity: Decimal
    vendor_name: Optional[str] = None

class ProductionUpdate(BaseModel):
    status: str
    expected_completion_date: Optional[date] = None
    remarks: Optional[str] = None

class InvoiceCreate(BaseModel):
    order_id: int
    invoice_number: str
    subtotal: Decimal
    gst: Optional[Decimal] = 0
    transport_charge: Optional[Decimal] = 0
    stereo_charge: Optional[Decimal] = 0
    total_amount: Decimal
    payment_status: Optional[str] = "PENDING"

class InvoicePaymentUpdate(BaseModel):
    payment_status: str

class CustomerCreate(BaseModel):
    company_name: Optional[str] = None
    contact_person: str
    phone: str
    alternate_phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    gst_number: Optional[str] = None
    notes: Optional[str] = None

class IndentCreate(BaseModel):
    item_name: str
    size: str
    quantity: Decimal

class ReminderCreate(BaseModel):
    title: str
    description: Optional[str] = None
    remind_at: datetime

class UserUpdate(BaseModel):
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str
    salary: Optional[float] = None
    department: Optional[str] = None
    designation: Optional[str] = None
    joining_date: Optional[str] = None
    is_active: Optional[bool] = None
