"""
Build Internal Products — Workshop API
A tiny taco-delivery API used as the hands-on sandbox.

Swagger playground is auto-generated at  /docs
"""

from fastapi import FastAPI, HTTPException, Security, status
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, Field
from typing import Optional, Literal
from copy import deepcopy

# ----------------------------------------------------------------------------
# CONFIG
# ----------------------------------------------------------------------------

API_KEY = "extra-guac"                  # <- the key you put on the slide
PROTECTED_ID_LIMIT = 100                # seeded orders (id <= 100) can't be changed/deleted
NEXT_NEW_ID = 1000                      # orders created by attendees start here

app = FastAPI(
    title="Build Internal Products — Taco Delivery API",
    description=(
        "A small, friendly API to practise on. It delivers tacos.\n\n"
        "**How to use this page**\n\n"
        "1. Click the green **Authorize** button, top right.\n"
        "2. Paste the API key you were given, and click Authorize.\n"
        "3. Pick an endpoint below, click **Try it out**, then **Execute**.\n\n"
        "Everything you create here disappears when the API restarts. "
        "Break whatever you like."
    ),
    version="1.0.0",
)

# ----------------------------------------------------------------------------
# AUTH  — a single key, sent on EVERY request (rule 3: the API has no memory)
# ----------------------------------------------------------------------------

api_key_header = APIKeyHeader(
    name="X-API-Key",
    description="Your workshop API key.",
    auto_error=False,
)


def check_key(key: Optional[str] = Security(api_key_header)) -> str:
    if key is None:
        raise HTTPException(
            status_code=401,
            detail="No API key. Click Authorize at the top of this page and paste your key.",
        )
    if key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="That API key isn't right. Check for stray spaces.",
        )
    return key


# ----------------------------------------------------------------------------
# MODELS
# ----------------------------------------------------------------------------

Status = Literal["preparing", "on_the_way", "delivered", "cancelled"]
City = Literal["frankfurt", "berlin", "munich"]


class Order(BaseModel):
    id: int
    customer: str
    restaurant: str
    city: City
    items: list[str]
    total_eur: float
    status: Status
    driver_id: Optional[int] = None


class NewOrder(BaseModel):
    customer: str = Field(..., examples=["Masha"])
    restaurant: str = Field(..., examples=["Taqueria Sol"])
    city: City = Field(..., examples=["frankfurt"])
    items: list[str] = Field(..., examples=[["Al pastor x3", "Extra guac"]])
    total_eur: float = Field(..., examples=[18.50])


class StatusUpdate(BaseModel):
    status: Status = Field(..., examples=["on_the_way"])


class Driver(BaseModel):
    id: int
    name: str
    city: City
    vehicle: str
    lat: float
    lng: float


class Restaurant(BaseModel):
    id: int
    name: str
    city: City
    cuisine: str
    open_now: bool


# ----------------------------------------------------------------------------
# SEED DATA  — the bedrock. Predictable, so the exercises always work.
# ----------------------------------------------------------------------------

SEED_ORDERS: list[dict] = [
    # --- FRANKFURT (8) ---
    {"id": 1,  "customer": "Anna",    "restaurant": "Taqueria Sol",   "city": "frankfurt", "items": ["Al pastor x3", "Horchata"],          "total_eur": 14.50, "status": "delivered",  "driver_id": 87},
    {"id": 2,  "customer": "Ben",     "restaurant": "El Pastor",      "city": "frankfurt", "items": ["Carnitas x4"],                  "total_eur": 22.00, "status": "delivered",  "driver_id": 87},
    {"id": 3,  "customer": "Clara",   "restaurant": "Casa Guac",     "city": "frankfurt", "items": ["Barbacoa x3", "Elote"],      "total_eur": 19.90, "status": "on_the_way", "driver_id": 88},
    {"id": 4,  "customer": "Dmitri",  "restaurant": "Taqueria Sol",   "city": "frankfurt", "items": ["Birria x4"],            "total_eur": 16.00, "status": "on_the_way", "driver_id": 87},
    {"id": 5,  "customer": "Elena",   "restaurant": "Verde Taqueria",     "city": "frankfurt", "items": ["Jackfruit tacos x3"],                "total_eur": 11.50, "status": "preparing",  "driver_id": None},
    {"id": 6,  "customer": "Farid",   "restaurant": "El Pastor",      "city": "frankfurt", "items": ["Pescado x4", "Guacamole"],    "total_eur": 27.40, "status": "delivered",  "driver_id": 88},
    {"id": 7,  "customer": "Greta",   "restaurant": "Casa Guac",     "city": "frankfurt", "items": ["Nopales x3"],             "total_eur": 15.00, "status": "cancelled",  "driver_id": None},
    {"id": 8,  "customer": "Hugo",    "restaurant": "Verde Taqueria",     "city": "frankfurt", "items": ["Cauliflower tacos x3", "Agua fresca"],         "total_eur": 18.20, "status": "delivered",  "driver_id": 87},

    # --- BERLIN (7) ---
    {"id": 9,  "customer": "Ines",    "restaurant": "Taco Palace",   "city": "berlin",    "items": ["Suadero x2", "Jarritos"],              "total_eur": 9.50,  "status": "delivered",  "driver_id": 91},
    {"id": 10, "customer": "Jonas",   "restaurant": "La Frontera",     "city": "berlin",    "items": ["Lengua x3"],                      "total_eur": 13.00, "status": "on_the_way", "driver_id": 91},
    {"id": 11, "customer": "Kata",    "restaurant": "Burrito Bros",    "city": "berlin",    "items": ["Crunchy beef x4", "Nachos"],       "total_eur": 16.80, "status": "preparing",  "driver_id": None},
    {"id": 12, "customer": "Lukas",   "restaurant": "Taco Palace",   "city": "berlin",    "items": ["Queso taco x2"],               "total_eur": 8.90,  "status": "delivered",  "driver_id": 92},
    {"id": 13, "customer": "Mira",    "restaurant": "La Frontera",     "city": "berlin",    "items": ["Chorizo x3", "Churros"],     "total_eur": 21.30, "status": "on_the_way", "driver_id": 92},
    {"id": 14, "customer": "Noah",    "restaurant": "Burrito Bros",    "city": "berlin",    "items": ["Brisket taco x4"],                "total_eur": 19.00, "status": "preparing",  "driver_id": None},
    {"id": 15, "customer": "Olga",    "restaurant": "Burrito Bros",    "city": "berlin",    "items": ["Black bean taco x3"],               "total_eur": 14.00, "status": "cancelled",  "driver_id": None},

    # --- MUNICH (5) ---
    {"id": 16, "customer": "Pia",     "restaurant": "Bavaria Tacos",     "city": "munich",    "items": ["Pretzel taco x2", "Michelada"],        "total_eur": 12.00, "status": "delivered",  "driver_id": 95},
    {"id": 17, "customer": "Quinn",   "restaurant": "Taco Loco",      "city": "munich",    "items": ["Al pastor x5"],             "total_eur": 17.50, "status": "on_the_way", "driver_id": 95},
    {"id": 18, "customer": "Rosa",    "restaurant": "Bavaria Tacos",     "city": "munich",    "items": ["Cheese taco x3", "Salsa verde"],          "total_eur": 13.60, "status": "delivered",  "driver_id": 96},
    {"id": 19, "customer": "Samir",   "restaurant": "Taco Loco",      "city": "munich",    "items": ["Burrito", "Extra guac"],        "total_eur": 20.10, "status": "preparing",  "driver_id": None},
    {"id": 20, "customer": "Tessa",   "restaurant": "Nacho House",   "city": "munich",    "items": ["Nacho platter"],                    "total_eur": 15.40, "status": "delivered",  "driver_id": 96},
]

SEED_DRIVERS: list[dict] = [
    {"id": 87, "name": "Marco",  "city": "frankfurt", "vehicle": "scooter", "lat": 50.1109, "lng": 8.6821},
    {"id": 88, "name": "Sofia",  "city": "frankfurt", "vehicle": "bicycle", "lat": 50.1155, "lng": 8.6842},
    {"id": 91, "name": "Tomas",  "city": "berlin",    "vehicle": "scooter", "lat": 52.5200, "lng": 13.4050},
    {"id": 92, "name": "Yara",   "city": "berlin",    "vehicle": "car",     "lat": 52.5163, "lng": 13.3777},
    {"id": 95, "name": "Leon",   "city": "munich",    "vehicle": "bicycle", "lat": 48.1372, "lng": 11.5755},
    {"id": 96, "name": "Nadia",  "city": "munich",    "vehicle": "scooter", "lat": 48.1391, "lng": 11.5802},
]

SEED_RESTAURANTS: list[dict] = [
    {"id": 1, "name": "Taqueria Sol",  "city": "frankfurt", "cuisine": "mexican",   "open_now": True},
    {"id": 2, "name": "El Pastor",     "city": "frankfurt", "cuisine": "mexican",  "open_now": True},
    {"id": 3, "name": "Casa Guac",    "city": "frankfurt", "cuisine": "mexican",    "open_now": False},
    {"id": 4, "name": "Verde Taqueria",    "city": "frankfurt", "cuisine": "vegan",   "open_now": True},
    {"id": 5, "name": "Taco Palace",  "city": "berlin",    "cuisine": "mexican",   "open_now": True},
    {"id": 6, "name": "La Frontera",    "city": "berlin",    "cuisine": "mexican","open_now": True},
    {"id": 7, "name": "Burrito Bros",   "city": "berlin",    "cuisine": "tex-mex",  "open_now": False},
    {"id": 8, "name": "Bavaria Tacos",    "city": "munich",    "cuisine": "tex-mex",    "open_now": True},
    {"id": 9, "name": "Taco Loco",     "city": "munich",    "cuisine": "mexican",   "open_now": True},
    {"id": 10,"name": "Nacho House",  "city": "munich",    "cuisine": "tex-mex",      "open_now": True},
]

# live, mutable state
orders: dict[int, dict] = {}
next_id: int = NEXT_NEW_ID


def load_seed() -> None:
    global orders, next_id
    orders = {o["id"]: deepcopy(o) for o in SEED_ORDERS}
    next_id = NEXT_NEW_ID


load_seed()


# ----------------------------------------------------------------------------
# ORDERS
# ----------------------------------------------------------------------------

@app.get("/orders", response_model=list[Order], tags=["Orders"],
         summary="Get all orders")
def list_orders(
    status: Optional[Status] = None,
    city: Optional[City] = None,
    _key: str = Security(check_key),
):
    """
    Returns every order.

    Add **parameters** to narrow it down — try `status=delivered`,
    or `city=frankfurt`, or both together.
    """
    result = list(orders.values())
    if status:
        result = [o for o in result if o["status"] == status]
    if city:
        result = [o for o in result if o["city"] == city]
    return sorted(result, key=lambda o: o["id"])


@app.get("/orders/{order_id}", response_model=Order, tags=["Orders"],
         summary="Get one order")
def get_order(order_id: int, _key: str = Security(check_key)):
    """Give me *this* order. Try `3`. Then try `999` and see what happens."""
    if order_id not in orders:
        raise HTTPException(status_code=404, detail=f"No order with id {order_id}.")
    return orders[order_id]


@app.post("/orders", response_model=Order, status_code=201, tags=["Orders"],
          summary="Place a new order")
def create_order(new: NewOrder, _key: str = Security(check_key)):
    """
    Creates an order. Note the response code: **201 Created**, not 200.

    Your new order gets an id from 1000 upwards — it's yours, do what you like with it.
    """
    global next_id
    order = {
        "id": next_id,
        **new.model_dump(),
        "status": "preparing",
        "driver_id": None,
    }
    orders[next_id] = order
    next_id += 1
    return order


@app.patch("/orders/{order_id}", response_model=Order, tags=["Orders"],
           summary="Update an order's status")
def update_status(order_id: int, update: StatusUpdate, _key: str = Security(check_key)):
    """
    Move an order along: `preparing` -> `on_the_way` -> `delivered`.

    The 20 seeded orders are read-only — try changing one and see what the API says.
    """
    if order_id not in orders:
        raise HTTPException(status_code=404, detail=f"No order with id {order_id}.")
    if order_id <= PROTECTED_ID_LIMIT:
        raise HTTPException(
            status_code=403,
            detail="This is a seeded order and can't be changed — everyone in the workshop shares it. Create your own with POST /orders and edit that instead.",
        )
    orders[order_id]["status"] = update.status
    return orders[order_id]


@app.delete("/orders/{order_id}", status_code=204, tags=["Orders"],
            summary="Cancel an order")
def delete_order(order_id: int, _key: str = Security(check_key)):
    """
    Deletes an order. Note the response: **204 No Content** — it worked,
    and there is nothing to give back.
    """
    if order_id not in orders:
        raise HTTPException(status_code=404, detail=f"No order with id {order_id}.")
    if order_id <= PROTECTED_ID_LIMIT:
        raise HTTPException(
            status_code=403,
            detail="This is a seeded order and can't be deleted — everyone in the workshop shares it. Create your own with POST /orders and delete that instead.",
        )
    del orders[order_id]
    return None


# ----------------------------------------------------------------------------
# DRIVERS  &  RESTAURANTS
# ----------------------------------------------------------------------------

@app.get("/drivers/{driver_id}", response_model=Driver, tags=["Drivers"],
         summary="Where is the driver?")
def get_driver(driver_id: int, _key: str = Security(check_key)):
    """This is the dot on the map. Try driver `87` — he's the one on the scooter with your tacos."""
    for d in SEED_DRIVERS:
        if d["id"] == driver_id:
            return d
    raise HTTPException(status_code=404, detail=f"No driver with id {driver_id}.")


@app.get("/restaurants", response_model=list[Restaurant], tags=["Restaurants"],
         summary="Get all restaurants")
def list_restaurants(
    city: Optional[City] = None,
    open_now: Optional[bool] = None,
    _key: str = Security(check_key),
):
    """Try `city=berlin`, or `open_now=true`, or both."""
    result = SEED_RESTAURANTS
    if city:
        result = [r for r in result if r["city"] == city]
    if open_now is not None:
        result = [r for r in result if r["open_now"] == open_now]
    return result


# ----------------------------------------------------------------------------
# RESET  — your panic button
# ----------------------------------------------------------------------------

@app.post("/reset", tags=["Workshop"], summary="Reset everything back to the seed data")
def reset(_key: str = Security(check_key)):
    """Wipes anything created during the session and restores the original 20 orders."""
    load_seed()
    return {"message": "Reset done.", "orders": len(orders)}
